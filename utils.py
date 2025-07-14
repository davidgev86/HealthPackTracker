"""
Utility functions for CSV operations and data management.
"""
import csv
import os
from datetime import datetime
from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, InventoryItem, WasteEntry, Vendor, Recipe, Category, DEFAULT_VENDORS, DEFAULT_CATEGORIES
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
RECIPES_FILE = 'recipes.csv'
CATEGORIES_FILE = 'categories.csv'

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
    
    # Initialize recipes.csv
    if not os.path.exists(RECIPES_FILE):
        with open(RECIPES_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'ingredients', 'meat_type', 'meat_pounds', 'servings', 'description'])
            writer.writeheader()
    
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
                    quantity=int(row['quantity']),
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
                entry = WasteEntry(
                    item_name=row['item_name'],
                    quantity=int(row['quantity']),
                    unit=row['unit'],
                    reason=row['reason'],
                    date=row['date'],
                    logged_by=row['logged_by'],
                    unit_cost=float(row.get('unit_cost', 0.0))
                )
                entries.append(entry)
    except FileNotFoundError:
        pass
    return entries

def add_waste_entry(entry: WasteEntry):
    """Add a new waste log entry"""
    with open(WASTE_LOG_FILE, 'a', newline='') as file:
        fieldnames = ['item_name', 'quantity', 'unit', 'reason', 'date', 'logged_by', 'unit_cost']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(entry.to_dict())

def get_low_stock_items() -> List[InventoryItem]:
    """Get all items that are below par level"""
    items = read_inventory()
    return [item for item in items if item.is_low_stock()]

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
                    email=row.get('email', '')
                )
                vendors.append(vendor)
    except FileNotFoundError:
        pass
    return vendors

def write_vendors(vendors: List[Vendor]):
    """Write vendors to CSV file"""
    with open(VENDORS_FILE, 'w', newline='') as file:
        fieldnames = ['name', 'contact_info', 'address', 'phone', 'email']
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

# Recipe management functions
def read_recipes() -> List[Recipe]:
    """Read recipes from CSV file"""
    recipes = []
    try:
        with open(RECIPES_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipe = Recipe(
                    name=row['name'],
                    ingredients=row['ingredients'],
                    meat_type=row.get('meat_type', ''),
                    meat_pounds=float(row.get('meat_pounds', 0.0)),
                    servings=int(row.get('servings', 1)),
                    description=row.get('description', '')
                )
                recipes.append(recipe)
    except FileNotFoundError:
        pass
    return recipes

def write_recipes(recipes: List[Recipe]):
    """Write recipes to CSV file"""
    with open(RECIPES_FILE, 'w', newline='') as file:
        fieldnames = ['name', 'ingredients', 'meat_type', 'meat_pounds', 'servings', 'description']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for recipe in recipes:
            writer.writerow(recipe.to_dict())

def get_recipe(name: str) -> Optional[Recipe]:
    """Get a specific recipe by name"""
    recipes = read_recipes()
    for recipe in recipes:
        if recipe.name == name:
            return recipe
    return None

def add_recipe(recipe: Recipe) -> bool:
    """Add a new recipe"""
    recipes = read_recipes()
    # Check if recipe already exists
    if any(r.name == recipe.name for r in recipes):
        return False
    recipes.append(recipe)
    write_recipes(recipes)
    return True

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
    """Get items that need to be restocked (low stock items)"""
    return filter_inventory(low_stock_only=True)

def get_recipes_using_low_stock_items() -> List[Recipe]:
    """Get recipes that use low stock ingredients"""
    low_stock_items = get_shopping_list_items()
    low_stock_names = [item.name.lower() for item in low_stock_items]
    
    recipes = read_recipes()
    matching_recipes = []
    
    for recipe in recipes:
        # Simple check if any low stock item is mentioned in ingredients
        ingredients_lower = recipe.ingredients.lower()
        if any(item_name in ingredients_lower for item_name in low_stock_names):
            matching_recipes.append(recipe)
    
    return matching_recipes

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
        # Group items by vendor
        vendor_groups = {}
        for item in low_stock_items:
            vendors = item.get_vendors() if item.get_vendors() else ['No Vendor Assigned']
            for vendor in vendors:
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

def generate_meal_plan_pdf() -> bytes:
    """Generate meal plan PDF for recipes using low stock ingredients"""
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
    story.append(Paragraph("Health Pack Meals - Meal Plan", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Get recipes using low stock items
    recipes = get_recipes_using_low_stock_items()
    low_stock_items = get_shopping_list_items()
    
    if not recipes:
        story.append(Paragraph("No meal recipes found using low stock ingredients.", styles['Normal']))
    else:
        story.append(Paragraph("Recommended Meals Using Low Stock Ingredients:", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Create table
        table_data = [['Meal Name', 'Meat Type', 'Meat Required (lbs)', 'Servings', 'Description']]
        
        for recipe in recipes:
            table_data.append([
                recipe.name,
                recipe.meat_type.title() if recipe.meat_type else 'N/A',
                str(recipe.meat_pounds),
                str(recipe.servings),
                recipe.description[:50] + '...' if len(recipe.description) > 50 else recipe.description
            ])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 0.8*inch, 2.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Add low stock items summary
        story.append(Paragraph("Low Stock Items Summary:", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for item in low_stock_items:
            story.append(Paragraph(f"• {item.name}: {item.quantity} {item.unit} (Par Level: {item.par_level})", styles['Normal']))
    
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
