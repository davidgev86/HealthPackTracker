# HPM Inventory - Quick Reference Guide

## For Staff (Daily Use)

### Google Sheets Update Process
1. **Open** the shared "HPM Inventory Data" Google Sheet
2. **Find** your assigned items or all items
3. **Update** the "quantity" column with actual counts
4. **Enter** today's date in "last_updated" column
5. **Save** automatically happens in Google Sheets

### Important Rules
- ✅ Only update quantity and last_updated columns
- ❌ Never change item names, units, or par levels
- ❌ Don't delete rows
- ❌ Don't add new items without manager approval

---

## For Managers (Weekly Use)

### Data Import Process
1. **Export from Google Sheets**
   - File → Download → CSV
   - Save as "inventory_YYYY_MM_DD.csv"

2. **Import to HPM Tracker**
   - Login to HPM Inventory Tracker
   - Go to Import/Export page
   - Select your CSV file
   - Click "Import Data"
   - Verify success message

3. **Verify Import**
   - Check inventory page
   - Look for low stock alerts
   - Export backup CSV

### Weekly Checklist
- [ ] Monday: Review low stock items
- [ ] Wednesday: Check Google Sheet for accuracy
- [ ] Friday: Import data to HPM Tracker
- [ ] Saturday: Generate reports and backup

---

## Troubleshooting

### Google Sheets Issues
- **Can't edit**: Check if you're signed into the correct Google account
- **Changes not saving**: Refresh the page and try again
- **Sheet not loading**: Check internet connection

### Import Issues
- **"Missing field" error**: Check that all required columns exist
- **"Invalid format" error**: Make sure quantities are numbers only
- **"Import failed"**: Contact IT support with error message

### Emergency Contacts
- System Admin: [Your contact info]
- IT Support: [Your contact info]
- Manager: [Your contact info]

---

## CSV Template Structure

```
name,unit,quantity,par_level,category,last_updated
Item Name,measurement,number,number,category,YYYY-MM-DD HH:MM:SS
```

### Valid Units
pieces, kg, lbs, oz, liters, gallons, cups, boxes, bags, cans

### Valid Categories
General, Proteins, Vegetables, Grains, Dairy, Spices, Beverages, Packaging, Cleaning

---

*Keep this guide handy for quick reference during daily operations*