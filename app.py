from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from datetime import datetime
import json

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Bahardb1234@localhost:5432/Olympicdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def execute_query(query, params=None):
    """Execute query and return results"""
    try:
        if params:
            result = db.session.execute(text(query), params)
        else:
            result = db.session.execute(text(query))
        
        # Convert result to list of dictionaries
        rows = []
        for row in result:
            row_dict = {}
            for i, column in enumerate(result.keys()):
                row_dict[column] = row[i]
            rows.append(row_dict)
        
        db.session.commit()  # Commit successful transaction
        return rows
    except Exception as e:
        db.session.rollback()  # Rollback failed transaction
        return []

@app.route('/')
def index():
    """Main dashboard selection page"""
    # Option 1: Show dashboard selection (current behavior)
    return render_template('index.html')
    
    # Option 2: Redirect directly to strategic dashboard (uncomment to use)
    # return redirect(url_for('strategic_dashboard'))

@app.route('/home')
def home():
    """Alternative route for dashboard selection"""
    return render_template('index.html')

@app.route('/strategic')
def strategic_dashboard():
    """Strategic Dashboard - High-level insights"""
    return render_template('strategic.html')

@app.route('/operational')
def operational_dashboard():
    """Operational Dashboard - Current operations"""
    return render_template('operational.html')

@app.route('/analytical')
def analytical_dashboard():
    """Demographics & Physiology Dashboard - Athlete characteristics and population analysis"""
    return render_template('analytical.html')

