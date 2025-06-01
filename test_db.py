import psycopg2

# Database connection
try:
    conn = psycopg2.connect(
        host="localhost",
        database="Olympicdb",
        user="postgres",
        password="Bahardb1234"
    )
    cursor = conn.cursor()
    
    print("✅ Database connection successful!")
    
    # Check if tables exist
    tables_to_check = ['olympicgames', 'athlete', 'country', 'sport', 'event', 'participation', 'medal', 'team']
    
    for table in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ Table '{table}': {count} rows")
        except Exception as e:
            print(f"❌ Table '{table}': Error - {e}")
    
    # Test specific queries from the app
    print("\n--- Testing app queries ---")
    
    try:
        cursor.execute("SELECT DISTINCT year FROM olympicgames ORDER BY year DESC LIMIT 5")
        years = cursor.fetchall()
        print(f"✅ Years query: Found {len(years)} years: {[y[0] for y in years]}")
    except Exception as e:
        print(f"❌ Years query error: {e}")
    
    try:
        cursor.execute("SELECT DISTINCT countryname FROM country ORDER BY countryname LIMIT 5")
        countries = cursor.fetchall()
        print(f"✅ Countries query: Found {len(countries)} countries: {[c[0] for c in countries]}")
    except Exception as e:
        print(f"❌ Countries query error: {e}")
    
    try:
        cursor.execute("SELECT DISTINCT sportname FROM sport ORDER BY sportname LIMIT 5")
        sports = cursor.fetchall()
        print(f"✅ Sports query: Found {len(sports)} sports: {[s[0] for s in sports]}")
    except Exception as e:
        print(f"❌ Sports query error: {e}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}") 