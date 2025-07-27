"""
Utility functions for CSV operations and data management.
"""
import csv
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, InventoryItem, WasteEntry, Vendor, Category, WeeklyWasteReport, WeeklyInventoryReport, DEFAULT_VENDORS, DEFAULT_CATEGORIES
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO

# File paths
INVENTORY_FILE = 'inventory.csv'
USERS_FILE = 'users.csv'
WASTE_LOG_FILE = 'waste_log.csv'
VENDORS_FILE = 'vendors.csv'
CATEGORIES_FILE = 'categories.csv'
WASTE_ARCHIVE_DIR = 'waste_archive'
WEEKLY_REPORTS_FILE = 'weekly_waste_reports.csv'
WEEKLY_INVENTORY_REPORTS_FILE = 'weekly_inventory_reports.csv'

def initialize_csv_files():
    """Initialize CSV files with headers if they don't exist"""
    
    # Initialize inventory.csv
    if not os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'unit', 'quantity', 'par_level', 'category', 'unit_cost', 'vendors', 'last_updated'])
            writer.writeheader()
    
    # Initialize users.csv with default admin user
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['username', 'password_hash', 'role', 'email'])
            writer.writeheader()
            # Create default admin user
            admin_user = {
                'username': 'admin',
                'password_hash': generate_password_hash('admin123'),
                'role': 'admin',
                'email': 'admin@healthpackmeals.com'
            }
            writer.writerow(admin_user)
    
    # Initialize waste_log.csv
    if not os.path.exists(WASTE_LOG_FILE):
        with open(WASTE_LOG_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost'])
            writer.writeheader()
    
    # Initialize vendors.csv with default vendors
    if not os.path.exists(VENDORS_FILE):
        with open(VENDORS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'contact_info', 'address', 'phone', 'email'])
            writer.writeheader()
            for vendor_name in DEFAULT_VENDORS:
                vendor = {
                    'name': vendor_name,
                    'contact_info': '',
                    'address': '',
                    'phone': '',
                    'email': ''
                }
                writer.writerow(vendor)
    

    # Initialize categories.csv with default categories
    if not os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'description', 'created_date'])
            writer.writeheader()
            # Add default categories
            for category_name in DEFAULT_CATEGORIES:
                writer.writerow({
                    'name': category_name,
                    'description': f'Default {category_name} category',
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # Initialize weekly reports
    initialize_waste_archive()
    
    # Initialize weekly inventory reports
    initialize_weekly_inventory_reports()

def read_inventory() -> List[InventoryItem]:
    """Read inventory items from CSV file"""
    items = []
    try:
        with open(INVENTORY_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                item = InventoryItem(
                    name=row['name'],
                    unit=row['unit'],
                    quantity=float(row['quantity']),
                    par_level=int(row['par_level']),
                    category=row.get('category', 'General'),
                    unit_cost=float(row.get('unit_cost', 0.0)),
                    vendors=row.get('vendors', ''),
                    last_updated=row.get('last_updated', '')
                )
                items.append(item)
    except FileNotFoundError:
        pass
    return items

def write_inventory(items: List[InventoryItem]):
    """Write inventory items to CSV file"""
    with open(INVENTORY_FILE, 'w', newline='') as file:
        fieldnames = ['name', 'unit', 'quantity', 'par_level', 'category', 'unit_cost', 'vendors', 'last_updated']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item.to_dict())

def get_inventory_item(name: str) -> Optional[InventoryItem]:
    """Get a specific inventory item by name"""
    items = read_inventory()
    for item in items:
        if item.name == name:
            return item
    return None

def update_inventory_item(name: str, updated_item: InventoryItem) -> bool:
    """Update a specific inventory item"""
    items = read_inventory()
    for i, item in enumerate(items):
        if item.name == name:
            items[i] = updated_item
            write_inventory(items)
            return True
    return False

def delete_inventory_item(name: str) -> bool:
    """Delete a specific inventory item"""
    items = read_inventory()
    original_length = len(items)
    items = [item for item in items if item.name != name]
    if len(items) < original_length:
        write_inventory(items)
        return True
    return False

def read_users() -> List[User]:
    """Read users from CSV file"""
    users = []
    try:
        with open(USERS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user = User(
                    username=row['username'],
                    password_hash=row['password_hash'],
                    role=row['role'],
                    email=row.get('email', '')
                )
                users.append(user)
    except FileNotFoundError:
        pass
    return users

def get_user(username: str) -> Optional[User]:
    """Get a specific user by username"""
    users = read_users()
    for user in users:
        if user.username == username:
            return user
    return None

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user(username)
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

def read_waste_log() -> List[WasteEntry]:
    """Read waste log entries from CSV file"""
    entries = []
    try:
        with open(WASTE_LOG_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Clean up the unit_cost field to handle any parsing issues
                    unit_cost_str = row.get('unit_cost', '0.0')
                    # Extract only numeric characters and decimal point
                    import re
                    unit_cost_clean = re.match(r'^[\d.]+', str(unit_cost_str))
                    unit_cost = float(unit_cost_clean.group()) if unit_cost_clean else 0.0
                    
                    entry = WasteEntry(
                        item_name=row['item_name'],
                        quantity=float(row['quantity']),
                        unit=row['unit'],
                        reason=row['reason'],
                        date=row['date'],
                        logged_by=row['logged_by'],
                        unit_cost=unit_cost
                    )
                    entries.append(entry)
                except (ValueError, KeyError) as e:
                    # Skip malformed entries and log the error
                    print(f"Skipping malformed waste log entry: {row}, Error: {e}")
                    continue
    except FileNotFoundError:
        pass
    return entries

def add_waste_entry(entry: WasteEntry):
    """Add a new waste log entry"""
    # Read existing entries
    entries = read_waste_log()
    # Add new entry
    entries.append(entry)
    # Write all entries back to ensure proper formatting
    write_waste_log(entries)

def write_waste_log(entries: List[WasteEntry]):
    """Write waste log entries to CSV file"""
    with open(WASTE_LOG_FILE, 'w', newline='') as file:
        fieldnames = ['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.to_dict())

def update_waste_entry(entry_index: int, updated_entry: WasteEntry) -> bool:
    """Update a waste log entry by index"""
    try:
        entries = read_waste_log()
        if 0 <= entry_index < len(entries):
            entries[entry_index] = updated_entry
            write_waste_log(entries)
            return True
        return False
    except Exception:
        return False

def delete_waste_entry(entry_index: int) -> bool:
    """Delete a waste log entry by index"""
    try:
        entries = read_waste_log()
        if 0 <= entry_index < len(entries):
            entries.pop(entry_index)
            write_waste_log(entries)
            return True
        return False
    except Exception:
        return False

def get_waste_entry(entry_index: int) -> Optional[WasteEntry]:
    """Get a specific waste log entry by index"""
    try:
        entries = read_waste_log()
        if 0 <= entry_index < len(entries):
            return entries[entry_index]
        return None
    except Exception:
        return None

def get_low_stock_items() -> List[InventoryItem]:
    """Get all items that are below par level (excluding HPM items)"""
    items = read_inventory()
    return [item for item in items if item.is_low_stock() and 'HPM' not in item.get_vendors()]

def export_inventory_csv() -> str:
    """Export inventory data as CSV string"""
    items = read_inventory()
    if not items:
        return ""
    
    output = "name,unit,quantity,par_level,category,unit_cost,vendors,last_updated\n"
    for item in items:
        output += f"{item.name},{item.unit},{item.quantity},{item.par_level},{item.category},{item.unit_cost},{item.vendors},{item.last_updated}\n"
    return output

def import_inventory_csv(csv_data: str) -> tuple[bool, str]:
    """Import inventory data from CSV string"""
    try:
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            return False, "CSV must have at least a header and one data row"
        
        # Parse header
        header = lines[0].split(',')
        required_fields = ['name', 'unit', 'quantity', 'par_level']
        
        for field in required_fields:
            if field not in header:
                return False, f"Missing required field: {field}"
        
        # Parse data rows
        items = []
        for i, line in enumerate(lines[1:], 2):
            try:
                values = line.split(',')
                if len(values) != len(header):
                    return False, f"Row {i}: Number of values doesn't match header"
                
                row_data = dict(zip(header, values))
                item = InventoryItem(
                    name=row_data['name'].strip(),
                    unit=row_data['unit'].strip(),
                    quantity=int(row_data['quantity']),
                    par_level=int(row_data['par_level']),
                    category=row_data.get('category', 'General').strip(),
                    unit_cost=float(row_data.get('unit_cost', 0.0)),
                    vendors=row_data.get('vendors', '').strip(),
                    last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                items.append(item)
            except ValueError as e:
                return False, f"Row {i}: Invalid data format - {str(e)}"
        
        # Write to file
        write_inventory(items)
        return True, f"Successfully imported {len(items)} items"
        
    except Exception as e:
        return False, f"Error parsing CSV: {str(e)}"

# Vendor management functions
def read_vendors() -> List[Vendor]:
    """Read vendors from CSV file"""
    vendors = []
    try:
        with open(VENDORS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                vendor = Vendor(
                    name=row['name'],
                    contact_info=row.get('contact_info', ''),
                    address=row.get('address', ''),
                    phone=row.get('phone', ''),
                    email=row.get('email', ''),
                    exclude_from_shopping_list=row.get('exclude_from_shopping_list', 'False').lower() == 'true'
                )
                vendors.append(vendor)
    except FileNotFoundError:
        pass
    return vendors

def write_vendors(vendors: List[Vendor]):
    """Write vendors to CSV file"""
    with open(VENDORS_FILE, 'w', newline='') as file:
        fieldnames = ['name', 'contact_info', 'address', 'phone', 'email', 'exclude_from_shopping_list']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for vendor in vendors:
            writer.writerow(vendor.to_dict())

def get_vendor(name: str) -> Optional[Vendor]:
    """Get a specific vendor by name"""
    vendors = read_vendors()
    for vendor in vendors:
        if vendor.name == name:
            return vendor
    return None

def add_vendor(vendor: Vendor) -> bool:
    """Add a new vendor"""
    vendors = read_vendors()
    # Check if vendor already exists
    if any(v.name == vendor.name for v in vendors):
        return False
    vendors.append(vendor)
    write_vendors(vendors)
    return True

def update_vendor(old_name: str, updated_vendor: Vendor) -> bool:
    """Update an existing vendor"""
    try:
        vendors = read_vendors()
        for i, vendor in enumerate(vendors):
            if vendor.name == old_name:
                vendors[i] = updated_vendor
                write_vendors(vendors)
                return True
        return False
    except Exception:
        return False

def delete_vendor(name: str) -> bool:
    """Delete a vendor"""
    try:
        vendors = read_vendors()
        vendors = [vendor for vendor in vendors if vendor.name != name]
        write_vendors(vendors)
        return True
    except Exception:
        return False

def is_vendor_in_use(vendor_name: str) -> bool:
    """Check if a vendor is being used by any inventory items"""
    items = read_inventory()
    for item in items:
        if vendor_name in item.get_vendors():
            return True
    return False



# Filtering and search functions
def filter_inventory(category: str = None, vendor: str = None, low_stock_only: bool = False) -> List[InventoryItem]:
    """Filter inventory items based on criteria"""
    items = read_inventory()
    
    if category:
        items = [item for item in items if item.category == category]
    
    if vendor:
        items = [item for item in items if vendor in item.get_vendors()]
    
    if low_stock_only:
        items = [item for item in items if item.is_low_stock()]
    
    return items

def get_shopping_list_items() -> List[InventoryItem]:
    """Get items that need to be restocked (low stock items), excluding items from excluded vendors and HPM items"""
    low_stock_items = filter_inventory(low_stock_only=True)
    
    # Get excluded vendors
    excluded_vendors = set()
    vendors = read_vendors()
    for vendor in vendors:
        if vendor.exclude_from_shopping_list:
            excluded_vendors.add(vendor.name)
    
    # Always exclude HPM items from main shopping list
    excluded_vendors.add('HPM')
    
    # Filter out items from excluded vendors
    filtered_items = []
    for item in low_stock_items:
        item_vendors = item.get_vendors()
        if not item_vendors:  # Items with no vendor are included
            filtered_items.append(item)
        else:
            # Include item if it has at least one non-excluded vendor
            if not all(vendor in excluded_vendors for vendor in item_vendors):
                filtered_items.append(item)
    
    return filtered_items



# PDF generation functions
def generate_shopping_list_pdf() -> bytes:
    """Generate shopping list PDF for low stock items"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue
    )
    story.append(Paragraph("Health Pack Meals - Shopping List", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Get low stock items
    low_stock_items = get_shopping_list_items()
    
    if not low_stock_items:
        story.append(Paragraph("No items are currently low in stock.", styles['Normal']))
    else:
        # Get excluded vendors
        excluded_vendors = set()
        vendors = read_vendors()
        for vendor in vendors:
            if vendor.exclude_from_shopping_list:
                excluded_vendors.add(vendor.name)
        
        # Group items by vendor, excluding excluded vendors
        vendor_groups = {}
        for item in low_stock_items:
            item_vendors = item.get_vendors() if item.get_vendors() else ['No Vendor Assigned']
            for vendor in item_vendors:
                if vendor not in excluded_vendors:  # Skip excluded vendors
                    if vendor not in vendor_groups:
                        vendor_groups[vendor] = []
                    vendor_groups[vendor].append(item)
        
        # Create table for each vendor
        for vendor, items in vendor_groups.items():
            story.append(Paragraph(f"Vendor: {vendor}", styles['Heading2']))
            
            # Table data
            table_data = [['Item Name', 'Current Stock', 'Par Level', 'Needed', 'Unit', 'Unit Cost', 'Total Cost']]
            total_cost = 0
            
            for item in items:
                needed = item.quantity_needed()
                item_cost = needed * item.unit_cost
                total_cost += item_cost
                
                table_data.append([
                    item.name,
                    str(item.quantity),
                    str(item.par_level),
                    str(needed),
                    item.unit,
                    f"${item.unit_cost:.2f}",
                    f"${item_cost:.2f}"
                ])
            
            # Add total row
            table_data.append(['', '', '', '', '', 'Total:', f"${total_cost:.2f}"])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes





# Category Management Functions
def read_categories() -> List[Category]:
    """Read categories from CSV file"""
    categories = []
    try:
        with open(CATEGORIES_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = Category(
                    name=row['name'],
                    description=row.get('description', ''),
                    created_date=row.get('created_date', '')
                )
                categories.append(category)
    except FileNotFoundError:
        # If file doesn't exist, return default categories
        for category_name in DEFAULT_CATEGORIES:
            categories.append(Category(
                name=category_name,
                description=f'Default {category_name} category',
                created_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
    return categories

def write_categories(categories: List[Category]):
    """Write categories to CSV file"""
    with open(CATEGORIES_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'description', 'created_date'])
        writer.writeheader()
        for category in categories:
            writer.writerow(category.to_dict())

def get_category(name: str) -> Optional[Category]:
    """Get a specific category by name"""
    categories = read_categories()
    for category in categories:
        if category.name == name:
            return category
    return None

def add_category(category: Category) -> bool:
    """Add a new category"""
    try:
        categories = read_categories()
        # Check if category already exists
        for existing_category in categories:
            if existing_category.name == category.name:
                return False
        categories.append(category)
        write_categories(categories)
        return True
    except Exception:
        return False

def update_category(old_name: str, updated_category: Category) -> bool:
    """Update an existing category"""
    try:
        categories = read_categories()
        for i, category in enumerate(categories):
            if category.name == old_name:
                categories[i] = updated_category
                write_categories(categories)
                return True
        return False
    except Exception:
        return False

def delete_category(name: str) -> bool:
    """Delete a category"""
    try:
        categories = read_categories()
        categories = [cat for cat in categories if cat.name != name]
        write_categories(categories)
        return True
    except Exception:
        return False

def get_category_names() -> List[str]:
    """Get list of all category names"""
    categories = read_categories()
    return [category.name for category in categories]

def is_category_in_use(category_name: str) -> bool:
    """Check if a category is being used by any inventory items"""
    items = read_inventory()
    for item in items:
        if item.category == category_name:
            return True
    return False

# Waste Log Archival Functions

def initialize_waste_archive():
    """Initialize waste archive directory and weekly reports file"""
    if not os.path.exists(WASTE_ARCHIVE_DIR):
        os.makedirs(WASTE_ARCHIVE_DIR)
    
    if not os.path.exists(WEEKLY_REPORTS_FILE):
        with open(WEEKLY_REPORTS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['week_start', 'week_end', 'total_entries', 'total_value', 'by_category', 'by_reason', 'by_item'])
            writer.writeheader()

def should_archive_waste_log() -> bool:
    """Check if waste log should be archived (7 days old)"""
    if not os.path.exists(WASTE_LOG_FILE):
        return False
    
    # Check if file has any entries
    entries = read_waste_log()
    if not entries:
        return False
    
    try:
        # Check if oldest entry is 7+ days old
        oldest_entry_date = min(datetime.strptime(entry.date, '%Y-%m-%d %H:%M:%S') for entry in entries)
        return (datetime.now() - oldest_entry_date).days >= 7
    except (ValueError, TypeError):
        # If there's an issue parsing dates, don't archive
        return False

def generate_weekly_report(entries: List[WasteEntry], week_start: str, week_end: str) -> WeeklyWasteReport:
    """Generate weekly waste report from entries"""
    total_entries = len(entries)
    total_value = sum(entry.waste_value() for entry in entries)
    
    # Group by category (get category from inventory)
    by_category = {}
    inventory_items = {item.name: item for item in read_inventory()}
    
    for entry in entries:
        item = inventory_items.get(entry.item_name)
        category = item.category if item else 'Unknown'
        by_category[category] = by_category.get(category, 0) + entry.waste_value()
    
    # Group by reason
    by_reason = {}
    for entry in entries:
        by_reason[entry.reason] = by_reason.get(entry.reason, 0) + entry.waste_value()
    
    # Group by item
    by_item = {}
    for entry in entries:
        by_item[entry.item_name] = by_item.get(entry.item_name, 0) + entry.waste_value()
    
    return WeeklyWasteReport(
        week_start=week_start,
        week_end=week_end,
        total_entries=total_entries,
        total_value=total_value,
        by_category=by_category,
        by_reason=by_reason,
        by_item=by_item
    )

def archive_waste_log():
    """Archive current waste log and generate weekly report"""
    entries = read_waste_log()
    if not entries:
        return
    
    # Initialize archive if needed
    initialize_waste_archive()
    
    # Determine week boundaries
    now = datetime.now()
    week_start = now - timedelta(days=7)
    week_end = now
    
    # Generate weekly report
    report = generate_weekly_report(entries, week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d'))
    
    # Save weekly report
    save_weekly_report(report)
    
    # Archive waste log file
    archive_filename = f"waste_log_{week_start.strftime('%Y%m%d')}_{week_end.strftime('%Y%m%d')}.csv"
    archive_path = os.path.join(WASTE_ARCHIVE_DIR, archive_filename)
    shutil.copy2(WASTE_LOG_FILE, archive_path)
    
    # Clear current waste log
    with open(WASTE_LOG_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost'])
        writer.writeheader()

def save_weekly_report(report: WeeklyWasteReport):
    """Save weekly report to file"""
    with open(WEEKLY_REPORTS_FILE, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['week_start', 'week_end', 'total_entries', 'total_value', 'by_category', 'by_reason', 'by_item'])
        writer.writerow(report.to_dict())

def read_weekly_reports() -> List[WeeklyWasteReport]:
    """Read weekly waste reports from file"""
    reports = []
    if not os.path.exists(WEEKLY_REPORTS_FILE):
        return reports
    
    try:
        with open(WEEKLY_REPORTS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse dictionary strings back to dicts
                by_category = eval(row['by_category']) if row['by_category'] else {}
                by_reason = eval(row['by_reason']) if row['by_reason'] else {}
                by_item = eval(row['by_item']) if row['by_item'] else {}
                
                report = WeeklyWasteReport(
                    week_start=row['week_start'],
                    week_end=row['week_end'],
                    total_entries=int(row['total_entries']),
                    total_value=float(row['total_value']),
                    by_category=by_category,
                    by_reason=by_reason,
                    by_item=by_item
                )
                reports.append(report)
    except Exception:
        pass
    
    return reports

def get_week_comparison(weeks_back: int = 1) -> Tuple[Optional[WeeklyWasteReport], Optional[WeeklyWasteReport]]:
    """Get comparison between current week and previous week(s)"""
    reports = read_weekly_reports()
    if len(reports) < weeks_back + 1:
        return None, None
    
    current_report = reports[-1]
    previous_report = reports[-(weeks_back + 1)]
    
    return current_report, previous_report

def check_and_archive_if_needed():
    """Check if archival is needed and perform it"""
    try:
        if should_archive_waste_log():
            archive_waste_log()
            return True
        return False
    except Exception:
        # If archival fails, don't break the application
        return False

# Weekly Inventory Tracking Functions
def initialize_weekly_inventory_reports():
    """Initialize weekly inventory reports file"""
    if not os.path.exists(WEEKLY_INVENTORY_REPORTS_FILE):
        with open(WEEKLY_INVENTORY_REPORTS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['week_start', 'week_end', 'total_items', 'total_value', 'by_category', 'by_vendor', 'low_stock_items', 'generated_date'])
            writer.writeheader()

def should_generate_weekly_inventory_report() -> bool:
    """Check if it's time to generate a weekly inventory report (every 7 days)"""
    reports = read_weekly_inventory_reports()
    if not reports:
        return True
    
    last_report = reports[-1]
    last_date = datetime.strptime(last_report.week_end, '%Y-%m-%d')
    current_date = datetime.now()
    
    return (current_date - last_date).days >= 7

def generate_weekly_inventory_report() -> WeeklyInventoryReport:
    """Generate weekly inventory report from current inventory (excluding HPM items)"""
    current_date = datetime.now()
    week_start = (current_date - timedelta(days=current_date.weekday())).strftime('%Y-%m-%d')
    week_end = (current_date + timedelta(days=6-current_date.weekday())).strftime('%Y-%m-%d')
    
    # Get all inventory items excluding HPM items
    all_items = read_inventory()
    non_hpm_items = [item for item in all_items if 'HPM' not in item.get_vendors()]
    
    # Calculate totals
    total_items = len(non_hpm_items)
    total_value = sum(item.total_value() for item in non_hpm_items)
    low_stock_items = len([item for item in non_hpm_items if item.is_low_stock()])
    
    # Group by category
    by_category = {}
    for item in non_hpm_items:
        category = item.category
        if category not in by_category:
            by_category[category] = 0
        by_category[category] += item.total_value()
    
    # Group by vendor
    by_vendor = {}
    for item in non_hpm_items:
        vendors = item.get_vendors() if item.get_vendors() else ['No Vendor']
        for vendor in vendors:
            if vendor not in by_vendor:
                by_vendor[vendor] = 0
            by_vendor[vendor] += item.total_value() / len(vendors)  # Split value across vendors
    
    return WeeklyInventoryReport(
        week_start=week_start,
        week_end=week_end,
        total_items=total_items,
        total_value=total_value,
        by_category=by_category,
        by_vendor=by_vendor,
        low_stock_items=low_stock_items,
        generated_date=current_date.strftime('%Y-%m-%d %H:%M:%S')
    )

def save_weekly_inventory_report(report: WeeklyInventoryReport):
    """Save weekly inventory report to file"""
    initialize_weekly_inventory_reports()
    with open(WEEKLY_INVENTORY_REPORTS_FILE, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['week_start', 'week_end', 'total_items', 'total_value', 'by_category', 'by_vendor', 'low_stock_items', 'generated_date'])
        writer.writerow(report.to_dict())

def read_weekly_inventory_reports() -> List[WeeklyInventoryReport]:
    """Read weekly inventory reports from file"""
    reports = []
    if not os.path.exists(WEEKLY_INVENTORY_REPORTS_FILE):
        return reports
    
    try:
        with open(WEEKLY_INVENTORY_REPORTS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse dictionary strings back to dicts
                by_category = eval(row['by_category']) if row['by_category'] else {}
                by_vendor = eval(row['by_vendor']) if row['by_vendor'] else {}
                
                report = WeeklyInventoryReport(
                    week_start=row['week_start'],
                    week_end=row['week_end'],
                    total_items=int(row['total_items']),
                    total_value=float(row['total_value']),
                    by_category=by_category,
                    by_vendor=by_vendor,
                    low_stock_items=int(row['low_stock_items']),
                    generated_date=row['generated_date']
                )
                reports.append(report)
    except Exception:
        pass
    
    return reports

def get_inventory_week_comparison(weeks_back: int = 1) -> Tuple[Optional[WeeklyInventoryReport], Optional[WeeklyInventoryReport]]:
    """Get comparison between current week and previous week(s) inventory reports"""
    reports = read_weekly_inventory_reports()
    if len(reports) < weeks_back + 1:
        return None, None
    
    current_report = reports[-1]
    previous_report = reports[-(weeks_back + 1)]
    
    return current_report, previous_report

def check_and_generate_inventory_report_if_needed():
    """Check if inventory report generation is needed and perform it"""
    try:
        if should_generate_weekly_inventory_report():
            report = generate_weekly_inventory_report()
            save_weekly_inventory_report(report)
            return True
        return False
    except Exception:
        # If report generation fails, don't break the application
        return False

# HPM-specific reporting functions
HPM_REPORTS_FILE = 'hpm_weekly_reports.csv'
HPM_WASTE_ARCHIVE_DIR = 'hpm_waste_archive'

def initialize_hpm_reports():
    """Initialize HPM reports CSV file if it doesn't exist"""
    if not os.path.exists(HPM_REPORTS_FILE):
        with open(HPM_REPORTS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['date', 'total_items', 'total_value', 'low_stock_count', 'total_waste_value', 'top_waste_categories', 'comparison_notes'])
            writer.writeheader()

def initialize_hpm_waste_archive():
    """Initialize HPM waste archive directory"""
    if not os.path.exists(HPM_WASTE_ARCHIVE_DIR):
        os.makedirs(HPM_WASTE_ARCHIVE_DIR)

def generate_hpm_weekly_report():
    """Generate a manual HPM weekly report"""
    from models import HPMWeeklyReport
    
    current_date = datetime.now()
    all_items = read_inventory()
    
    # Get HPM items only
    hpm_items = [item for item in all_items if 'HPM' in item.get_vendors()]
    
    # Get HPM waste entries
    all_waste_entries = read_waste_log()
    hpm_waste_entries = [entry for entry in all_waste_entries if any(item.name == entry.item_name for item in hpm_items)]
    
    # Calculate stats
    total_items = len(hpm_items)
    total_value = sum(item.total_value() for item in hpm_items)
    low_stock_count = len([item for item in hpm_items if item.is_low_stock()])
    total_waste_value = sum(entry.waste_value() for entry in hpm_waste_entries)
    
    # Get top waste categories
    waste_by_category = {}
    inventory_dict = {item.name: item for item in hpm_items}
    for entry in hpm_waste_entries:
        item = inventory_dict.get(entry.item_name)
        if item:
            category = item.category
            waste_by_category[category] = waste_by_category.get(category, 0) + entry.waste_value()
    
    # Format top categories
    sorted_categories = sorted(waste_by_category.items(), key=lambda x: x[1], reverse=True)
    top_categories = ', '.join([f"{cat}: ${val:.2f}" for cat, val in sorted_categories[:3]])
    
    # Generate comparison notes with previous report
    comparison_notes = generate_hpm_comparison_notes(total_items, total_value, low_stock_count, total_waste_value)
    
    return HPMWeeklyReport(
        date=current_date.strftime('%Y-%m-%d %H:%M:%S'),
        total_items=total_items,
        total_value=total_value,
        low_stock_count=low_stock_count,
        total_waste_value=total_waste_value,
        top_waste_categories=top_categories,
        comparison_notes=comparison_notes
    )

def save_hpm_report(report):
    """Save HPM report to file"""
    initialize_hpm_reports()
    with open(HPM_REPORTS_FILE, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'total_items', 'total_value', 'low_stock_count', 'total_waste_value', 'top_waste_categories', 'comparison_notes'])
        writer.writerow(report.to_dict())

def read_hpm_reports():
    """Read HPM reports from file"""
    from models import HPMWeeklyReport
    
    reports = []
    if not os.path.exists(HPM_REPORTS_FILE):
        return reports
    
    try:
        with open(HPM_REPORTS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                report = HPMWeeklyReport(
                    date=row['date'],
                    total_items=int(row['total_items']),
                    total_value=float(row['total_value']),
                    low_stock_count=int(row['low_stock_count']),
                    total_waste_value=float(row['total_waste_value']),
                    top_waste_categories=row['top_waste_categories'],
                    comparison_notes=row['comparison_notes']
                )
                reports.append(report)
    except Exception:
        pass
    
    return reports

def generate_hpm_comparison_notes(current_items, current_value, current_low_stock, current_waste):
    """Generate comparison notes with previous HPM report"""
    previous_reports = read_hpm_reports()
    if not previous_reports:
        return "First HPM report generated"
    
    last_report = previous_reports[-1]
    
    notes = []
    
    # Items comparison
    item_diff = current_items - last_report.total_items
    if item_diff > 0:
        notes.append(f"+{item_diff} items")
    elif item_diff < 0:
        notes.append(f"{item_diff} items")
    
    # Value comparison
    value_diff = current_value - last_report.total_value
    if abs(value_diff) > 1:  # Only note significant changes
        if value_diff > 0:
            notes.append(f"+${value_diff:.2f} inventory value")
        else:
            notes.append(f"-${abs(value_diff):.2f} inventory value")
    
    # Low stock comparison
    stock_diff = current_low_stock - last_report.low_stock_count
    if stock_diff > 0:
        notes.append(f"+{stock_diff} low stock items")
    elif stock_diff < 0:
        notes.append(f"{abs(stock_diff)} fewer low stock items")
    
    # Waste comparison
    waste_diff = current_waste - last_report.total_waste_value
    if abs(waste_diff) > 1:  # Only note significant changes
        if waste_diff > 0:
            notes.append(f"+${waste_diff:.2f} waste value")
        else:
            notes.append(f"-${abs(waste_diff):.2f} waste value")
    
    return "; ".join(notes) if notes else "No significant changes"

def archive_hpm_waste_log():
    """Archive HPM waste log entries and remove them from main log"""
    initialize_hpm_waste_archive()
    
    # Read all waste entries
    all_waste_entries = read_waste_log()
    all_items = read_inventory()
    
    # Get HPM items
    hpm_items = [item for item in all_items if 'HPM' in item.get_vendors()]
    hpm_item_names = set(item.name for item in hpm_items)
    
    # Separate HPM and non-HPM waste entries
    hpm_waste_entries = [entry for entry in all_waste_entries if entry.item_name in hpm_item_names]
    non_hpm_waste_entries = [entry for entry in all_waste_entries if entry.item_name not in hpm_item_names]
    
    if not hpm_waste_entries:
        return 0  # No HPM waste entries to archive
    
    # Create archive file with timestamp
    current_date = datetime.now()
    archive_filename = f"hpm_waste_log_{current_date.strftime('%Y%m%d_%H%M%S')}.csv"
    archive_path = os.path.join(HPM_WASTE_ARCHIVE_DIR, archive_filename)
    
    # Write HPM waste entries to archive
    with open(archive_path, 'w', newline='') as file:
        if hpm_waste_entries:
            writer = csv.DictWriter(file, fieldnames=['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost'])
            writer.writeheader()
            for entry in hpm_waste_entries:
                writer.writerow(entry.to_dict())
    
    # Rewrite main waste log with only non-HPM entries
    with open(WASTE_LOG_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost'])
        writer.writeheader()
        for entry in non_hpm_waste_entries:
            writer.writerow(entry.to_dict())
    
    return len(hpm_waste_entries)
