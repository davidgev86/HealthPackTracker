# HPM Inventory Tracker - Data Management Workflow

## Overview

This workflow enables Health Pack Meals staff to collaborate on inventory management using Google Sheets for data entry and the HPM Inventory Tracker application for centralized management.

## Workflow Steps

### Phase 1: Google Sheets Setup (Owner/Manager)

1. **Create Master Google Sheet**
   - Create a new Google Sheet named "HPM Inventory Data"
   - Set up the following columns in the exact order:
     ```
     name | unit | quantity | par_level | category | last_updated
     ```

2. **Share with Team**
   - Share the Google Sheet with inventory staff
   - Set permissions:
     - Staff: Can edit (for quantity updates)
     - Managers: Can edit (for all fields)
     - Owner: Owner access

3. **Set Up Data Validation** (Optional but recommended)
   - **Unit column**: Create dropdown with: pieces, kg, lbs, oz, liters, gallons, cups, boxes, bags, cans
   - **Category column**: Create dropdown with: General, Proteins, Vegetables, Grains, Dairy, Spices, Beverages, Packaging, Cleaning

### Phase 2: Staff Data Entry (Workers)

1. **Daily Inventory Counts**
   - Open the shared Google Sheet
   - Update the "quantity" column with actual counts
   - Update "last_updated" column with current date/time
   - Do NOT modify item names, units, or par levels (unless authorized)

2. **Adding New Items** (Manager approval required)
   - Add new row at the bottom of the sheet
   - Fill in all required fields:
     - **name**: Item description
     - **unit**: Measurement unit
     - **quantity**: Current stock
     - **par_level**: Minimum stock level
     - **category**: Item category
     - **last_updated**: Current date/time

3. **Best Practices for Staff**
   - Always use consistent naming (e.g., "Chicken Breast" not "chicken breast")
   - Double-check quantities before submitting
   - Leave notes in a separate "Notes" column if needed
   - Report any discrepancies to management immediately

### Phase 3: Data Import (Owner/Manager)

1. **Export from Google Sheets**
   - Open the Google Sheet
   - Go to File → Download → Comma Separated Values (.csv)
   - Save the file with a descriptive name (e.g., "inventory_2025_01_15.csv")

2. **Import to HPM Inventory Tracker**
   - Login to the HPM Inventory Tracker application
   - Navigate to "Import/Export" page
   - Click "Select CSV File" and choose your downloaded file
   - Review the preview if available
   - Click "Import Data"
   - Verify the import was successful

3. **Verification Steps**
   - Check the inventory page for new/updated items
   - Verify quantities match the Google Sheet
   - Look for any low stock alerts
   - Generate a backup using the "Export to CSV" feature

## Google Sheets Template

### Column Definitions

| Column | Description | Example | Required |
|--------|-------------|---------|----------|
| name | Item name | Chicken Breast | Yes |
| unit | Measurement unit | lbs | Yes |
| quantity | Current stock | 25 | Yes |
| par_level | Minimum stock level | 10 | Yes |
| category | Item category | Proteins | Optional |
| last_updated | Last modification date | 2025-01-15 14:30:00 | Optional |

### Sample Template

```csv
name,unit,quantity,par_level,category,last_updated
Chicken Breast,lbs,25,10,Proteins,2025-01-15 14:30:00
Ground Beef,lbs,18,15,Proteins,2025-01-15 14:30:00
Rice,kg,12,20,Grains,2025-01-15 14:30:00
Broccoli,lbs,8,5,Vegetables,2025-01-15 14:30:00
Olive Oil,liters,4,3,General,2025-01-15 14:30:00
```

## Recommended Schedule

### Daily Tasks (Staff)
- **Morning**: Update quantities from previous day's service
- **Evening**: Final count after service, update any waste

### Weekly Tasks (Manager)
- **Monday**: Review low stock items and plan orders
- **Wednesday**: Mid-week quantity verification
- **Friday**: Export and import data to main system
- **Saturday**: Generate reports and backup data

### Monthly Tasks (Owner)
- **Month-end**: Complete data backup
- **Review**: Analyze waste patterns and par level adjustments
- **Update**: Modify categories or add new items as needed

## Troubleshooting

### Common Import Issues

1. **"Missing required field" error**
   - Ensure all required columns exist: name, unit, quantity, par_level
   - Check column spelling and capitalization

2. **"Invalid data format" error**
   - Verify quantity and par_level are numbers (no text)
   - Remove any special characters from item names

3. **"Number of values doesn't match header" error**
   - Check for extra commas in item names
   - Ensure each row has the same number of columns

### Google Sheets Issues

1. **Staff can't edit quantities**
   - Check sharing permissions
   - Verify the correct email addresses were invited

2. **Data validation not working**
   - Reapply data validation rules
   - Check if dropdown lists are properly configured

3. **Formulas breaking**
   - Avoid using formulas in data columns
   - Keep calculations in separate columns or sheets

## Security Best Practices

### Google Sheets Security
- Use company Google Workspace accounts only
- Regularly review who has access
- Enable activity notifications
- Don't share edit links publicly

### Application Security
- Change default admin password immediately
- Create separate accounts for each manager
- Regularly backup data
- Use strong passwords for all accounts

## Integration Tips

### Efficient Data Flow
1. **Batch Updates**: Import data weekly rather than daily to reduce workload
2. **Version Control**: Keep dated copies of CSV files
3. **Validation**: Always verify critical items after import
4. **Backup Strategy**: Export from application monthly for redundancy

### Communication Protocol
1. **Notify team** before major imports
2. **Document changes** in a shared log
3. **Report issues** immediately to prevent data loss
4. **Schedule downtime** for major updates if needed

## Advanced Features

### Conditional Formatting in Google Sheets
- Highlight cells where quantity < par_level (red background)
- Use color coding for different categories
- Add progress bars for stock levels

### Automated Reminders
- Set up Google Sheets notifications for low stock
- Create calendar reminders for import schedules
- Use email alerts for critical inventory levels

## Support and Training

### Staff Training Checklist
- [ ] Google Sheets basic navigation
- [ ] Data entry procedures
- [ ] Understanding units and categories
- [ ] Error reporting process
- [ ] Backup procedures

### Manager Training Checklist
- [ ] Google Sheets advanced features
- [ ] CSV export procedures
- [ ] Import process in HPM Tracker
- [ ] Error resolution
- [ ] Report generation
- [ ] User management

## Appendix

### Quick Reference Card (Print and Post)

**Daily Staff Tasks:**
1. Open HPM Inventory Google Sheet
2. Update quantity column with actual counts
3. Update last_updated with current date/time
4. Report any issues to manager

**Weekly Manager Tasks:**
1. Review Google Sheet for accuracy
2. Export as CSV file
3. Import to HPM Inventory Tracker
4. Verify import success
5. Generate backup

**Emergency Contacts:**
- IT Support: [Contact Information]
- System Administrator: [Contact Information]
- Google Workspace Admin: [Contact Information]

---

*This workflow guide should be reviewed and updated quarterly to ensure optimal efficiency and accuracy.*