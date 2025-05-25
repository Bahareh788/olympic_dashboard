from dash import html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine, text
import os

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:Bahardb1234@localhost:5432/Olympicdb')
engine = create_engine(DATABASE_URL)

# Font settings
DEFAULT_FONT = dict(family="Roboto, sans-serif", size=12)
TITLE_FONT = dict(family="Roboto, sans-serif", size=14, color="#2c3e50")

def create_tactical_summary_cards():
    # Optimized query for summary statistics with updated medal counts
    query = """
    WITH medal_stats AS (
        SELECT 
            (SELECT COUNT(p.medalid) FROM participation p WHERE p.medalid IS NOT NULL) as total_medals,
            (SELECT COUNT(p.medalid) FROM participation p JOIN medal m ON p.medalid = m.medalid WHERE m.medaltype = 'Gold') as gold_medals
    ),
    top_country AS (
        SELECT 
            c.countryname,
            COUNT(m.medalid) as medal_count
        FROM medal m
        JOIN participation p ON m.medalid = p.medalid
        JOIN team t ON p.teamid = t.teamid
        JOIN country c ON t.noc = c.noc
        WHERE m.medaltype != 'None'
        GROUP BY c.countryname
        ORDER BY medal_count DESC
        LIMIT 1
    ),
    top_athlete AS (
        SELECT 
            a.fullname,
            COUNT(m.medalid) as medal_count
        FROM medal m
        JOIN participation p ON m.medalid = p.medalid
        JOIN athlete a ON p.athleteid = a.athleteid
        WHERE m.medaltype != 'None'
        GROUP BY a.fullname
        ORDER BY medal_count DESC
        LIMIT 1
    )
    SELECT 
        ms.total_medals,
        ms.gold_medals,
        tc.countryname as top_country,
        tc.medal_count as country_medals,
        ta.fullname as top_athlete,
        ta.medal_count as athlete_medals
    FROM medal_stats ms
    CROSS JOIN top_country tc
    CROSS JOIN top_athlete ta
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(query))
        row = result.fetchone()
        
    return [
        {"type": "simple", "value": row.total_medals},
        {"type": "simple", "value": row.gold_medals},
        {"type": "complex", "name": row.top_country, "value": row.country_medals},
        {"type": "complex", "name": row.top_athlete, "value": row.athlete_medals}
    ]

def create_medal_by_country_gender():
    query = """
    SELECT 
        c.countryname,
        a.gender,
        COUNT(m.medalid) as medal_count
    FROM medal m
    JOIN participation p ON m.medalid = p.medalid
    JOIN athlete a ON p.athleteid = a.athleteid
    JOIN team t ON p.teamid = t.teamid
    JOIN country c ON t.noc = c.noc
    WHERE m.medaltype != 'None'
    GROUP BY c.countryname, a.gender
    ORDER BY medal_count DESC
    LIMIT 10
    """
    
    df = pd.read_sql(query, engine)
    
    fig = px.bar(df, 
                 x='countryname', 
                 y='medal_count',
                 color='gender',
                 barmode='group',
                 title='Medals by Country and Gender',
                 labels={'countryname': 'Country', 'medal_count': 'Number of Medals', 'gender': 'Gender'})
    
    fig.update_layout(
        font=DEFAULT_FONT,
        title_font=TITLE_FONT,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff"
    )
    
    return fig

def create_gold_medals_pie():
    query = """
    SELECT 
        c.countryname,
        COUNT(m.medalid) as gold_count
    FROM medal m
    JOIN participation p ON m.medalid = p.medalid
    JOIN team t ON p.teamid = t.teamid
    JOIN country c ON t.noc = c.noc
    WHERE m.medaltype = 'Gold'
    GROUP BY c.countryname
    ORDER BY gold_count DESC
    LIMIT 5
    """
    
    df = pd.read_sql(query, engine)
    
    fig = px.pie(df, 
                 values='gold_count', 
                 names='countryname',
                 title='Teams with Most Gold Medals',
                 hover_data=['gold_count'])
    
    fig.update_traces(
        textposition='outside',
        textfont_size=11,
        marker=dict(line=dict(color='#fff', width=1)),
        pull=[0.02]*len(df)
    )
    
    fig.update_layout(
        font=DEFAULT_FONT,
        title_font=TITLE_FONT,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            bgcolor="#fff",
            bordercolor="#eee",
            borderwidth=1,
            font=DEFAULT_FONT
        ),
        margin=dict(l=40, r=150, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=400,
        showlegend=True
    )
    
    return fig

def create_top_athletes():
    query = """
    SELECT 
        a.athletename,
        c.countryname,
        COUNT(m.medalid) as medal_count
    FROM medal m
    JOIN participation p ON m.medalid = p.medalid
    JOIN athlete a ON p.athleteid = a.athleteid
    JOIN team t ON p.teamid = t.teamid
    JOIN country c ON t.noc = c.noc
    WHERE m.medaltype != 'None'
    GROUP BY a.athletename, c.countryname
    ORDER BY medal_count DESC
    LIMIT 10
    """
    
    df = pd.read_sql(query, engine)
    
    fig = px.bar(df,
                 x='athletename',
                 y='medal_count',
                 color='countryname',
                 title='Top Athletes by Medal Count',
                 labels={'athletename': 'Athlete', 'medal_count': 'Number of Medals', 'countryname': 'Country'})
    
    fig.update_layout(
        font=DEFAULT_FONT,
        title_font=TITLE_FONT,
        xaxis_tickangle=-45,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=20, t=60, b=100),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff"
    )
    
    return fig