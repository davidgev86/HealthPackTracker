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
    quantity: int
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
    
    def quantity_needed(self) -> int:
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
    quantity: int
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
class Vendor:
    name: str
    contact_info: str = ''
    address: str = ''
    phone: str = ''
    email: str = ''
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'name': self.name,
            'contact_info': self.contact_info,
            'address': self.address,
            'phone': self.phone,
            'email': self.email
        }

@dataclass
class Recipe:
    name: str
    ingredients: str  # JSON string of ingredient requirements
    meat_type: str = ''  # beef, chicken, turkey, seafood
    meat_pounds: float = 0.0  # pounds of meat required
    servings: int = 1
    description: str = ''
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'name': self.name,
            'ingredients': self.ingredients,
            'meat_type': self.meat_type,
            'meat_pounds': self.meat_pounds,
            'servings': self.servings,
            'description': self.description
        }

# Category constants
CATEGORIES = [
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

# Default vendors
DEFAULT_VENDORS = [
    'Sams Club',
    'Costco',
    'Restaurant Depot',
    'Webrestaurant',
    'Keany Produce',
    'H-mart'
]
