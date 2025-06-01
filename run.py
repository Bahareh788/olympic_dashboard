#!/usr/bin/env python3
"""
Olympic Dashboard - Run Script
Simple script to start the Flask application with proper configuration
"""

import os
import sys
from app import app, db

def main():
    """Main function to run the Flask application"""
    
    print("🏅 Starting Olympic Dashboard...")
    print("=" * 50)
    
    # Display database connection info
    print("🗄️  Database Configuration:")
    print("   ➤ Database: Olympicdb")
    print("   ➤ Host: localhost:5432")
    print("   ➤ User: postgres")
    print()
    
    # Display startup information
    print("🌐 Dashboard will be available at:")
    print("   ➤ http://localhost:5000")
    print()
    print("📊 Available Dashboards:")
    print("   ➤ Strategic:    http://localhost:5000/strategic")
    print("   ➤ Operational:  http://localhost:5000/operational") 
    print("   ➤ Analytical:   http://localhost:5000/analytical")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    print()
    
    try:
        # Test database connection
        with app.app_context():
            result = db.session.execute('SELECT 1')
            result.close()
        print("✅ Database connection successful!")
        print()
        
        # Run the Flask application
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("📖 Please check your database configuration and ensure PostgreSQL is running.")
        print("🔧 Make sure the database 'Olympicdb' exists and contains the Olympic data.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Olympic Dashboard stopped.")
        print("Thank you for using the Olympic Dashboard! 🏅")
        sys.exit(0)

if __name__ == '__main__':
    main() 