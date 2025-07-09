"""
Flask routes for the HPM Inventory application.
"""
from flask import render_template, request, redirect, url_for, flash, session, make_response
from datetime import datetime
import csv
import io
from app import app
from models import InventoryItem, WasteEntry
from utils import (
    read_inventory, write_inventory, get_inventory_item, 
    update_inventory_item, delete_inventory_item,
    authenticate_user, get_user, read_waste_log, add_waste_entry,
    get_low_stock_items, export_inventory_csv, import_inventory_csv
)

def require_login(f):
    """Decorator to require login for routes"""
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_permission(permission):
    """Decorator to require specific permission for routes"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            user = get_user(session['username'])
            if not user or not user.has_permission(permission):
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('inventory'))
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@app.route('/')
def index():
    """Redirect to inventory page"""
    return redirect(url_for('inventory'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = authenticate_user(username, password)
        if user:
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('inventory'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/inventory')
@require_login
def inventory():
    """Main inventory page"""
    items = read_inventory()
    low_stock_items = get_low_stock_items()
    user = get_user(session['username'])
    
    return render_template('inventory.html', 
                         items=items, 
                         low_stock_count=len(low_stock_items),
                         user=user)

@app.route('/add_item', methods=['GET', 'POST'])
@require_permission('edit')
def add_item():
    """Add new inventory item"""
    if request.method == 'POST':
        name = request.form['name'].strip()
        unit = request.form['unit'].strip()
        quantity = int(request.form['quantity'])
        par_level = int(request.form['par_level'])
        category = request.form.get('category', 'General').strip()
        
        # Check if item already exists
        if get_inventory_item(name):
            flash(f'Item "{name}" already exists.', 'danger')
            return render_template('add_item.html')
        
        # Create new item
        new_item = InventoryItem(
            name=name,
            unit=unit,
            quantity=quantity,
            par_level=par_level,
            category=category,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Add to inventory
        items = read_inventory()
        items.append(new_item)
        write_inventory(items)
        
        flash(f'Item "{name}" added successfully.', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('add_item.html')

@app.route('/edit_item/<item_name>', methods=['GET', 'POST'])
@require_permission('edit')
def edit_item(item_name):
    """Edit existing inventory item"""
    item = get_inventory_item(item_name)
    if not item:
        flash(f'Item "{item_name}" not found.', 'danger')
        return redirect(url_for('inventory'))
    
    if request.method == 'POST':
        # Update item details
        item.unit = request.form['unit'].strip()
        item.quantity = int(request.form['quantity'])
        item.par_level = int(request.form['par_level'])
        item.category = request.form.get('category', 'General').strip()
        item.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save changes
        if update_inventory_item(item_name, item):
            flash(f'Item "{item_name}" updated successfully.', 'success')
            return redirect(url_for('inventory'))
        else:
            flash(f'Error updating item "{item_name}".', 'danger')
    
    return render_template('edit_item.html', item=item)

@app.route('/delete_item/<item_name>', methods=['POST'])
@require_permission('delete')
def delete_item(item_name):
    """Delete inventory item"""
    if delete_inventory_item(item_name):
        flash(f'Item "{item_name}" deleted successfully.', 'success')
    else:
        flash(f'Error deleting item "{item_name}".', 'danger')
    
    return redirect(url_for('inventory'))

@app.route('/update_count/<item_name>', methods=['POST'])
@require_permission('record_counts')
def update_count(item_name):
    """Update item count (for staff users)"""
    item = get_inventory_item(item_name)
    if not item:
        flash(f'Item "{item_name}" not found.', 'danger')
        return redirect(url_for('inventory'))
    
    new_count = int(request.form['count'])
    item.quantity = new_count
    item.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if update_inventory_item(item_name, item):
        flash(f'Count updated for "{item_name}".', 'success')
    else:
        flash(f'Error updating count for "{item_name}".', 'danger')
    
    return redirect(url_for('inventory'))

@app.route('/waste_log', methods=['GET', 'POST'])
@require_login
def waste_log():
    """Waste logging page"""
    if request.method == 'POST':
        item_name = request.form['item_name'].strip()
        quantity = int(request.form['quantity'])
        unit = request.form['unit'].strip()
        reason = request.form['reason'].strip()
        
        # Create waste entry
        entry = WasteEntry(
            item_name=item_name,
            quantity=quantity,
            unit=unit,
            reason=reason,
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            logged_by=session['username']
        )
        
        # Add to waste log
        add_waste_entry(entry)
        
        # Update inventory if item exists
        item = get_inventory_item(item_name)
        if item:
            item.quantity = max(0, item.quantity - quantity)
            item.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_inventory_item(item_name, item)
        
        flash(f'Waste logged for "{item_name}".', 'success')
        return redirect(url_for('waste_log'))
    
    # Get waste log entries and inventory items
    waste_entries = read_waste_log()
    inventory_items = read_inventory()
    user = get_user(session['username'])
    
    # Convert inventory items to dict format for JavaScript
    inventory_data = [item.to_dict() for item in inventory_items]
    
    return render_template('waste_log.html', 
                         waste_entries=waste_entries, 
                         inventory_items=inventory_items,
                         inventory_data=inventory_data,
                         user=user)

@app.route('/import_export', methods=['GET', 'POST'])
@require_permission('import')
def import_export():
    """Import/Export page"""
    if request.method == 'POST':
        if 'import_file' in request.files:
            file = request.files['import_file']
            if file.filename != '':
                try:
                    csv_data = file.read().decode('utf-8')
                    success, message = import_inventory_csv(csv_data)
                    if success:
                        flash(message, 'success')
                    else:
                        flash(f'Import failed: {message}', 'danger')
                except Exception as e:
                    flash(f'Error reading file: {str(e)}', 'danger')
        
        return redirect(url_for('import_export'))
    
    user = get_user(session['username'])
    return render_template('import_export.html', user=user)

@app.route('/export_csv')
@require_permission('export')
def export_csv():
    """Export inventory as CSV file"""
    csv_data = export_inventory_csv()
    
    # Create response with CSV data
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=hpm_inventory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('layout.html', error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template('layout.html', error_message="Internal server error"), 500
