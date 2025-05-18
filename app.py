from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Bahardb1234@localhost:5432/Olympicdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def home():
    # Render the landing page with buttons to each dashboard
    return render_template('index.html')

@app.route('/dashboard/analytic')
def analytic_dashboard():
    # 1) Gender distribution
    gender_query = text("""
        SELECT gender, COUNT(*) AS cnt
        FROM athlete
        GROUP BY gender;
    """)
    gender_result = db.session.execute(gender_query)
    gender_data = [{'gender': row[0], 'count': row[1]} for row in gender_result]

    # 2) Participation trend by Olympic years & season
    trend_query = text("""
        SELECT og.year, og.season, COUNT(*) AS cnt
        FROM participation p
        JOIN olympicgames og ON p.gamesid = og.gamesid
        GROUP BY og.year, og.season
        ORDER BY og.year;
    """)
    trend_result = db.session.execute(trend_query)
    trend_data = [{'year': row[0], 'season': row[1], 'count': row[2]} for row in trend_result]

    # 3) Participation by country (choropleth)
    country_participation_query = text("""
        SELECT t.noc, COUNT(*) AS cnt
        FROM participation p
        JOIN athlete  a ON p.athleteid = a.athleteid
        JOIN team     t ON a.teamid   = t.teamid
        GROUP BY t.noc;
    """)
    country_participation_result = db.session.execute(country_participation_query)
    country_participation_data = [{'noc': row[0], 'count': row[1]} for row in country_participation_result]

    # 4) Athletes & medals by continent (region)
    continent_query = text("""
        SELECT c.region AS continent,
               COUNT(DISTINCT a.athleteid) AS athletes,
               COUNT(p.medalid)             AS medals
        FROM participation p
        JOIN athlete  a ON p.athleteid = a.athleteid
        JOIN team     t ON a.teamid    = t.teamid
        JOIN country  c ON t.noc       = c.noc
        GROUP BY c.region;
    """)
    continent_result = db.session.execute(continent_query)
    continent_data = [
        {'continent': row[0], 'athletes': row[1], 'medals': row[2]}
        for row in continent_result
    ]

    # 5) Top 10 most participated events
    top_events_query = text("""
        SELECT e.eventname, COUNT(*) AS cnt
        FROM participation p
        JOIN event      e ON p.eventid = e.eventid
        GROUP BY e.eventname
        ORDER BY cnt DESC
        LIMIT 10;
    """)
    top_events_result = db.session.execute(top_events_query)
    top_events_data = [{'event': row[0], 'count': row[1]} for row in top_events_result]

    return render_template(
        'analytic_dashboard.html',
        gender_data=gender_data,
        trend_data=trend_data,
        country_participation_data=country_participation_data,
        continent_data=continent_data,
        top_events_data=top_events_data
    )

@app.route('/dashboard/tactical')
def tactical_dashboard():
    return render_template('tactical_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
