import plotly.graph_objects as go
from db_utils import execute_query

def create_analytical_summary_cards():
    # Optimized query for summary statistics
    query = """
    WITH stats AS (
        SELECT 
            (SELECT COUNT(DISTINCT athleteid) FROM athlete) as total_athletes,
            (SELECT COUNT(DISTINCT sportid) FROM sport) as total_sports,
            (SELECT COUNT(DISTINCT eventid) FROM event) as total_events,
            (SELECT MIN(year) FROM olympicgames) as min_year,
            (SELECT MAX(year) FROM olympicgames) as max_year
    )
    SELECT * FROM stats
    """
    data = execute_query(query)[0]
    
    # Create summary cards using plotly
    cards = []
    
    # Total Athletes Card
    fig1 = go.Figure()
    fig1.add_trace(go.Indicator(
        mode="number",
        value=data['total_athletes'],
        title="Total Athletes",
        number={'font': {'size': 40}},
        domain={'row': 0, 'column': 0}
    ))
    fig1.update_layout(
        height=150,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
    )
    cards.append(fig1)
    
    # Total Number of Sports Card
    fig2 = go.Figure()
    fig2.add_trace(go.Indicator(
        mode="number",
        value=data['total_sports'],
        title="Total Number of Sports",
        number={'font': {'size': 40}},
        domain={'row': 0, 'column': 1}
    ))
    fig2.update_layout(
        height=150,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
    )
    cards.append(fig2)
    
    # Events Covered Card
    fig3 = go.Figure()
    fig3.add_trace(go.Indicator(
        mode="number",
        value=data['total_events'],
        title="Events Covered",
        number={'font': {'size': 40}},
        domain={'row': 0, 'column': 2}
    ))
    fig3.update_layout(
        height=150,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
    )
    cards.append(fig3)
    
    # Year Range Card
    fig4 = go.Figure()
    fig4.add_trace(go.Indicator(
        mode="number+delta",
        value=data['max_year'],
        delta={'reference': data['min_year']},
        title="Year Range",
        number={'font': {'size': 40}},
        domain={'row': 0, 'column': 3}
    ))
    fig4.update_layout(
        height=150,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
    )
    cards.append(fig4)
    
    return cards 