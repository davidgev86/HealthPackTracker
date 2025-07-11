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
    last_updated: str = ''
    
    def is_low_stock(self) -> bool:
        """Check if item is below par level"""
        return self.quantity < self.par_level
    
    def total_value(self) -> float:
        """Calculate total value of current stock"""
        return self.quantity * self.unit_cost
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return {
            'name': self.name,
            'unit': self.unit,
            'quantity': self.quantity,
            'par_level': self.par_level,
            'category': self.category,
            'unit_cost': self.unit_cost,
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
