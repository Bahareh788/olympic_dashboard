from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Bahardb1234@localhost:5432/Olympicdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard/analytic')
def analytic_dashboard():
    # -- Analytical Dashboard Queries (unchanged) --
    gender_query = text(
        """
        SELECT gender, COUNT(*) AS count
        FROM athlete
        GROUP BY gender;
        """
    )
    gender_result = db.session.execute(gender_query)
    gender_data = [{'gender': row[0], 'count': row[1]} for row in gender_result]

    trend_query = text(
        """
        SELECT og.year, og.season, COUNT(*) AS count
        FROM participation p
        JOIN olympicgames og ON p.gamesid = og.gamesid
        GROUP BY og.year, og.season
        ORDER BY og.year;
        """
    )
    trend_result = db.session.execute(trend_query)
    trend_data = [{'year': row[0], 'season': row[1], 'count': row[2]} for row in trend_result]

    country_participation_query = text(
        """
        SELECT t.noc, COUNT(*) AS count
        FROM staging_main sm
        JOIN team t ON sm.teamid = t.teamid
        GROUP BY t.noc;
        """
    )
    country_participation_result = db.session.execute(country_participation_query)
    country_participation_data = [{'noc': row[0], 'count': row[1]} for row in country_participation_result]

    continent_query = text(
        """
        SELECT c.region AS continent,
               COUNT(DISTINCT sm.athleteid) AS athletes,
               COUNT(sm.medalid) AS medals
        FROM staging_main sm
        JOIN team t ON sm.teamid = t.teamid
        JOIN country c ON t.noc = c.noc
        GROUP BY c.region;
        """
    )
    continent_result = db.session.execute(continent_query)
    continent_data = [
        {'continent': row[0], 'athletes': row[1], 'medals': row[2]}
        for row in continent_result
    ]

    top_events_query = text(
        """
        SELECT e.eventname, COUNT(*) AS count
        FROM staging_main sm
        JOIN event e ON sm.eventid = e.eventid
        GROUP BY e.eventname
        ORDER BY count DESC
        LIMIT 10;
        """
    )
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
    # 1) Medal count by country & gender
    medal_count_query = text("""
        SELECT
          t.teamname,
          sm.gender,
          COUNT(sm.medalid) AS medal_count
        FROM staging_main sm
        JOIN team    t ON sm.teamid    = t.teamid
        WHERE sm.medalid IS NOT NULL
        GROUP BY t.teamname, sm.gender
        ORDER BY t.teamname, sm.gender;
    """)
    medal_count_data = [
        {'country': row[0], 'gender': row[1], 'count': row[2]}
        for row in db.session.execute(medal_count_query)
    ]

    # 2) Age distribution of medalists (pulled from staging_main.age)
    medalist_ages_query = text("""
        SELECT age
        FROM staging_main
        WHERE medalid IS NOT NULL
          AND age IS NOT NULL;
    """)
    medalist_ages = [r[0] for r in db.session.execute(medalist_ages_query)]

    # 3) Top performing sports by medal count
    top_sports_query = text("""
        SELECT
          s.sportname,
          COUNT(sm.medalid) AS medals
        FROM staging_main sm
        JOIN event e ON sm.eventid = e.eventid
        JOIN sport s ON e.sportid   = s.sportid
        WHERE sm.medalid IS NOT NULL
        GROUP BY s.sportname
        ORDER BY medals DESC
        LIMIT 10;
    """)
    top_sports_data = [
        {'sport': row[0], 'medals': row[1]}
        for row in db.session.execute(top_sports_query)
    ]

    # 4) Medal efficiency by country (medals per athlete)
    efficiency_query = text("""
        SELECT
          t.teamname,
          COUNT(sm.medalid)::float
            / NULLIF(COUNT(DISTINCT sm.athleteid), 0)
            AS efficiency
        FROM staging_main sm
        JOIN team t ON sm.teamid = t.teamid
        GROUP BY t.teamname
        ORDER BY efficiency DESC
        LIMIT 10;
    """)
    efficiency_data = [
        {'country': row[0], 'efficiency': round(row[1], 2)}
        for row in db.session.execute(efficiency_query)
    ]

    return render_template(
        'tactical_dashboard.html',
        medal_count_data=medal_count_data,
        medalist_ages=medalist_ages,
        top_sports_data=top_sports_data,
        efficiency_data=efficiency_data
    )

if __name__ == '__main__':
    app.run(debug=True)