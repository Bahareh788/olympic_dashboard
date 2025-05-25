import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from db_utils import execute_query
from components.analytical_summary_cards import create_analytical_summary_cards

# Olympic colors
OLYMPIC_COLORS = {
    'blue': '#0085C3',
    'yellow': '#F4C300',
    'black': '#000000',
    'green': '#009F3D',
    'red': '#DF0024'
}

DEFAULT_FONT = dict(family='Montserrat, Roboto, sans-serif', size=13, color='#222')
TITLE_FONT = dict(family='Montserrat, Roboto, sans-serif', size=16, color='#222')

def create_gender_distribution():
    query = """
    SELECT gender, COUNT(DISTINCT athleteid) as count
    FROM athlete
    GROUP BY gender
    """
    data = execute_query(query)
    
    fig = px.pie(
        data,
        values='count',
        names='gender',
        title='Total Athletes by Gender',
        labels={'gender': 'Gender', 'count': 'Number of Athletes'},
        color='gender',
        color_discrete_map={'M': OLYMPIC_COLORS['blue'], 'F': OLYMPIC_COLORS['red']}
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
            borderwidth=1
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_participation_trend():
    query = """
    SELECT og.year as year, COUNT(DISTINCT p.athleteid) as athlete_count
    FROM olympicgames og
    JOIN participation p ON og.gamesid = p.gamesid
    GROUP BY og.year
    ORDER BY og.year
    """
    data = execute_query(query)
    
    fig = px.line(
        data,
        x='year',
        y='athlete_count',
        title='Gender Participation Evolution Over Time',
        labels={'year': 'Olympic Year', 'athlete_count': 'Number of Athletes'}
    )
    fig.update_traces(line_color=OLYMPIC_COLORS['blue'])
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
            borderwidth=1
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_top_events():
    query = """
    SELECT s.sportname as name, COUNT(DISTINCT p.athleteid) as athlete_count
    FROM sport s
    JOIN event e ON s.sportid = e.sportid
    JOIN participation p ON e.eventid = p.eventid
    GROUP BY s.sportname
    ORDER BY athlete_count DESC
    LIMIT 5
    """
    data = execute_query(query)
    
    fig = px.bar(
        data,
        y='name',
        x='athlete_count',
        orientation='h',
        title='Top 5 Sports by Number of Athletes',
        labels={'name': 'Sport', 'athlete_count': 'Number of Athletes'},
        color='athlete_count',
        color_continuous_scale=[
            OLYMPIC_COLORS['blue'],
            OLYMPIC_COLORS['yellow'],
            OLYMPIC_COLORS['black'],
            OLYMPIC_COLORS['green'],
            OLYMPIC_COLORS['red']
        ]
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
            borderwidth=1
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_sport_distribution():
    query = """
    SELECT s.sportname as name, COUNT(DISTINCT e.eventid) as event_count
    FROM sport s
    JOIN event e ON s.sportid = e.sportid
    GROUP BY s.sportname
    """
    data = execute_query(query)
    
    fig = px.treemap(
        data,
        path=['name'],
        values='event_count',
        title='Events per Sport',
        color='event_count',
        color_continuous_scale=["#b6fcd5", "#009F3D"]
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
            borderwidth=1
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_country_map():
    # First query to check all countries (optional, keep for debugging if needed)
    # query = """
    # SELECT
    #     c.countryname as name,
    #     c.noc as noc,
    #     c.region as region
    # FROM country c
    # """
    # all_countries_data = pd.DataFrame(execute_query(query))
    # print("\nAll countries from country table:\n", all_countries_data)
    # print("\nFrench Guiana in all_countries_data:\n", all_countries_data[all_countries_data['noc'] == 'GUF'])

    # Main query for the map, joining staging_main with country
    query = """
    SELECT
        c.countryname as name,
        c.noc as noc,
        COALESCE(sm_counts.athlete_count, 0) as athlete_count,
        c.region as region
    FROM country c
LEFT JOIN (
    SELECT
        noc,
        COUNT(DISTINCT athleteid) as athlete_count
    FROM staging_main
    GROUP BY noc
) sm_counts ON c.noc = sm_counts.noc;
    """
    data = pd.DataFrame(execute_query(query))

    # Strip whitespace from country names
    data['name'] = data['name'].str.strip()


    # Define mapping from database regions to continent names and color scales
    region_mapping = {
        'North America': {'continent': 'Americas', 'scale': ['#FFE5E5', OLYMPIC_COLORS['red']]},  # Red
        'South America': {'continent': 'Americas', 'scale': ['#FFE5E5', OLYMPIC_COLORS['red']]},  # Red
        'Americas': {'continent': 'Americas', 'scale': ['#FFE5E5', OLYMPIC_COLORS['red']]}, # Add Americas mapping for exact match
        'Europe': {'continent': 'Europe', 'scale': ['#E5FFE5', OLYMPIC_COLORS['green']]},    # Green
        'Africa': {'continent': 'Africa', 'scale': ['#CCCCCC', OLYMPIC_COLORS['black']]},    # Black/Gray
        'Asia': {'continent': 'Asia', 'scale': ['#FFF9E5', OLYMPIC_COLORS['yellow']]},      # Yellow
        'Oceania': {'continent': 'Oceania', 'scale': ['#E5F5FF', OLYMPIC_COLORS['blue']]},    # Blue
        'Mixed': {'continent': 'Other', 'scale': ['#F0F0F0', '#B0F0B0']}, # Map Mixed to Other
        'Unknown': {'continent': 'Other', 'scale': ['#F0F0F0', '#B0F0B0']}, # Map Unknown to Other
        None: {'continent': 'Other', 'scale': ['#F0F0F0', '#B0F0B0']} # Map None to Other
    }

    fig = go.Figure()

    # Get unique regions from data, including None
    unique_regions_in_data = data['region'].unique()

    # Iterate through the unique regions found in the data
    for region_value in unique_regions_in_data:
        # Determine the mapping for this region value, default to 'Other' mapping if not found
        mapping = region_mapping.get(region_value, region_mapping[None])

        # Filter data for the current region value (handle None specifically)
        if region_value is None:
             region_data = data[data['region'].isnull()].copy() # Create a copy to avoid SettingWithCopyWarning
        else:
             # Exclude France from Europe and French Guiana from Americas in the main loop
             if region_value == 'Europe':
                 region_data = data[(data['region'] == region_value) & (data['name'] != 'France')].copy() # Create a copy
             elif region_value == 'Americas' or region_value == 'North America' or region_value == 'South America':
                  region_data = data[(data['region'] == region_value) & (data['name'] != 'French Guiana')].copy() # Create a copy
             else:
                 region_data = data[data['region'] == region_value].copy() # Create a copy

        # For countries with no participation data, athlete_count will be 0. Handle this for coloring.
        region_data['athlete_count'] = region_data['athlete_count'].fillna(0);

        if not region_data.empty:
            # Add print statement to inspect data for Europe region
            # if mapping['continent'] == 'Europe':
                # print("\nData for Europe region before creating trace:\n", region_data)

            fig.add_trace(go.Choropleth(
                locations=region_data['name'].tolist(), # Use list of country names for locations
                z=region_data['athlete_count'].tolist(), # Use list of athlete counts for z
                locationmode='country names', # Use country names for most countries
                name=mapping['continent'], # Use mapped continent name for legend
                colorscale=mapping['scale'],
                showscale=False, # Hide individual trace color scales
                hoverinfo='location+name+z',
                hoverlabel=dict(bgcolor='white'),
                marker=dict(line=dict(color='lightgray', width=0.5))
            ))

    # Update the layout for a minimal style and title
    fig.update_geos(
        showcoastlines=True,
        coastlinecolor='lightgray',
        showland=True,
        landcolor='#F0F0F0',
        showocean=True,
        oceancolor='#E0E0E0',
        showlakes=True,
        lakecolor='#E0E0E0',
        showcountries=True,
        countrycolor='lightgray',
        showframe=False,
        projection_type='equirectangular'
    )

    # Update the layout for light theme
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
            borderwidth=1
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        showlegend=True, # Show continent legends
        annotations=[{
            'text': 'Light → Dark shows fewer to more athletes within each continent',
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper',
            'x': 0.5,
            'y': -0.1,
            'font': {'size': 12, 'color': '#000000'}
        }]
    )

    # Keep or adjust colorscale for data representation as needed in light theme
    # fig.update_traces(colorscale='Viridis') # Example of a different colorscale

    fig.update_layout(
        dragmode='zoom'
    )

    return fig

def create_gender_participation_trend():
    query = """
    SELECT
        og.year as year,
        a.gender as gender,
        COUNT(DISTINCT p.athleteid) as athlete_count
    FROM olympicgames og
    JOIN participation p ON og.gamesid = p.gamesid
    JOIN athlete a ON p.athleteid = a.athleteid
    GROUP BY og.year, a.gender
    ORDER BY og.year, a.gender
    """
    data = execute_query(query)
    
    fig = px.line(
        data,
        x='year',
        y='athlete_count',
        color='gender',
        title='Gender Participation Evolution Over Time',
        labels={'year': 'Olympic Year', 'athlete_count': 'Number of Athletes', 'gender': 'Gender'},
        color_discrete_map={'M': OLYMPIC_COLORS['blue'], 'F': OLYMPIC_COLORS['red']}
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
            borderwidth=1
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_top_countries_by_medals():
    query = """
    SELECT 
        c.countryname,
        COUNT(m.medalid) as medal_count
    FROM country c
    JOIN team t ON c.noc = t.noc
    JOIN participation p ON t.teamid = p.teamid
    JOIN medal m ON p.medalid = m.medalid
    WHERE m.medaltype != 'None'
    GROUP BY c.countryname
    ORDER BY medal_count DESC
    LIMIT 3
    """
    data = execute_query(query)
    
    cards = []
    for index, row in enumerate(data):
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="number",
            value=row['medal_count'],
            title={"text": f"{row['countryname']}"},
            number={'font': {'size': 30}},
            domain={'row': 0, 'column': 0}
        ))
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
                borderwidth=1
            ),
            margin=dict(l=40, r=20, t=60, b=40),
            paper_bgcolor="#fff",
            plot_bgcolor="#fff",
            height=220
        )
        cards.append(fig)
    return cards

