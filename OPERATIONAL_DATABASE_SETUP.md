# Olympic Operational Dashboard Database Setup

This guide explains how to set up the operational database tables and insert fake data for your Olympic operational dashboard.

## Overview

The operational dashboard now uses **real database tables** instead of hardcoded JavaScript data. This makes it more realistic and allows your lecturer to see that the data is properly stored and retrieved from the database.

## Database Tables Created

The setup creates 8 new tables with realistic operational data:

1. **`operational_venues`** - Venue capacity and status data
2. **`operational_staff`** - Staff deployment by department
3. **`operational_transport`** - Transportation flow and performance
4. **`operational_schedule`** - Event schedule performance by day
5. **`operational_resources`** - Resource utilization percentages
6. **`operational_status`** - System status metrics
7. **`operational_alerts`** - Priority alerts and incidents
8. **`operational_intelligence`** - AI-powered operational insights

## Setup Instructions

### Method 1: Using the Python Setup Script (Recommended)

1. **Run the setup script:**
   ```bash
   python setup_operational_db.py
   ```

2. **The script will:**
   - Create all 8 operational tables
   - Insert realistic fake data
   - Verify the data was inserted correctly
   - Show you a summary of records created

### Method 2: Manual SQL Execution

1. **Connect to your PostgreSQL database:**
   ```bash
   psql -h localhost -U postgres -d Olympicdb
   ```

2. **Run the SQL script:**
   ```sql
   \i create_operational_tables.sql
   ```

## Fake Data Included

### Venues (8 venues)
- Olympic Stadium: 95% capacity (76,000/80,000)
- Aquatics Center: 87% capacity (13,050/15,000)
- Gymnastics Arena: 92% capacity (11,040/12,000)
- Basketball Arena: 78% capacity (14,040/18,000)
- Tennis Courts: 65% capacity (6,500/10,000)
- Cycling Velodrome: 88% capacity (5,280/6,000)
- Wrestling Arena: 82% capacity (6,560/8,000)
- Boxing Arena: 91% capacity (8,190/9,000)

### Staff Deployment (7 departments)
- Security: 485 active / 520 total
- Medical: 127 active / 140 total
- Technical: 298 active / 320 total
- Volunteers: 1,247 active / 1,300 total
- Catering: 189 active / 200 total
- Transport: 156 active / 170 total
- Media: 345 active / 360 total

### Transportation (9 time slots)
- Hourly passenger counts from 06:00 to 22:00
- On-time performance ranging from 89% to 99%

### Schedule Performance (7 days)
- Daily event counts with on-time, minor delays, major delays
- Total of 247 events across the week

### Priority Alerts (3 active alerts)
- Aquatics Center: Pool temperature adjustment (Medium priority)
- Olympic Stadium: Security sweep completed (Resolved)
- Transport Hub: Increased passenger flow (Monitoring)

## How It Works

### Before (Hardcoded Data)
```javascript
// Old way - fake data in JavaScript
const venueData = {
    labels: ['Olympic Stadium', 'Aquatics Center', ...],
    datasets: [{
        data: [95, 87, 92, 78, ...]
    }]
};
```

### After (Database Data)
```javascript
// New way - data from database
fetch('/api/operational-data')
    .then(response => response.json())
    .then(data => {
        initializeVenueStatusChart(data.venues);
    });
```

## API Endpoints

The operational dashboard now uses these API endpoints:

- **`/api/operational-data`** - All operational chart data
- **`/api/operational-kpis`** - Real-time KPI metrics

## Verification

After setup, you can verify the data was inserted correctly:

```sql
-- Check venue data
SELECT venue_name, capacity, current_occupancy, 
       ROUND((current_occupancy::numeric/capacity::numeric)*100, 1) as capacity_percent
FROM operational_venues;

-- Check staff deployment
SELECT department, active_count, total_assigned 
FROM operational_staff 
ORDER BY active_count DESC;

-- Check alerts
SELECT venue_name, description, priority_level, status 
FROM operational_alerts;
```

## Benefits for Your Lecturer

1. **Real Database Integration**: Shows proper database design and usage
2. **Realistic Data**: Comprehensive fake data that represents real Olympic operations
3. **Professional Implementation**: Proper separation of data layer and presentation layer
4. **Scalable Architecture**: Easy to add more data or modify existing records

## Troubleshooting

### Connection Issues
- Verify your database credentials in `setup_operational_db.py`
- Ensure PostgreSQL is running
- Check that the database `Olympicdb` exists

### Permission Issues
- Make sure your PostgreSQL user has CREATE TABLE permissions
- Verify the user can INSERT data

### Data Not Showing
- Check the browser console for API errors
- Verify the Flask app is running on port 5000
- Test the API endpoints directly: `http://localhost:5000/api/operational-data`

## Next Steps

1. **Run the setup script**
2. **Start your Flask app**: `python app.py`
3. **Visit the operational dashboard**: `http://localhost:5000/operational`
4. **Show your lecturer**: The dashboard now uses real database data!

The operational dashboard will now load all data from your PostgreSQL database, making it a much more professional and realistic implementation for your project. 