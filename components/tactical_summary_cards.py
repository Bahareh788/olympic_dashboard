import plotly.graph_objects as go
from db_utils import execute_query

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
            COUNT(CASE WHEN m.medaltype = 'Gold' THEN 1 END) as gold_count
        FROM medal m
        JOIN participation p ON m.medalid = p.medalid
        JOIN athlete a ON p.athleteid = a.athleteid
        WHERE m.medaltype = 'Gold'
        GROUP BY a.fullname
        ORDER BY gold_count DESC
        LIMIT 1
    )
    SELECT 
        ms.total_medals,
        ms.gold_medals,
        tc.countryname as top_country,
        tc.medal_count as country_medal_count,
        ta.fullname as top_athlete,
        ta.gold_count as athlete_gold_count
    FROM medal_stats ms
    CROSS JOIN top_country tc
    CROSS JOIN top_athlete ta
    """
    data = execute_query(query)[0]
    
    # Create summary cards using plotly
    cards = []
    
    # Total Medals Card
    fig1 = go.Figure()
    fig1.add_trace(go.Indicator(
        mode="number",
        value=data['total_medals'],
        title="Total Medals",
        number={'font': {'size': 40}},
        domain={'row': 0, 'column': 0}
    ))
    fig1.update_layout(
        height=150,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    cards.append(fig1)
    
    # Gold Medals Card
    fig2 = go.Figure()
    fig2.add_trace(go.Indicator(
        mode="number",
        value=data['gold_medals'],
        title="Gold Medals",
        number={'font': {'size': 40}},
        domain={'row': 0, 'column': 1}
    ))
    fig2.update_layout(
        height=150,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    cards.append(fig2)
    
    # Top Country Card (show count, name in title)
    fig3 = go.Figure()
    fig3.add_trace(go.Indicator(
        mode="number",
        value=data['country_medal_count'],
        title={"text": f"Top Country:<br>{data['top_country']}"},
        number={'font': {'size': 40}},
        domain={'row': 0, 'column': 2}
    ))
    fig3.update_layout(
        height=150,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    cards.append(fig3)
    
    # Top Athlete Card (show count, name in title)
    fig4 = go.Figure()
    fig4.add_trace(go.Indicator(
        mode="number",
        value=data['athlete_gold_count'],
        title={"text": f"Top Athlete:<br>{data['top_athlete']}"},
        number={'font': {'size': 40}},
        domain={'row': 0, 'column': 3}
    ))
    fig4.update_layout(
        height=150,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    cards.append(fig4)
    
    return cards 