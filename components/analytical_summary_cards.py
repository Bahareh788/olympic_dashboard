import plotly.graph_objects as go
from db_utils import execute_query

# Olympic color scheme to match dashboard
OLYMPIC_COLORS = {
    'blue': '#2563EB',      # High contrast blue
    'yellow': '#F59E0B',    # Amber/Orange
    'black': '#1F2937',     # Dark gray
    'green': '#059669',     # Emerald green
    'red': '#DC2626'        # High contrast red
}

DEFAULT_FONT = dict(family='Montserrat, Roboto, sans-serif', size=13, color='#222')

def create_top_kpi_cards():
    """
    Create 4 KPI summary cards for the TOP of the analytical dashboard:
    1. Total Athletes - total unique athletes
    2. Gender Ratio - male vs female percentage
    3. Number of Sports - distinct sports count  
    4. Median Athlete Age - median age of athletes
    """
    
    # Query for basic metrics using correct tables
    query = """
    SELECT 
        (SELECT COUNT(DISTINCT athleteid) FROM athlete) as total_athletes,
        (SELECT COUNT(DISTINCT sportid) FROM sport) as total_sports,
        (SELECT COUNT(DISTINCT athleteid) FROM athlete WHERE gender = 'M') as male_count,
        (SELECT COUNT(DISTINCT athleteid) FROM athlete WHERE gender = 'F') as female_count
    """
    
    # Query for median age using staging_main table
    median_query = """
    WITH age_data AS (
        SELECT 
            age,
            ROW_NUMBER() OVER (ORDER BY age) as row_num,
            COUNT(*) OVER () as total_count
        FROM staging_main 
        WHERE age IS NOT NULL 
        AND age > 0
    )
    SELECT 
        AVG(CAST(age AS FLOAT)) as median_age
    FROM age_data 
    WHERE row_num IN ((total_count + 1) / 2, (total_count + 2) / 2)
    """
    
    try:
        data = execute_query(query)[0]
        median_result = execute_query(median_query)
        median_age = median_result[0]['median_age'] if median_result and median_result[0]['median_age'] else 25.0
        
        # Calculate gender percentages
        total_gendered = data['male_count'] + data['female_count']
        male_percentage = (data['male_count'] / total_gendered * 100) if total_gendered > 0 else 50.0
        female_percentage = (data['female_count'] / total_gendered * 100) if total_gendered > 0 else 50.0
        
    except Exception as e:
        print(f"Error in KPI cards query: {e}")
        # Fallback values
        data = {'total_athletes': 0, 'total_sports': 0, 'male_count': 0, 'female_count': 0}
        median_age = 25.0
        male_percentage = 50.0
        female_percentage = 50.0
    
    cards = []
    
    # 1. Total Athletes Card (Olympic Blue)
    fig1 = go.Figure()
    fig1.add_trace(go.Indicator(
        mode="number",
        value=data['total_athletes'],
        title={
            "text": "Total Athletes",
            "font": {"size": 16, "family": "Montserrat, sans-serif", "color": OLYMPIC_COLORS['blue']}
        },
        number={
            'font': {'size': 48, 'color': OLYMPIC_COLORS['blue'], 'family': 'Montserrat, sans-serif'},
            'valueformat': ','
        },
        domain={'row': 0, 'column': 0}
    ))
    fig1.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(37, 99, 235, 0.05)',  # Light blue background
        plot_bgcolor='rgba(37, 99, 235, 0.05)',
        font=DEFAULT_FONT,
        shapes=[
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color=OLYMPIC_COLORS['blue'], width=2),
                fillcolor="rgba(255, 255, 255, 0.9)"
            )
        ]
    )
    cards.append(fig1)
    
    # 2. Gender Ratio Card (Olympic Red for diversity)
    fig2 = go.Figure()
    fig2.add_trace(go.Indicator(
        mode="number+delta",
        value=male_percentage,
        delta={
            'reference': female_percentage,
            'valueformat': '.1f',
            'suffix': '%',
            'font': {'size': 14, 'color': OLYMPIC_COLORS['red']}
        },
        title={
            "text": f"Gender Ratio<br><span style='font-size:12px;color:#666'>♂ {male_percentage:.1f}% | ♀ {female_percentage:.1f}%</span>",
            "font": {"size": 16, "family": "Montserrat, sans-serif", "color": OLYMPIC_COLORS['red']}
        },
        number={
            'font': {'size': 36, 'color': OLYMPIC_COLORS['red'], 'family': 'Montserrat, sans-serif'},
            'suffix': '% ♂',
            'valueformat': '.1f'
        },
        domain={'row': 0, 'column': 1}
    ))
    fig2.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(220, 38, 38, 0.05)',  # Light red background
        plot_bgcolor='rgba(220, 38, 38, 0.05)',
        font=DEFAULT_FONT,
        shapes=[
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color=OLYMPIC_COLORS['red'], width=2),
                fillcolor="rgba(255, 255, 255, 0.9)"
            )
        ]
    )
    cards.append(fig2)
    
    # 3. Number of Sports Card (Olympic Green)
    fig3 = go.Figure()
    fig3.add_trace(go.Indicator(
        mode="number",
        value=data['total_sports'],
        title={
            "text": "Number of Sports",
            "font": {"size": 16, "family": "Montserrat, sans-serif", "color": OLYMPIC_COLORS['green']}
        },
        number={
            'font': {'size': 48, 'color': OLYMPIC_COLORS['green'], 'family': 'Montserrat, sans-serif'},
            'valueformat': ','
        },
        domain={'row': 0, 'column': 2}
    ))
    fig3.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(5, 150, 105, 0.05)',  # Light green background
        plot_bgcolor='rgba(5, 150, 105, 0.05)',
        font=DEFAULT_FONT,
        shapes=[
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color=OLYMPIC_COLORS['green'], width=2),
                fillcolor="rgba(255, 255, 255, 0.9)"
            )
        ]
    )
    cards.append(fig3)
    
    # 4. Median Athlete Age Card (Olympic Yellow/Amber)
    fig4 = go.Figure()
    fig4.add_trace(go.Indicator(
        mode="number",
        value=median_age,
        title={
            "text": "Median Athlete Age",
            "font": {"size": 16, "family": "Montserrat, sans-serif", "color": OLYMPIC_COLORS['yellow']}
        },
        number={
            'font': {'size': 48, 'color': OLYMPIC_COLORS['yellow'], 'family': 'Montserrat, sans-serif'},
            'suffix': ' yrs',
            'valueformat': '.1f'
        },
        domain={'row': 0, 'column': 3}
    ))
    fig4.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(245, 158, 11, 0.05)',  # Light yellow background
        plot_bgcolor='rgba(245, 158, 11, 0.05)',
        font=DEFAULT_FONT,
        shapes=[
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color=OLYMPIC_COLORS['yellow'], width=2),
                fillcolor="rgba(255, 255, 255, 0.9)"
            )
        ]
    )
    cards.append(fig4)
    
    return cards

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