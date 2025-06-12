#!/usr/bin/env python3
"""
Olympic Operational Dashboard Database Setup Script
This script creates the operational tables and inserts fake data for the dashboard.
"""

import psycopg2
from psycopg2 import sql
import sys

# Database configuration (update these to match your setup)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'Olympicdb',
    'user': 'postgres',
    'password': 'Bahardb1234',
    'port': 5432
}

def read_sql_file(filename):
    """Read SQL commands from file"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: SQL file '{filename}' not found!")
        return None

def execute_sql_script(sql_content):
    """Execute SQL script"""
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Executing SQL script...")
        
        # Split the SQL content by statements (simple approach)
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement.upper().startswith('COMMIT'):
                continue
                
            try:
                print(f"Executing statement {i+1}/{len(statements)}...")
                cursor.execute(statement)
                print(f"✓ Statement {i+1} executed successfully")
            except Exception as e:
                print(f"✗ Error in statement {i+1}: {e}")
                print(f"Statement was: {statement[:100]}...")
                continue
        
        print("\n✓ Database setup completed successfully!")
        
        # Verify the data was inserted
        print("\nVerifying data insertion...")
        
        verification_queries = [
            ("Venues", "SELECT COUNT(*) FROM operational_venues"),
            ("Staff", "SELECT COUNT(*) FROM operational_staff"),
            ("Transport", "SELECT COUNT(*) FROM operational_transport"),
            ("Schedule", "SELECT COUNT(*) FROM operational_schedule"),
            ("Resources", "SELECT COUNT(*) FROM operational_resources"),
            ("Status", "SELECT COUNT(*) FROM operational_status"),
            ("Alerts", "SELECT COUNT(*) FROM operational_alerts"),
            ("Intelligence", "SELECT COUNT(*) FROM operational_intelligence")
        ]
        
        for table_name, query in verification_queries:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"✓ {table_name}: {count} records inserted")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Operational dashboard database setup complete!")
        print("You can now run your Flask app and the operational dashboard will use database data.")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("Olympic Operational Dashboard Database Setup")
    print("=" * 50)
    
    # Read SQL file
    sql_content = read_sql_file('create_operational_tables.sql')
    if not sql_content:
        sys.exit(1)
    
    # Execute SQL script
    success = execute_sql_script(sql_content)
    
    if success:
        print("\nNext steps:")
        print("1. Start your Flask app: python app.py")
        print("2. Navigate to: http://localhost:5000/operational")
        print("3. The dashboard will now load data from your database!")
    else:
        print("\nSetup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 