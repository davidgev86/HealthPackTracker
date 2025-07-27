"""
Data models for the HPM Inventory application.
Since we're using CSV storage, these are simple data classes.
"""
from dataclasses import dataclass
from typing import List, Optional
import csv
import os

@dataclass
class User:
    username: str
    password_hash: str
    role: str  # 'admin', 'manager', 'staff'
    email: str = ''
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission based on role"""
        permissions = {
            'admin': ['view', 'edit', 'delete', 'import', 'export', 'manage_users'],
            'manager': ['view', 'edit', 'import', 'export', 'approve_orders'],
            'staff': ['view', 'record_counts', 'log_waste']
        }
        return permission in permissions.get(self.role, [])

@dataclass
class InventoryItem:
    name: str
    unit: str
    quantity: float
    par_level: int
    category: str = 'General'
    unit_cost: float = 0.0  # Cost per unit
    vendors: str = ''  # Comma-separated vendor names
    last_updated: str = ''
    
    def is_low_stock(self) -> bool:
        """Check if item is below par level"""
        return self.quantity <= self.par_level
    
    def total_value(self) -> float:
        """Calculate total value of current stock"""
        return self.quantity * self.unit_cost
    
    def get_vendors(self) -> List[str]:
        """Get list of vendors for this item"""
        return [v.strip() for v in self.vendors.split(',') if v.strip()]
    
    def quantity_needed(self) -> float:
        """Calculate quantity needed to reach par level"""
        return max(0, self.par_level - self.quantity)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'name': self.name,
            'unit': self.unit,
            'quantity': self.quantity,
            'par_level': self.par_level,
            'category': self.category,
            'unit_cost': self.unit_cost,
            'vendors': self.vendors,
            'last_updated': self.last_updated
        }

@dataclass
class WasteEntry:
    item_name: str
    quantity: float
    unit: str
    reason: str
    date: str
    logged_by: str
    unit_cost: float = 0.0  # Cost per unit at time of waste
    
    def waste_value(self) -> float:
        """Calculate total value of wasted items"""
        return self.quantity * self.unit_cost
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'item_name': self.item_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'reason': self.reason,
            'date': self.date,
            'logged_by': self.logged_by,
            'unit_cost': self.unit_cost
        }

@dataclass
class WeeklyWasteReport:
    week_start: str
    week_end: str
    total_entries: int
    total_value: float
    by_category: dict  # category -> total_value
    by_reason: dict    # reason -> total_value
    by_item: dict      # item_name -> total_value
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'week_start': self.week_start,
            'week_end': self.week_end,
            'total_entries': self.total_entries,
            'total_value': self.total_value,
            'by_category': str(self.by_category),
            'by_reason': str(self.by_reason),
            'by_item': str(self.by_item)
        }

@dataclass
class WeeklyInventoryReport:
    week_start: str
    week_end: str
    total_items: int
    total_value: float
    by_category: dict  # category -> total_value
    by_vendor: dict    # vendor -> total_value
    low_stock_items: int
    generated_date: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'week_start': self.week_start,
            'week_end': self.week_end,
            'total_items': self.total_items,
            'total_value': self.total_value,
            'by_category': str(self.by_category),
            'by_vendor': str(self.by_vendor),
            'low_stock_items': self.low_stock_items,
            'generated_date': self.generated_date
        }

@dataclass
class Vendor:
    name: str
    contact_info: str = ''
    address: str = ''
    phone: str = ''
    email: str = ''
    exclude_from_shopping_list: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'name': self.name,
            'contact_info': self.contact_info,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'exclude_from_shopping_list': str(self.exclude_from_shopping_list)
        }



# Category constants
DEFAULT_CATEGORIES = [
    'General',
    'Produce',
    'Meat & Poultry',
    'Dairy',
    'Pantry',
    'Beverages',
    'Frozen',
    'Cleaning Supplies',
    'Frozen Bulk Items',
    'Frozen Beef Meals',
    'Frozen Chicken Meals',
    'Frozen Turkey Meals',
    'Frozen Seafood'
]

@dataclass
class Category:
    name: str
    description: str = ''
    created_date: str = ''
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date
        }

# Default vendors
DEFAULT_VENDORS = [
    'Sams Club',
    'Costco',
    'Restaurant Depot',
    'Webrestaurant',
    'Keany Produce',
    'H-mart'
]

@dataclass
class HPMWeeklyReport:
    date: str
    total_items: int
    total_value: float
    low_stock_count: int
    total_waste_value: float
    top_waste_categories: str
    comparison_notes: str = ''
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'date': self.date,
            'total_items': str(self.total_items),
            'total_value': str(self.total_value),
            'low_stock_count': str(self.low_stock_count),
            'total_waste_value': str(self.total_waste_value),
            'top_waste_categories': self.top_waste_categories,
            'comparison_notes': self.comparison_notes
        }