def get_continent_metrics():
    def normalize_continent(region):
        if region in ('North America', 'South America', 'Americas'):
            return 'Americas'
        elif region in ('Europe',):
            return 'Europe'
        elif region in ('Africa',):
            return 'Africa'
        elif region in ('Asia',):
            return 'Asia'
        elif region in ('Oceania',):
            return 'Oceania'
        else:
            return None

    athletes_query = '''
        SELECT c.region as continent, COUNT(DISTINCT a.athleteid) as total_athletes
        FROM country c
        JOIN team t ON c.noc = t.noc
        JOIN participation p ON t.teamid = p.teamid
        JOIN athlete a ON p.athleteid = a.athleteid
        GROUP BY c.region
    '''
    athletes = execute_query(athletes_query)
    athletes_dict = {}
    for row in athletes:
        norm = normalize_continent(row['continent'])
        if norm:
            athletes_dict[norm] = athletes_dict.get(norm, 0) + row['total_athletes']

    medals_query = '''
        SELECT c.region as continent, COUNT(m.medalid) as total_medals
        FROM country c
        JOIN team t ON c.noc = t.noc
        JOIN participation p ON t.teamid = p.teamid
        JOIN medal m ON p.medalid = m.medalid
        WHERE m.medaltype != 'None'
        GROUP BY c.region
    '''
    medals = execute_query(medals_query)
    medals_dict = {}
    for row in medals:
        norm = normalize_continent(row['continent'])
        if norm:
            medals_dict[norm] = medals_dict.get(norm, 0) + row['total_medals']

    main_continents = [
        ('Europe', 'green'),
        ('Americas', 'red'),
        ('Asia', 'yellow'),
        ('Africa', 'black'),
        ('Oceania', 'cyan'),
    ]
    tactical_colors = {
        'green':  '#4CAF50',
        'red':    '#F44336',
        'yellow': '#FFC107',
        'black':  '#000000',
        'cyan':   '#00BCD4',
    }
    metrics = []
    for continent, color_key in main_continents:
        metrics.append({
            'continent': continent,
            'athletes': athletes_dict.get(continent, 0),
            'medals': medals_dict.get(continent, 0),
            'color': tactical_colors[color_key],
            'text_color': '#222' if color_key in ['yellow', 'green'] else '#fff'
        })
    metrics = sorted(metrics, key=lambda x: x['athletes'], reverse=True)
    return metrics

def get_athlete_participation_table():
    query = '''
        SELECT 
            a.fullname AS athlete_name,
            c.countryname AS country,
            og.year AS year,
            s.sportname AS sport,
            a.gender AS gender
        FROM athlete a
        JOIN participation p ON a.athleteid = p.athleteid
        JOIN team t ON p.teamid = t.teamid
        JOIN country c ON t.noc = c.noc
        JOIN olympicgames og ON p.gamesid = og.gamesid
        JOIN event e ON p.eventid = e.eventid
        JOIN sport s ON e.sportid = s.sportid
    '''
    data = execute_query(query)
    return data

def get_analytical_dashboard():
    return {
        'summary_cards': create_analytical_summary_cards(),
        'gender_distribution': create_gender_distribution(),
        'participation_trend': create_participation_trend(),
        'top_events': create_top_events(),
        'sport_distribution': create_sport_distribution(),
        'country_map': create_country_map(),
        'gender_participation_trend': create_gender_participation_trend(),
        'top_countries_by_medals': create_top_countries_by_medals(),
        'continent_metrics': get_continent_metrics(),
        'athlete_participation_table': get_athlete_participation_table()
    } 