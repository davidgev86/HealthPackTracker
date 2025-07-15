"""
Flask routes for the HPM Inventory application.
"""
from flask import render_template, request, redirect, url_for, flash, session, make_response
from datetime import datetime
import csv
import io
from app import app
from models import InventoryItem, WasteEntry, Vendor, Category, DEFAULT_CATEGORIES
from utils import (
    read_inventory, write_inventory, get_inventory_item, 
    update_inventory_item, delete_inventory_item,
    authenticate_user, get_user, read_waste_log, add_waste_entry, 
    write_waste_log, update_waste_entry, delete_waste_entry, get_waste_entry,
    get_low_stock_items, export_inventory_csv, import_inventory_csv,
    read_vendors, write_vendors, get_vendor, add_vendor, update_vendor, delete_vendor, is_vendor_in_use,
    filter_inventory, get_shopping_list_items,
    generate_shopping_list_pdf,
    read_categories, write_categories, get_category, add_category,
    update_category, delete_category, get_category_names, is_category_in_use,
    check_and_archive_if_needed, read_weekly_reports, get_week_comparison, 
    initialize_waste_archive
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
    """Main inventory page with filtering support"""
    # Get filter parameters
    category_filter = request.args.get('category')
    vendor_filter = request.args.get('vendor')
    low_stock_filter = request.args.get('low_stock') == 'true'
    
    # Apply filters
    items = filter_inventory(category=category_filter, vendor=vendor_filter, low_stock_only=low_stock_filter)
    all_items = read_inventory()  # For totals
    low_stock_items = get_low_stock_items()
    user = get_user(session['username'])
    
    # Calculate total inventory value
    total_value = sum(item.total_value() for item in all_items)
    
    # Get vendors and categories for filter dropdowns
    vendors = read_vendors()
    categories = get_category_names()
    
    return render_template('inventory.html', 
                         items=items, 
                         all_items=all_items,
                         low_stock_count=len(low_stock_items),
                         total_value=total_value,
                         vendors=vendors,
                         categories=categories,
                         current_category=category_filter,
                         current_vendor=vendor_filter,
                         low_stock_filter=low_stock_filter,
                         user=user)

@app.route('/add_item', methods=['GET', 'POST'])
@require_permission('edit')
def add_item():
    """Add new inventory item"""
    if request.method == 'POST':
        name = request.form['name'].strip()
        unit = request.form['unit'].strip()
        quantity = float(request.form['quantity'])
        par_level = int(request.form['par_level'])
        category = request.form.get('category', 'General').strip()
        unit_cost = float(request.form.get('unit_cost', 0.0))
        vendors = request.form.get('vendors', '').strip()
        
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
            unit_cost=unit_cost,
            vendors=vendors,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Add to inventory
        items = read_inventory()
        items.append(new_item)
        write_inventory(items)
        
        flash(f'Item "{name}" added successfully.', 'success')
        return redirect(url_for('inventory'))
    
    # Get vendors and categories for form dropdowns
    vendors = read_vendors()
    categories = get_category_names()
    
    return render_template('add_item.html', vendors=vendors, categories=categories)

@app.route('/edit_item/<item_name>', methods=['GET', 'POST'])
@require_permission('edit')
def edit_item(item_name):
    """Edit existing inventory item"""
    item = get_inventory_item(item_name)
    if not item:
        flash(f'Item "{item_name}" not found.', 'danger')
        return redirect(url_for('inventory'))
    
    if request.method == 'POST':
        new_name = request.form['name'].strip()
        
        # Check if name is being changed and if new name already exists
        if new_name != item_name:
            existing_item = get_inventory_item(new_name)
            if existing_item:
                flash(f'Item "{new_name}" already exists. Please choose a different name.', 'danger')
                vendors = read_vendors()
                categories = get_category_names()
                return render_template('edit_item.html', item=item, vendors=vendors, categories=categories)
        
        # Update item details
        item.name = new_name
        item.unit = request.form['unit'].strip()
        item.quantity = float(request.form['quantity'])
        item.par_level = int(request.form['par_level'])
        item.category = request.form.get('category', 'General').strip()
        item.unit_cost = float(request.form.get('unit_cost', 0.0))
        item.vendors = request.form.get('vendors', '').strip()
        item.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # If name changed, delete old item and create new one
        if new_name != item_name:
            if delete_inventory_item(item_name):
                items = read_inventory()
                items.append(item)
                write_inventory(items)
                flash(f'Item renamed from "{item_name}" to "{new_name}" successfully.', 'success')
            else:
                flash(f'Error renaming item "{item_name}".', 'danger')
        else:
            # Save changes to existing item
            if update_inventory_item(item_name, item):
                flash(f'Item "{item_name}" updated successfully.', 'success')
            else:
                flash(f'Error updating item "{item_name}".', 'danger')
        
        return redirect(url_for('inventory'))
    
    # Get vendors and categories for form dropdowns
    vendors = read_vendors()
    categories = get_category_names()
    
    return render_template('edit_item.html', item=item, vendors=vendors, categories=categories)

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
@require_login
def update_count(item_name):
    """Update item count (for staff users and managers)"""
    user = get_user(session['username'])
    if not (user.has_permission('record_counts') or user.has_permission('edit')):
        flash('You do not have permission to update inventory counts.', 'danger')
        return redirect(url_for('inventory'))
    
    item = get_inventory_item(item_name)
    if not item:
        flash(f'Item "{item_name}" not found.', 'danger')
        return redirect(url_for('inventory'))
    
    new_count = float(request.form['count'])
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
    """Waste logging page with full CRUD operations"""
    # Check if we need to archive old waste data
    try:
        if check_and_archive_if_needed():
            flash('Waste log archived automatically (7+ days old data moved to archive).', 'info')
    except Exception:
        # If archival check fails, continue without archiving
        pass
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            try:
                item_name = request.form['item_name'].strip()
                quantity = float(request.form['quantity'])
                unit = request.form['unit'].strip()
                reason = request.form['reason'].strip()
                
                # Get unit cost from inventory item
                item = get_inventory_item(item_name)
                unit_cost = item.unit_cost if item else 0.0
                
                # Create waste entry
                entry = WasteEntry(
                    item_name=item_name,
                    quantity=quantity,
                    unit=unit,
                    reason=reason,
                    date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    logged_by=session['username'],
                    unit_cost=unit_cost
                )
                
                # Add to waste log
                add_waste_entry(entry)
                
                # Update inventory if item exists
                if item:
                    item.quantity = max(0, item.quantity - quantity)
                    item.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_inventory_item(item_name, item)
                
                flash(f'Waste logged for "{item_name}".', 'success')
            except Exception as e:
                flash(f'Error logging waste entry: {str(e)}', 'danger')
        
        elif action == 'edit':
            try:
                entry_index = int(request.form.get('entry_index', -1))
                item_name = request.form['item_name'].strip()
                quantity = float(request.form['quantity'])
                unit = request.form['unit'].strip()
                reason = request.form['reason'].strip()
                
                # Get original entry to restore inventory
                original_entry = get_waste_entry(entry_index)
                if original_entry:
                    # Restore inventory from original entry
                    original_item = get_inventory_item(original_entry.item_name)
                    if original_item:
                        original_item.quantity += original_entry.quantity
                        update_inventory_item(original_entry.item_name, original_item)
                
                # Get unit cost from inventory item
                item = get_inventory_item(item_name)
                unit_cost = item.unit_cost if item else 0.0
                
                # Create updated entry
                updated_entry = WasteEntry(
                    item_name=item_name,
                    quantity=quantity,
                    unit=unit,
                    reason=reason,
                    date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    logged_by=session['username'],
                    unit_cost=unit_cost
                )
                
                # Update waste log
                if update_waste_entry(entry_index, updated_entry):
                    # Update inventory with new waste
                    if item:
                        item.quantity = max(0, item.quantity - quantity)
                        item.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        update_inventory_item(item_name, item)
                    
                    flash(f'Waste entry updated successfully.', 'success')
                else:
                    flash('Error updating waste entry.', 'danger')
            except Exception as e:
                flash(f'Error updating waste entry: {str(e)}', 'danger')
        
        elif action == 'delete':
            try:
                entry_index = int(request.form.get('entry_index', -1))
                
                # Get entry to restore inventory
                entry = get_waste_entry(entry_index)
                if entry:
                    # Restore inventory
                    item = get_inventory_item(entry.item_name)
                    if item:
                        item.quantity += entry.quantity
                        item.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        update_inventory_item(entry.item_name, item)
                    
                    # Delete entry
                    if delete_waste_entry(entry_index):
                        flash(f'Waste entry deleted successfully.', 'success')
                    else:
                        flash('Error deleting waste entry.', 'danger')
                else:
                    flash('Waste entry not found.', 'danger')
            except Exception as e:
                flash(f'Error deleting waste entry: {str(e)}', 'danger')
        
        return redirect(url_for('waste_log'))
    
    # Get waste log entries and inventory items
    waste_entries = read_waste_log()
    inventory_items = read_inventory()
    user = get_user(session['username'])
    
    # Convert inventory items to dict format for JavaScript
    inventory_data = [item.to_dict() for item in inventory_items]
    
    # Calculate total waste value
    total_waste_value = sum(entry.waste_value() for entry in waste_entries)
    
    return render_template('waste_log.html', 
                         waste_entries=waste_entries, 
                         inventory_items=inventory_items,
                         inventory_data=inventory_data,
                         total_waste_value=total_waste_value,
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

# Vendor Management Routes
@app.route('/vendors', methods=['GET', 'POST'])
@require_permission('edit')
def vendors():
    """Vendor management page"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name', '').strip()
            contact_info = request.form.get('contact_info', '').strip()
            address = request.form.get('address', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            exclude_from_shopping_list = request.form.get('exclude_from_shopping_list') == 'on'
            
            if not name:
                flash('Vendor name is required.', 'danger')
                return redirect(url_for('vendors'))
            
            new_vendor = Vendor(
                name=name,
                contact_info=contact_info,
                address=address,
                phone=phone,
                email=email,
                exclude_from_shopping_list=exclude_from_shopping_list
            )
            
            if add_vendor(new_vendor):
                flash(f'Vendor "{name}" added successfully.', 'success')
            else:
                flash(f'Vendor "{name}" already exists.', 'danger')
        
        elif action == 'edit':
            old_name = request.form.get('old_name', '').strip()
            new_name = request.form.get('new_name', '').strip()
            contact_info = request.form.get('contact_info', '').strip()
            address = request.form.get('address', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            exclude_from_shopping_list = request.form.get('exclude_from_shopping_list') == 'on'
            
            if not old_name or not new_name:
                flash('Vendor name is required.', 'danger')
                return redirect(url_for('vendors'))
            
            updated_vendor = Vendor(
                name=new_name,
                contact_info=contact_info,
                address=address,
                phone=phone,
                email=email,
                exclude_from_shopping_list=exclude_from_shopping_list
            )
            
            if update_vendor(old_name, updated_vendor):
                flash(f'Vendor "{old_name}" updated successfully.', 'success')
            else:
                flash(f'Vendor "{old_name}" not found.', 'danger')
        
        elif action == 'delete':
            vendor_name = request.form.get('vendor_name', '').strip()
            
            if not vendor_name:
                flash('Vendor name is required.', 'danger')
                return redirect(url_for('vendors'))
            
            # Check if vendor is in use
            if is_vendor_in_use(vendor_name):
                flash(f'Vendor "{vendor_name}" is in use and cannot be deleted.', 'danger')
            else:
                if delete_vendor(vendor_name):
                    flash(f'Vendor "{vendor_name}" deleted successfully.', 'success')
                else:
                    flash(f'Error deleting vendor "{vendor_name}".', 'danger')
        
        return redirect(url_for('vendors'))
    
    # Get all vendors
    vendors = read_vendors()
    
    # Get usage information for each vendor
    vendor_usage = {}
    for vendor in vendors:
        vendor_usage[vendor.name] = is_vendor_in_use(vendor.name)
    
    return render_template('vendors.html', vendors=vendors, vendor_usage=vendor_usage)

@app.route('/add_vendor', methods=['GET', 'POST'])
@require_permission('edit')
def add_vendor_route():
    """Add new vendor"""
    if request.method == 'POST':
        name = request.form['name'].strip()
        contact_info = request.form.get('contact_info', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        
        # Check if vendor already exists
        if get_vendor(name):
            flash(f'Vendor "{name}" already exists.', 'danger')
            return render_template('add_vendor.html')
        
        # Create new vendor
        new_vendor = Vendor(
            name=name,
            contact_info=contact_info,
            address=address,
            phone=phone,
            email=email
        )
        
        if add_vendor(new_vendor):
            flash(f'Vendor "{name}" added successfully.', 'success')
            return redirect(url_for('vendors'))
        else:
            flash(f'Error adding vendor "{name}".', 'danger')
    
    return render_template('add_vendor.html')

@app.route('/edit_vendor/<vendor_name>', methods=['GET', 'POST'])
@require_permission('edit')
def edit_vendor(vendor_name):
    """Edit existing vendor"""
    vendor = get_vendor(vendor_name)
    if not vendor:
        flash(f'Vendor "{vendor_name}" not found.', 'danger')
        return redirect(url_for('vendors'))
    
    if request.method == 'POST':
        vendor.contact_info = request.form.get('contact_info', '').strip()
        vendor.address = request.form.get('address', '').strip()
        vendor.phone = request.form.get('phone', '').strip()
        vendor.email = request.form.get('email', '').strip()
        
        # Update vendor
        vendors = read_vendors()
        for i, v in enumerate(vendors):
            if v.name == vendor_name:
                vendors[i] = vendor
                break
        
        write_vendors(vendors)
        flash(f'Vendor "{vendor_name}" updated successfully.', 'success')
        return redirect(url_for('vendors'))
    
    return render_template('edit_vendor.html', vendor=vendor)



@app.route('/categories', methods=['GET', 'POST'])
@require_permission('edit')
def categories():
    """Category management page"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('Category name is required.', 'danger')
                return redirect(url_for('categories'))
            
            new_category = Category(
                name=name,
                description=description,
                created_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            if add_category(new_category):
                flash(f'Category "{name}" added successfully.', 'success')
            else:
                flash(f'Category "{name}" already exists.', 'danger')
        
        elif action == 'edit':
            old_name = request.form.get('old_name', '').strip()
            new_name = request.form.get('new_name', '').strip()
            new_description = request.form.get('new_description', '').strip()
            
            if not old_name or not new_name:
                flash('Category name is required.', 'danger')
                return redirect(url_for('categories'))
            
            updated_category = Category(
                name=new_name,
                description=new_description,
                created_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            if update_category(old_name, updated_category):
                flash(f'Category "{old_name}" updated successfully.', 'success')
            else:
                flash(f'Category "{old_name}" not found.', 'danger')
        
        elif action == 'delete':
            category_name = request.form.get('category_name', '').strip()
            
            if not category_name:
                flash('Category name is required.', 'danger')
                return redirect(url_for('categories'))
            
            # Check if category is in use
            if is_category_in_use(category_name):
                flash(f'Category "{category_name}" is in use and cannot be deleted.', 'danger')
            else:
                if delete_category(category_name):
                    flash(f'Category "{category_name}" deleted successfully.', 'success')
                else:
                    flash(f'Error deleting category "{category_name}".', 'danger')
        
        return redirect(url_for('categories'))
    
    # Get all categories
    categories = read_categories()
    
    # Get usage information for each category
    category_usage = {}
    for category in categories:
        category_usage[category.name] = is_category_in_use(category.name)
    
    return render_template('categories.html', categories=categories, category_usage=category_usage)

# PDF Generation Routes
@app.route('/generate_shopping_list_pdf')
@require_permission('view')
def generate_shopping_list_pdf_route():
    """Generate shopping list PDF"""
    try:
        pdf_bytes = generate_shopping_list_pdf()
        
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="shopping_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response
    except Exception as e:
        flash(f'Error generating shopping list PDF: {str(e)}', 'danger')
        return redirect(url_for('inventory'))

# Weekly Waste Reports Routes
@app.route('/weekly_waste_reports')
@require_permission('view')
def weekly_waste_reports():
    """Weekly waste reports and comparison page"""
    # Initialize waste archive if needed
    initialize_waste_archive()
    
    # Get weekly reports
    weekly_reports = read_weekly_reports()
    
    # Get week-to-week comparison
    current_week, previous_week = get_week_comparison()
    
    # Calculate comparison data
    comparison_data = None
    if current_week and previous_week:
        comparison_data = {
            'current': current_week,
            'previous': previous_week,
            'value_change': current_week.total_value - previous_week.total_value,
            'entries_change': current_week.total_entries - previous_week.total_entries,
            'value_change_percent': ((current_week.total_value - previous_week.total_value) / previous_week.total_value * 100) if previous_week.total_value > 0 else 0,
            'entries_change_percent': ((current_week.total_entries - previous_week.total_entries) / previous_week.total_entries * 100) if previous_week.total_entries > 0 else 0
        }
    
    # Get current week data (if any)
    current_waste_entries = read_waste_log()
    current_week_data = None
    if current_waste_entries:
        # Calculate current week totals
        total_value = sum(entry.waste_value() for entry in current_waste_entries)
        total_entries = len(current_waste_entries)
        
        # Group by category
        by_category = {}
        inventory_items = {item.name: item for item in read_inventory()}
        for entry in current_waste_entries:
            item = inventory_items.get(entry.item_name)
            category = item.category if item else 'Unknown'
            by_category[category] = by_category.get(category, 0) + entry.waste_value()
        
        # Group by reason
        by_reason = {}
        for entry in current_waste_entries:
            by_reason[entry.reason] = by_reason.get(entry.reason, 0) + entry.waste_value()
        
        current_week_data = {
            'total_value': total_value,
            'total_entries': total_entries,
            'by_category': by_category,
            'by_reason': by_reason
        }
    
    return render_template('weekly_waste_reports.html', 
                         weekly_reports=weekly_reports, 
                         comparison_data=comparison_data,
                         current_week_data=current_week_data)

@app.route('/force_archive', methods=['POST'])
@require_permission('edit')
def force_archive():
    """Force archive current waste log (for testing/admin purposes)"""
    from utils import archive_waste_log
    
    entries = read_waste_log()
    if not entries:
        flash('No waste entries to archive.', 'warning')
    else:
        archive_waste_log()
        flash('Waste log archived successfully.', 'success')
    
    return redirect(url_for('weekly_waste_reports'))