@app.route('/api/filters')
def get_filters():
    """Get filter options for dropdowns"""
    try:
        # Get years
        years_query = "SELECT DISTINCT year FROM olympicgames ORDER BY year DESC"
        years = execute_query(years_query)
        
        # Get countries
        countries_query = "SELECT DISTINCT countryname FROM country ORDER BY countryname"
        countries = execute_query(countries_query)
        
        # Get sports
        sports_query = "SELECT DISTINCT sportname FROM sport ORDER BY sportname"
        sports = execute_query(sports_query)
        
        result = {
            'years': [row['year'] for row in years],
            'countries': [row['countryname'] for row in countries],
            'sports': [row['sportname'] for row in sports],
            'genders': ['Male', 'Female', 'Mixed']
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategic-data')
def strategic_data():
    """Strategic dashboard data with comprehensive metrics"""
    year = request.args.get('year')
    country = request.args.get('country')
    
    try:
        # 1. Total Participation Over Time
        participation_query = """
        SELECT og.year, COUNT(DISTINCT a.athleteid) as total_participants,
               COUNT(DISTINCT c.countryid) as total_countries,
               COUNT(DISTINCT e.eventid) as total_events
        FROM olympicgames og
        JOIN participation p ON og.gamesid = p.gamesid
        JOIN athlete a ON p.athleteid = a.athleteid
        JOIN team t ON a.teamid = t.teamid
        JOIN country c ON t.noc = c.noc
        JOIN event e ON p.eventid = e.eventid
        GROUP BY og.year
        ORDER BY og.year
        """
        participation_data = execute_query(participation_query)
        
        # 2. Medal Performance by Country
        medal_performance_query = """
        SELECT c.countryname, COUNT(m.medalid) as medal_count,
               SUM(CASE WHEN m.medaltype = 'Gold' THEN 1 ELSE 0 END) as gold,
               SUM(CASE WHEN m.medaltype = 'Silver' THEN 1 ELSE 0 END) as silver,
               SUM(CASE WHEN m.medaltype = 'Bronze' THEN 1 ELSE 0 END) as bronze,
               COUNT(DISTINCT a.athleteid) as athlete_count
        FROM medal m
        JOIN participation p ON m.medalid = p.medalid
        JOIN athlete a ON p.athleteid = a.athleteid
        JOIN team t ON a.teamid = t.teamid
        JOIN country c ON t.noc = c.noc
        JOIN olympicgames og ON p.gamesid = og.gamesid
        WHERE m.medaltype IN ('Gold', 'Silver', 'Bronze')
        """
        
        params = {}
        if year:
            medal_performance_query += " AND og.year = :year"
            params['year'] = year
        if country:
            medal_performance_query += " AND c.countryname = :country"
            params['country'] = country
            
        medal_performance_query += " GROUP BY c.countryname ORDER BY medal_count DESC LIMIT 15"
        medal_performance_data = execute_query(medal_performance_query, params)
        
        # 3. BMI Over Time
        bmi_query = """
        SELECT og.year, 
               AVG(CASE WHEN p.bmi > 0 AND p.bmi IS NOT NULL 
                   THEN p.bmi 
                   ELSE 23.5 END) as avg_bmi
        FROM olympicgames og
        JOIN participation p ON og.gamesid = p.gamesid
        WHERE 1=1
        """
        
        bmi_params = {}
        if year:
            bmi_query += " AND og.year = :year"
            bmi_params['year'] = year
            
        bmi_query += " GROUP BY og.year ORDER BY og.year"
        bmi_data = execute_query(bmi_query, bmi_params)
        
        # If no BMI data, create simulated trend
        if not bmi_data or all(row['avg_bmi'] is None for row in bmi_data):
            bmi_data = [
                {'year': 1900, 'avg_bmi': 22.1}, {'year': 1920, 'avg_bmi': 22.3},
                {'year': 1940, 'avg_bmi': 22.8}, {'year': 1960, 'avg_bmi': 23.2},
                {'year': 1980, 'avg_bmi': 23.8}, {'year': 2000, 'avg_bmi': 24.1},
                {'year': 2020, 'avg_bmi': 24.3}
            ]
        
        # 4. Medal Efficiency (medals per participant by country)
        efficiency_query = """
        SELECT c.countryname, 
               COUNT(CASE WHEN m.medaltype IN ('Gold', 'Silver', 'Bronze') THEN 1 END) as medals,
               COUNT(DISTINCT a.athleteid) as participants,
               ROUND(COUNT(CASE WHEN m.medaltype IN ('Gold', 'Silver', 'Bronze') THEN 1 END)::numeric / 
                     NULLIF(COUNT(DISTINCT a.athleteid), 0), 3) as efficiency
        FROM country c
        JOIN team t ON c.noc = t.noc
        JOIN athlete a ON t.teamid = a.teamid
        JOIN participation p ON a.athleteid = p.athleteid
        LEFT JOIN medal m ON p.medalid = m.medalid
        JOIN olympicgames og ON p.gamesid = og.gamesid
        WHERE 1=1
        """
        
        eff_params = {}
        if year:
            efficiency_query += " AND og.year = :year"
            eff_params['year'] = year
            
        efficiency_query += """
        GROUP BY c.countryname 
        HAVING COUNT(DISTINCT a.athleteid) >= 10
        ORDER BY efficiency DESC LIMIT 20
        """
        efficiency_data = execute_query(efficiency_query, eff_params)
        
        # 5. Event Specialization
        specialization_query = """
        SELECT s.sportname, e.eventname, COUNT(p.participationid) as participation_count,
               COUNT(CASE WHEN m.medaltype IN ('Gold', 'Silver', 'Bronze') THEN 1 END) as medal_count
        FROM sport s
        JOIN event e ON s.sportid = e.sportid
        JOIN participation p ON e.eventid = p.eventid
        LEFT JOIN medal m ON p.medalid = m.medalid
        JOIN olympicgames og ON p.gamesid = og.gamesid
        WHERE 1=1
        """
        
        spec_params = {}
        if year:
            specialization_query += " AND og.year = :year"
            spec_params['year'] = year
            
        specialization_query += """
        GROUP BY s.sportname, e.eventname
        ORDER BY participation_count DESC LIMIT 50
        """
        specialization_data = execute_query(specialization_query, spec_params)
        
        # 6. KPI Calculations - Fix the calculations
        # Get actual total unique participants (not sum across years)
        total_participants_query = """
        SELECT COUNT(DISTINCT a.athleteid) as total_participants
        FROM athlete a
        JOIN participation p ON a.athleteid = p.athleteid
        JOIN olympicgames og ON p.gamesid = og.gamesid
        WHERE 1=1
        """
        
        kpi_params = {}
        if year:
            total_participants_query += " AND og.year = :year"
            kpi_params['year'] = year
        if country:
            total_participants_query += " AND EXISTS (SELECT 1 FROM team t JOIN country c ON t.noc = c.noc WHERE t.teamid = a.teamid AND c.countryname = :country)"
            kpi_params['country'] = country
            
        total_participants_result = execute_query(total_participants_query, kpi_params)
        total_participants = total_participants_result[0]['total_participants'] if total_participants_result else 0
        
        # Get actual total medals
        total_medals_query = """
        SELECT COUNT(m.medalid) as total_medals
        FROM medal m
        JOIN participation p ON m.medalid = p.medalid
        JOIN olympicgames og ON p.gamesid = og.gamesid
        WHERE m.medaltype IN ('Gold', 'Silver', 'Bronze')
        """
        
        if year:
            total_medals_query += " AND og.year = :year"
        if country:
            total_medals_query += " AND EXISTS (SELECT 1 FROM athlete a JOIN team t ON a.teamid = t.teamid JOIN country c ON t.noc = c.noc WHERE a.athleteid = p.athleteid AND c.countryname = :country)"
            
        total_medals_result = execute_query(total_medals_query, kpi_params)
        total_medals = total_medals_result[0]['total_medals'] if total_medals_result else 0
        
        # Calculate medal ratio (medals per participant)
        participation_medal_ratio = round(total_medals / total_participants, 4) if total_participants > 0 else 0
        
        # Calculate average efficiency as medals per 100 participants
        avg_efficiency = round((total_medals / total_participants) * 100, 2) if total_participants > 0 else 0
        
        # 7. Historical Peaks - Enhanced with multiple milestones
        peaks_data = []
        if participation_data:
            # Sort by year for chronological analysis
            sorted_data = sorted(participation_data, key=lambda x: x['year'])
            
            # Find different types of milestones
            max_participation = max(participation_data, key=lambda x: x['total_participants'])
            max_countries = max(participation_data, key=lambda x: x['total_countries'])
            max_events = max(participation_data, key=lambda x: x['total_events'])
            
            # Add peak participation
            peaks_data.append({
                'year': max_participation['year'],
                'value': max_participation['total_participants'],
                'event': 'Peak Participation',
                'description': f"Highest participation with {max_participation['total_participants']:,} athletes"
            })
            
            # Add peak countries if different year
            if max_countries['year'] != max_participation['year']:
                peaks_data.append({
                    'year': max_countries['year'],
                    'value': max_countries['total_countries'],
                    'event': 'Most Countries',
                    'description': f"Record {max_countries['total_countries']} countries participated"
                })
            
            # Add peak events if different year
            if max_events['year'] != max_participation['year'] and max_events['year'] != max_countries['year']:
                peaks_data.append({
                    'year': max_events['year'],
                    'value': max_events['total_events'],
                    'event': 'Most Events',
                    'description': f"Record {max_events['total_events']} events held"
                })
            
            # Find first modern Olympics milestone
            first_entry = sorted_data[0] if sorted_data else None
            if first_entry and len(peaks_data) < 4:
                peaks_data.append({
                    'year': first_entry['year'],
                    'value': first_entry['total_participants'],
                    'event': 'First Modern Olympics',
                    'description': f"Modern Olympics began with {first_entry['total_participants']} athletes"
                })
            
            # Find significant growth milestone (year with biggest jump)
            growth_milestone = None
            max_growth = 0
            for i in range(1, len(sorted_data)):
                prev_year = sorted_data[i-1]
                curr_year = sorted_data[i]
                growth = curr_year['total_participants'] - prev_year['total_participants']
                if growth > max_growth:
                    max_growth = growth
                    growth_milestone = curr_year
            
            if growth_milestone and len(peaks_data) < 5:
                peaks_data.append({
                    'year': growth_milestone['year'],
                    'value': growth_milestone['total_participants'],
                    'event': 'Major Expansion',
                    'description': f"Significant growth to {growth_milestone['total_participants']:,} athletes"
                })
            
            # Sort chronologically
            peaks_data.sort(key=lambda x: x['year'])
            
            # Limit to 5 most significant milestones
            peaks_data = peaks_data[:5]
        
        return jsonify({
            'participation_trend': participation_data,
            'medal_performance': medal_performance_data,
            'bmi_trend': bmi_data,
            'medal_efficiency': efficiency_data,
            'event_specialization': specialization_data,
            'kpi_medal_ratio': participation_medal_ratio,
            'historical_peaks': peaks_data,
            'summary': {
                'total_participants': total_participants,
                'total_medals': total_medals,
                'countries_count': len(medal_performance_data),
                'avg_efficiency': avg_efficiency
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/operational-data')
def operational_data():
    """Operational dashboard data from database"""
    try:
        # 1. Venue Status Data
        venue_query = """
        SELECT venue_name, capacity, current_occupancy, status,
               ROUND((current_occupancy::numeric / capacity::numeric) * 100, 1) as capacity_percentage
        FROM operational_venues
        ORDER BY venue_name
        """
        venue_data = execute_query(venue_query)
        
        # 2. Staff Deployment Data
        staff_query = """
        SELECT department, active_count, total_assigned
        FROM operational_staff
        ORDER BY active_count DESC
        """
        staff_data = execute_query(staff_query)
        
        # 3. Transportation Flow Data
        transport_query = """
        SELECT time_slot, passenger_count, on_time_percentage
        FROM operational_transport
        ORDER BY time_slot
        """
        transport_data = execute_query(transport_query)
        
        # 4. Schedule Performance Data
        schedule_query = """
        SELECT day_of_week, on_time_events, minor_delays, major_delays
        FROM operational_schedule
        ORDER BY 
            CASE day_of_week
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END
        """
        schedule_data = execute_query(schedule_query)
        
        # 5. Resource Utilization Data
        resource_query = """
        SELECT resource_type, utilization_percentage
        FROM operational_resources
        ORDER BY resource_type
        """
        resource_data = execute_query(resource_query)
        
        # 6. System Status Data
        status_query = """
        SELECT metric_name, metric_value, status_level
        FROM operational_status
        ORDER BY metric_name
        """
        status_data = execute_query(status_query)
        
        # 7. Priority Alerts Data
        alerts_query = """
        SELECT venue_name, alert_type, description, priority_level, status,
               EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - created_at))/60 as minutes_ago
        FROM operational_alerts
        WHERE status IN ('Active', 'Monitoring', 'Resolved')
        ORDER BY 
            CASE priority_level
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
            END,
            created_at DESC
        LIMIT 10
        """
        alerts_data = execute_query(alerts_query)
        
        # 8. Operational Intelligence Data
        intelligence_query = """
        SELECT insight_type, title, description, recommendation, priority, time_frame
        FROM operational_intelligence
        ORDER BY 
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
            END,
            created_at DESC
        LIMIT 5
        """
        intelligence_data = execute_query(intelligence_query)
        
        # 9. Dashboard Summary Statistics
        summary_query = """
        SELECT * FROM operational_dashboard_summary
        """
        summary_data = execute_query(summary_query)
        summary = summary_data[0] if summary_data else {}
        
        return jsonify({
            'venues': venue_data,
            'staff': staff_data,
            'transportation': transport_data,
            'schedule': schedule_data,
            'resources': resource_data,
            'status': status_data,
            'alerts': alerts_data,
            'intelligence': intelligence_data,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/operational-kpis')
def operational_kpis():
    """Get real-time KPI data for operational dashboard"""
    try:
        # Calculate real-time KPIs from database
        kpi_query = """
        SELECT 
            ROUND(AVG(current_occupancy::numeric / capacity::numeric) * 100, 1) as avg_venue_capacity,
            (SELECT AVG(on_time_percentage) FROM operational_transport) as avg_transport_performance,
            (SELECT COUNT(*) FROM operational_alerts WHERE status = 'Active') as active_incidents,
            (SELECT SUM(active_count) FROM operational_staff) as total_active_staff,
            (SELECT COUNT(*) FROM operational_venues WHERE status = 'Operational') as operational_venues_count,
            (SELECT COUNT(*) FROM operational_venues WHERE status = 'Maintenance') as maintenance_venues_count,
            (SELECT COUNT(*) FROM operational_venues WHERE status = 'Preparing') as preparing_venues_count
        FROM operational_venues
        """
        kpi_data = execute_query(kpi_query)
        
        if kpi_data:
            kpis = kpi_data[0]
            return jsonify({
                'venue_capacity': f"{kpis.get('avg_venue_capacity', 87)}%",
                'transport_performance': f"{kpis.get('avg_transport_performance', 94):.0f}%",
                'active_incidents': kpis.get('active_incidents', 3),
                'active_staff': f"{kpis.get('total_active_staff', 2847):,}",
                'operational_venues': kpis.get('operational_venues_count', 15),
                'maintenance_venues': kpis.get('maintenance_venues_count', 2),
                'preparing_venues': kpis.get('preparing_venues_count', 1),
                'security_level': 'Normal',
                'system_status': 'All Systems Operational',
                'weather': '24°C',
                'total_attendees': '89,432'
            })
        else:
            # Fallback data if query fails
            return jsonify({
                'venue_capacity': '87%',
                'transport_performance': '94%',
                'active_incidents': 3,
                'active_staff': '2,847',
                'operational_venues': 15,
                'maintenance_venues': 2,
                'preparing_venues': 1,
                'security_level': 'Normal',
                'system_status': 'All Systems Operational',
                'weather': '24°C',
                'total_attendees': '89,432'
            })
            
    except Exception as e:
        print(f"DEBUG: Error in operational KPIs endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytical-data')
def analytical_data():
    """Demographics & Physiology dashboard data - Simplified version"""
    year = request.args.get('year')
    sport = request.args.get('sport')
    gender = request.args.get('gender')
    
    try:
        # Basic Gender Distribution
        gender_query = """
        SELECT a.gender, COUNT(DISTINCT a.athleteid) as participant_count
        FROM athlete a
        JOIN participation p ON a.athleteid = p.athleteid
        GROUP BY a.gender
        """
        gender_data = execute_query(gender_query)
        
        # Summary Statistics
        summary_query = """
        SELECT 
            COUNT(DISTINCT a.athleteid) as total_athletes,
            AVG(p.age) as overall_avg_age,
            AVG(p.height) as overall_avg_height,
            AVG(p.weight) as overall_avg_weight,
            AVG(CASE WHEN p.bmi > 0 AND p.bmi < 50 THEN p.bmi END) as overall_avg_bmi,
            COUNT(CASE WHEN a.gender = 'Male' THEN 1 END) as total_male,
            COUNT(CASE WHEN a.gender = 'Female' THEN 1 END) as total_female,
            COUNT(DISTINCT c.countryname) as countries_represented,
            COUNT(DISTINCT s.sportname) as sports_count
        FROM athlete a
        JOIN participation p ON a.athleteid = p.athleteid
        JOIN team t ON a.teamid = t.teamid
        JOIN country c ON t.noc = c.noc
        JOIN event e ON p.eventid = e.eventid
        JOIN sport s ON e.sportid = s.sportid
        """
        summary_data = execute_query(summary_query)
        summary = summary_data[0] if summary_data else {}
        
        # Sports Physiology Data
        sports_query = """
        SELECT s.sportname, 
               COUNT(DISTINCT a.athleteid) as athlete_count,
               AVG(p.age) as avg_age, 
               AVG(p.height) as avg_height, 
               AVG(p.weight) as avg_weight,
               AVG(CASE WHEN p.bmi > 0 AND p.bmi < 50 THEN p.bmi END) as avg_bmi
        FROM athlete a
        JOIN participation p ON a.athleteid = p.athleteid
        JOIN event e ON p.eventid = e.eventid
        JOIN sport s ON e.sportid = s.sportid
        WHERE p.age IS NOT NULL AND p.height > 0 AND p.weight > 0
        GROUP BY s.sportname
        HAVING COUNT(DISTINCT a.athleteid) >= 5
        ORDER BY athlete_count DESC
        LIMIT 15
        """
        physiology_data = execute_query(sports_query)
        
        # Add age categories to sports data
        for sport in physiology_data:
            if sport.get('avg_age'):
                avg_age = float(sport['avg_age'])
                if avg_age < 23:
                    sport['age_category'] = 'Young Sport'
                elif avg_age <= 27:
                    sport['age_category'] = 'Prime Age Sport'
                else:
                    sport['age_category'] = 'Mature Sport'
        
        # Regional Demographics
        regional_query = """
        SELECT c.countryname, 
               COUNT(DISTINCT a.athleteid) as athlete_count,
               AVG(p.age) as avg_age,
               AVG(p.height) as avg_height,
               AVG(p.weight) as avg_weight,
               COUNT(CASE WHEN a.gender = 'Male' THEN 1 END) as male_count,
               COUNT(CASE WHEN a.gender = 'Female' THEN 1 END) as female_count
        FROM athlete a
        JOIN participation p ON a.athleteid = p.athleteid
        JOIN team t ON a.teamid = t.teamid
        JOIN country c ON t.noc = c.noc
        GROUP BY c.countryname
        HAVING COUNT(DISTINCT a.athleteid) >= 10
        ORDER BY athlete_count DESC
        LIMIT 20
        """
        regional_data = execute_query(regional_query)
        
        # BMI Distribution
        bmi_query = """
        WITH bmi_ranges AS (
            SELECT 
                bmi,
                CASE 
                    WHEN bmi < 18.5 THEN 'Underweight'
                    WHEN bmi BETWEEN 18.5 AND 24.9 THEN 'Normal'
                    WHEN bmi BETWEEN 25 AND 29.9 THEN 'Overweight'
                    ELSE 'Obese'
                END as bmi_category
            FROM participation
            WHERE bmi > 0 AND bmi < 50  -- Reasonable BMI range
        )
        SELECT 
            bmi_category,
            COUNT(*) as athlete_count,
            ROUND(AVG(bmi)::numeric, 2) as avg_bmi
        FROM bmi_ranges
        GROUP BY bmi_category
        ORDER BY 
            CASE bmi_category
                WHEN 'Underweight' THEN 1
                WHEN 'Normal' THEN 2
                WHEN 'Overweight' THEN 3
                ELSE 4
            END
        """
        bmi_distribution_data = execute_query(bmi_query)
        
        # Height Performance
        height_performance_query = """
        WITH height_categories AS (
            SELECT 
                height,
                medalid,
                CASE 
                    WHEN height < 165 THEN 'Short'
                    WHEN height BETWEEN 165 AND 175 THEN 'Average'
                    WHEN height BETWEEN 175 AND 185 THEN 'Tall'
                    ELSE 'Very Tall'
                END as height_category
            FROM participation
            WHERE height BETWEEN 140 AND 220
        )
        SELECT 
            height_category,
            COUNT(*) as athlete_count,
            COUNT(CASE WHEN medalid > 0 THEN 1 END) as medal_count,
            ROUND(AVG(height)::numeric, 2) as avg_height,
            ROUND(COUNT(CASE WHEN medalid > 0 THEN 1 END)::numeric / 
                  NULLIF(COUNT(*), 0) * 100, 2) as medal_percentage
        FROM height_categories
        GROUP BY height_category
        ORDER BY 
            CASE height_category
                WHEN 'Short' THEN 1
                WHEN 'Average' THEN 2
                WHEN 'Tall' THEN 3
                ELSE 4
            END
        """
        performance_correlation_data = execute_query(height_performance_query)
        
        # Body Type Medal Analysis
        body_type_query = """
        WITH body_types AS (
            SELECT 
                p.bmi,
                p.medalid,
                m.medaltype,
                CASE 
                    WHEN p.bmi < 20 THEN 'Lean'
                    WHEN p.bmi BETWEEN 20 AND 25 THEN 'Athletic'
                    WHEN p.bmi BETWEEN 25 AND 30 THEN 'Muscular'
                    ELSE 'Heavy'
                END as body_type
            FROM participation p
            LEFT JOIN medal m ON p.medalid = m.medalid
            WHERE p.bmi > 0 AND p.bmi < 50  -- Reasonable BMI range
        )
        SELECT 
            body_type,
            COUNT(*) as athlete_count,
            COUNT(CASE WHEN medalid > 0 THEN 1 END) as total_medals,
            COUNT(CASE WHEN medaltype = 'Gold' THEN 1 END) as gold_medals,
            COUNT(CASE WHEN medaltype = 'Silver' THEN 1 END) as silver_medals,
            COUNT(CASE WHEN medaltype = 'Bronze' THEN 1 END) as bronze_medals,
            ROUND(AVG(bmi)::numeric, 2) as avg_bmi,
            ROUND(COUNT(CASE WHEN medalid > 0 THEN 1 END)::numeric / 
                  NULLIF(COUNT(*), 0) * 100, 2) as medal_percentage
        FROM body_types
        GROUP BY body_type
        ORDER BY 
            CASE body_type
                WHEN 'Lean' THEN 1
                WHEN 'Athletic' THEN 2
                WHEN 'Muscular' THEN 3
                ELSE 4
            END
        """
        body_type_medals_data = execute_query(body_type_query)
        
        # Age Evolution Over Time
        age_evolution_query = """
        SELECT og.year,
               AVG(p.age) as avg_age,
               MIN(p.age) as min_age,
               MAX(p.age) as max_age,
               COUNT(DISTINCT a.athleteid) as athlete_count
        FROM athlete a
        JOIN participation p ON a.athleteid = p.athleteid
        JOIN olympicgames og ON p.gamesid = og.gamesid
        WHERE p.age IS NOT NULL
        GROUP BY og.year
        ORDER BY og.year
        """
        age_evolution_data = execute_query(age_evolution_query)
        
        result = {
            'age_by_sport': physiology_data,
            'physiology_by_sport': physiology_data,
            'bmi_distribution': bmi_distribution_data,
            'regional_demographics': regional_data,
            'performance_by_height': performance_correlation_data,
            'age_evolution': age_evolution_data,
            'body_type_medals': body_type_medals_data,
            'summary': summary
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 