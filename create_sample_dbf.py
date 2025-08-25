#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sample DBF Creator for EDVAN DBF Commander

This script creates sample DBF files for testing the application.
Run this script to create test files before running the main application.
"""

import os
from datetime import datetime, date

try:
    import dbf
except ImportError:
    print("Error: dbf library not installed.")
    print("Please install it with: pip install dbf")
    exit(1)


def create_employees_dbf():
    """Create a sample employees DBF file"""
    
    # Define the table structure
    table = dbf.Table(
        'sample_employees.dbf',
        'emp_id N(6,0); name C(30); department C(20); salary N(10,2); hire_date D; active L'
    )
    
    # Open the table for writing
    table.open(mode=dbf.READ_WRITE)
    
    # Sample data
    employees = [
        (1, 'John Smith', 'Engineering', 75000.00, date(2020, 1, 15), True),
        (2, 'Sarah Johnson', 'Marketing', 65000.50, date(2019, 6, 10), True),
        (3, 'Michael Brown', 'Engineering', 82000.00, date(2018, 3, 22), True),
        (4, 'Emily Davis', 'HR', 58000.75, date(2021, 9, 5), True),
        (5, 'Robert Wilson', 'Finance', 70000.00, date(2017, 12, 1), True),
        (6, 'Lisa Anderson', 'Marketing', 67000.25, date(2020, 8, 18), False),
        (7, 'David Taylor', 'Engineering', 79000.00, date(2019, 2, 14), True),
        (8, 'Jennifer White', 'HR', 62000.00, date(2022, 4, 7), True),
        (9, 'Christopher Lee', 'Finance', 71500.50, date(2018, 11, 30), True),
        (10, 'Amanda Martinez', 'Engineering', 83000.00, date(2017, 5, 25), True),
        (11, 'James Garcia', 'Marketing', 66000.00, date(2021, 1, 12), True),
        (12, 'Michelle Rodriguez', 'Engineering', 77000.75, date(2020, 7, 3), True),
        (13, 'Thomas Hernandez', 'Finance', 69000.00, date(2019, 10, 8), False),
        (14, 'Jessica Lopez', 'HR', 61000.25, date(2021, 3, 20), True),
        (15, 'Daniel Gonzalez', 'Marketing', 68000.50, date(2018, 8, 16), True),
    ]
    
    # Add records to the table
    for emp_data in employees:
        table.append(emp_data)
    
    # Close the table
    table.close()
    
    print(f"Created sample_employees.dbf with {len(employees)} records")


def create_products_dbf():
    """Create a sample products DBF file"""
    
    # Define the table structure
    table = dbf.Table(
        'sample_products.dbf',
        'prod_id C(10); prod_name C(50); category C(20); price N(8,2); in_stock N(6,0); descrip M'
    )
    
    # Open the table for writing
    table.open(mode=dbf.READ_WRITE)
    
    # Sample data
    products = [
        ('LAPTOP001', 'Dell XPS 13 Laptop', 'Electronics', 1299.99, 25, 'High-performance ultrabook with 11th Gen Intel Core processor'),
        ('PHONE001', 'iPhone 14 Pro', 'Electronics', 999.00, 50, 'Latest iPhone with Pro camera system and A16 Bionic chip'),
        ('DESK001', 'Ergonomic Office Desk', 'Furniture', 299.95, 15, 'Height-adjustable standing desk with spacious work surface'),
        ('CHAIR001', 'Herman Miller Aeron Chair', 'Furniture', 1395.00, 8, 'Premium ergonomic office chair with lumbar support'),
        ('BOOK001', 'Python Programming Guide', 'Books', 49.99, 100, 'Comprehensive guide to Python programming for beginners'),
        ('MONITOR01', 'LG 27 4K Monitor', 'Electronics', 399.99, 30, '27-inch 4K UHD monitor with HDR support'),
        ('KEYBOARD1', 'Mechanical Gaming Keyboard', 'Electronics', 129.99, 45, 'RGB backlit mechanical keyboard with Cherry MX switches'),
        ('MOUSE001', 'Wireless Gaming Mouse', 'Electronics', 79.99, 60, 'High-precision wireless gaming mouse with RGB lighting'),
        ('TABLE001', 'Coffee Table', 'Furniture', 199.99, 12, 'Modern glass-top coffee table with metal legs'),
        ('LAMP001', 'LED Desk Lamp', 'Furniture', 59.99, 75, 'Adjustable LED desk lamp with USB charging port'),
        ('HEADSET01', 'Noise-Canceling Headphones', 'Electronics', 249.99, 20, 'Premium over-ear headphones with active noise cancellation'),
        ('TABLET01', 'iPad Air', 'Electronics', 599.00, 35, '10.9-inch iPad Air with M1 chip and all-day battery life'),
        ('PRINTER1', 'All-in-One Printer', 'Electronics', 149.99, 18, 'Wireless all-in-one inkjet printer with scanner and copier'),
        ('STORAGE1', '1TB External SSD', 'Electronics', 89.99, 40, 'Portable 1TB external SSD with USB-C connectivity'),
        ('WEBCAM01', '4K Webcam', 'Electronics', 199.99, 22, '4K webcam with auto-focus and built-in microphone'),
    ]
    
    # Add records to the table
    for prod_data in products:
        table.append(prod_data)
    
    # Close the table
    table.close()
    
    print(f"Created sample_products.dbf with {len(products)} records")


def create_sales_dbf():
    """Create a sample sales transactions DBF file"""
    
    # Define the table structure
    table = dbf.Table(
        'sample_sales.dbf',
        'sale_id N(8,0); customer C(40); prod_id C(10); quantity N(4,0); unit_price N(8,2); sale_date D; total_amt N(10,2)'
    )
    
    # Open the table for writing
    table.open(mode=dbf.READ_WRITE)
    
    # Sample data
    sales = [
        (1001, 'Alice Johnson', 'LAPTOP001', 1, 1299.99, date(2024, 1, 15), 1299.99),
        (1002, 'Bob Smith', 'PHONE001', 2, 999.00, date(2024, 1, 16), 1998.00),
        (1003, 'Carol Davis', 'DESK001', 1, 299.95, date(2024, 1, 17), 299.95),
        (1004, 'David Wilson', 'CHAIR001', 1, 1395.00, date(2024, 1, 18), 1395.00),
        (1005, 'Eva Martinez', 'BOOK001', 3, 49.99, date(2024, 1, 19), 149.97),
        (1006, 'Frank Brown', 'MONITOR01', 2, 399.99, date(2024, 1, 20), 799.98),
        (1007, 'Grace Lee', 'KEYBOARD1', 1, 129.99, date(2024, 1, 21), 129.99),
        (1008, 'Henry Garcia', 'MOUSE001', 2, 79.99, date(2024, 1, 22), 159.98),
        (1009, 'Iris Rodriguez', 'TABLE001', 1, 199.99, date(2024, 1, 23), 199.99),
        (1010, 'Jack Hernandez', 'LAMP001', 3, 59.99, date(2024, 1, 24), 179.97),
        (1011, 'Kelly Lopez', 'HEADSET01', 1, 249.99, date(2024, 1, 25), 249.99),
        (1012, 'Luis Gonzalez', 'TABLET01', 1, 599.00, date(2024, 1, 26), 599.00),
        (1013, 'Maria Perez', 'PRINTER1', 1, 149.99, date(2024, 1, 27), 149.99),
        (1014, 'Nathan Torres', 'STORAGE1', 2, 89.99, date(2024, 1, 28), 179.98),
        (1015, 'Olivia Rivera', 'WEBCAM01', 1, 199.99, date(2024, 1, 29), 199.99),
        (1016, 'Paul Cooper', 'LAPTOP001', 1, 1299.99, date(2024, 1, 30), 1299.99),
        (1017, 'Quinn Murphy', 'PHONE001', 1, 999.00, date(2024, 1, 31), 999.00),
        (1018, 'Rachel Ward', 'DESK001', 2, 299.95, date(2024, 2, 1), 599.90),
        (1019, 'Steve Bailey', 'KEYBOARD1', 2, 129.99, date(2024, 2, 2), 259.98),
        (1020, 'Tina Foster', 'MOUSE001', 1, 79.99, date(2024, 2, 3), 79.99),
    ]
    
    # Add records to the table
    for sale_data in sales:
        table.append(sale_data)
    
    # Close the table
    table.close()
    
    print(f"Created sample_sales.dbf with {len(sales)} records")


def main():
    """Create all sample DBF files"""
    
    print("Creating sample DBF files for EDVAN DBF Commander...")
    print("=" * 50)
    
    try:
        create_employees_dbf()
        create_products_dbf()
        create_sales_dbf()
        
        print("=" * 50)
        print("✅ All sample DBF files created successfully!")
        print("\nFiles created:")
        print("- sample_employees.dbf (Employee data)")
        print("- sample_products.dbf (Product catalog)")
        print("- sample_sales.dbf (Sales transactions)")
        print("\nYou can now open these files in EDVAN DBF Commander to test the application.")
        
    except Exception as e:
        print(f"❌ Error creating sample files: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
