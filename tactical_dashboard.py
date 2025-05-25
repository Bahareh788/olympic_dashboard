import plotly.express as px
import plotly.graph_objects as go
from db_utils import execute_query
from components.tactical_summary_cards import create_tactical_summary_cards

# Olympic colors
OLYMPIC_COLORS = {
    'blue': '#0085C3',
    'yellow': '#F4C300',
    'black': '#000000',
    'green': '#009F3D',
    'red': '#DF0024',
    'gold': '#FFD700',
    'silver': '#C0C0C0',
    'bronze': '#CD7F32'
}

DEFAULT_FONT = dict(family='Montserrat, Roboto, sans-serif', size=13, color='#222')
TITLE_FONT = dict(family='Montserrat, Roboto, sans-serif', size=16, color='#222')

def create_medal_by_country_gender():
    query = """
    SELECT c.countryname as country, a.gender as gender, COUNT(m.medalid) as medal_count
    FROM country c
    JOIN team t ON c.noc = t.noc
    JOIN participation p ON t.teamid = p.teamid
    JOIN athlete a ON p.athleteid = a.athleteid
    JOIN medal m ON p.medalid = m.medalid
    GROUP BY c.countryname, a.gender
    ORDER BY c.countryname, a.gender
    """
    data = execute_query(query)
    
    fig = px.bar(
        data,
        x='country',
        y='medal_count',
        color='gender',
        title='Medals by Country and Gender',
        labels={'country': 'Country', 'medal_count': 'Number of Medals', 'gender': 'Gender'},
        color_discrete_map={'M': OLYMPIC_COLORS['blue'], 'F': OLYMPIC_COLORS['red']},
        hover_data=['medal_count', 'gender']
    )
    fig.update_layout(
        font=DEFAULT_FONT,
        title_font=TITLE_FONT,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="#fff",
            bordercolor="#eee",
            borderwidth=1,
            font=DEFAULT_FONT
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_medalist_age_distribution():
    query = """
    SELECT p.age as age, COUNT(m.medalid) as medal_count
    FROM athlete a
    JOIN participation p ON a.athleteid = p.athleteid
    JOIN medal m ON p.medalid = m.medalid
    GROUP BY p.age
    ORDER BY p.age
    """
    data = execute_query(query)
    
    fig = px.line(
        data,
        x='age',
        y='medal_count',
        title='Age Distribution of Medalists',
        labels={'age': 'Age', 'medal_count': 'Number of Medals'},
        hover_data=['medal_count']
    )
    fig.update_traces(line_color=OLYMPIC_COLORS['green'])
    fig.update_layout(
        font=DEFAULT_FONT,
        title_font=TITLE_FONT,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="#fff",
            bordercolor="#eee",
            borderwidth=1,
            font=DEFAULT_FONT
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_top_sports():
    query = """
    SELECT s.sportname as name, COUNT(m.medalid) as medal_count
    FROM sport s
    JOIN event e ON s.sportid = e.sportid
    JOIN participation p ON e.eventid = p.eventid
    JOIN medal m ON p.medalid = m.medalid
    GROUP BY s.sportname
    ORDER BY medal_count DESC
    LIMIT 10
    """
    data = execute_query(query)
    
    fig = px.bar(
        data,
        y='name',
        x='medal_count',
        orientation='h',
        title='Top Performing Sports by Medal Count',
        labels={'name': 'Sport', 'medal_count': 'Number of Medals'},
        color='medal_count',
        color_continuous_scale=[OLYMPIC_COLORS['blue'], OLYMPIC_COLORS['yellow']],
        hover_data=['medal_count']
    )
    fig.update_layout(
        font=DEFAULT_FONT,
        title_font=TITLE_FONT,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="#fff",
            bordercolor="#eee",
            borderwidth=1,
            font=DEFAULT_FONT
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_gold_medal_teams():
    query = """
    SELECT t.teamname as team, COUNT(m.medalid) as gold_count
    FROM team t
    JOIN participation p ON t.teamid = p.teamid
    JOIN medal m ON p.medalid = m.medalid
    WHERE m.medaltype = 'Gold'
    GROUP BY t.teamname
    ORDER BY gold_count DESC
    LIMIT 10
    """
    data = execute_query(query)
    # Truncate team names for clarity
    data = [{**row, 'team': row['team'][:16] + ('...' if len(row['team']) > 16 else '')} for row in data]
    fig = px.pie(
        data,
        values='gold_count',
        names='team',
        title='Teams with Most Gold Medals',
        hole=0.55,
        color_discrete_sequence=[OLYMPIC_COLORS['gold'], OLYMPIC_COLORS['silver'], OLYMPIC_COLORS['bronze'], OLYMPIC_COLORS['blue'], OLYMPIC_COLORS['yellow'], OLYMPIC_COLORS['black'], OLYMPIC_COLORS['green'], OLYMPIC_COLORS['red']],
        hover_data=['gold_count']
    )
    fig.update_traces(textinfo='label', textposition='outside', textfont_size=11, marker=dict(line=dict(color='#fff', width=1)), pull=[0.02]*len(data))
    fig.update_layout(
        font=DEFAULT_FONT,
        title_font=TITLE_FONT,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            bgcolor="#fff",
            bordercolor="#eee",
            borderwidth=1,
            font=DEFAULT_FONT
        ),
        margin=dict(l=40, r=20, t=60, b=40, autoexpand=True),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=320
    )
    return fig

def create_top_athletes():
    query = """
    SELECT 
        a.fullname as name,
        COUNT(CASE WHEN m.medaltype = 'Gold' THEN 1 END) as gold_count
    FROM athlete a
    JOIN participation p ON a.athleteid = p.athleteid
    JOIN medal m ON p.medalid = m.medalid
    WHERE m.medaltype = 'Gold'
    GROUP BY a.fullname
    ORDER BY gold_count DESC
    LIMIT 10
    """
    data = execute_query(query)
    
    fig = px.bar(
        data,
        y='name',
        x='gold_count',
        orientation='h',
        title='Top Athletes by Gold Medals',
        labels={'name': 'Athlete', 'gold_count': 'Number of Gold Medals'},
        color='gold_count',
        color_continuous_scale=[OLYMPIC_COLORS['yellow'], OLYMPIC_COLORS['black']],
        hover_data=['gold_count']
    )
    fig.update_layout(
        font=DEFAULT_FONT,
        title_font=TITLE_FONT,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="#fff",
            bordercolor="#eee",
            borderwidth=1,
            font=DEFAULT_FONT
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_age_vs_medal_type():
    query = """
    SELECT
        p.age as age,
        m.medaltype as medaltype
    FROM participation p
    JOIN medal m ON p.medalid = m.medalid
    WHERE m.medalid IS NOT NULL AND p.age IS NOT NULL
    """
    data = execute_query(query)
    
    fig = px.box(
        data,
        x='medaltype',
        y='age',
        title='Age Distribution by Medal Type',
        labels={'medaltype': 'Medal Type', 'age': 'Age'},
        category_orders={'medaltype': ['Gold', 'Silver', 'Bronze']},
        color='medaltype',
        color_discrete_map={'Gold': OLYMPIC_COLORS['yellow'], 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'},
        hover_data=['age']
    )
    fig.update_layout(
        font=DEFAULT_FONT,
        title_font=TITLE_FONT,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="#fff",
            bordercolor="#eee",
            borderwidth=1,
            font=DEFAULT_FONT
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def get_noc_medal_table():
    query = '''
        SELECT
            c.countryname AS team_noc,
            SUM(CASE WHEN m.medaltype = 'Gold' THEN 1 ELSE 0 END) AS gold,
            SUM(CASE WHEN m.medaltype = 'Silver' THEN 1 ELSE 0 END) AS silver,
            SUM(CASE WHEN m.medaltype = 'Bronze' THEN 1 ELSE 0 END) AS bronze
        FROM country c
        JOIN team t ON c.noc = t.noc
        JOIN participation p ON t.teamid = p.teamid
        JOIN medal m ON p.medalid = m.medalid
        WHERE m.medaltype != 'None'
        GROUP BY c.countryname
        ORDER BY gold DESC, silver DESC, bronze DESC
    '''
    data = execute_query(query)
    return data

def get_tactical_dashboard():
    return {
        'summary_cards': create_tactical_summary_cards(),
        'medal_by_country_gender': create_medal_by_country_gender(),
        'medalist_age': create_medalist_age_distribution(),
        'top_sports': create_top_sports(),
        'gold_medal_teams': create_gold_medal_teams(),
        'top_athletes': create_top_athletes(),
        'age_vs_medal_type': create_age_vs_medal_type(),
        'noc_medal_table': get_noc_medal_table()
    } 