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
        color_discrete_map={'M': OLYMPIC_COLORS['blue'], 'F': OLYMPIC_COLORS['red']}
    )
    fig.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
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
        labels={'age': 'Age', 'medal_count': 'Number of Medals'}
    )
    fig.update_traces(line_color=OLYMPIC_COLORS['green'])
    fig.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
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
        color_continuous_scale=[OLYMPIC_COLORS['blue'], OLYMPIC_COLORS['yellow']]
    )
    fig.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
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
    
    fig = px.pie(
        data,
        values='gold_count',
        names='team',
        title='Teams with Most Gold Medals',
        hole=0.4,
        color_discrete_sequence=[OLYMPIC_COLORS['gold'], OLYMPIC_COLORS['silver'], OLYMPIC_COLORS['bronze'], OLYMPIC_COLORS['blue'], OLYMPIC_COLORS['yellow'], OLYMPIC_COLORS['black'], OLYMPIC_COLORS['green'], OLYMPIC_COLORS['red']]
    )
    fig.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
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
        color_continuous_scale=[OLYMPIC_COLORS['yellow'], OLYMPIC_COLORS['black']]
    )
    fig.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
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
        color_discrete_map={'Gold': OLYMPIC_COLORS['yellow'], 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}
    )
    fig.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font={'color': '#000000'}
    )
    return fig

def get_tactical_dashboard():
    return {
        'summary_cards': create_tactical_summary_cards(),
        'medal_by_country_gender': create_medal_by_country_gender(),
        'medalist_age': create_medalist_age_distribution(),
        'top_sports': create_top_sports(),
        'gold_medal_teams': create_gold_medal_teams(),
        'top_athletes': create_top_athletes(),
        'age_vs_medal_type': create_age_vs_medal_type()
    } 