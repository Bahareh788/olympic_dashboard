import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from db_utils import execute_query
from components.analytical_summary_cards import create_analytical_summary_cards, create_top_kpi_cards

# Olympic colors with accessibility improvements - colorblind-friendly palette
OLYMPIC_COLORS = {
    'blue': '#2563EB',      # High contrast blue (WCAG AA compliant)
    'yellow': '#F59E0B',    # Amber/Orange (better contrast than pure yellow)
    'black': '#1F2937',     # Dark gray (better readability than pure black)
    'green': '#059669',     # Emerald green (colorblind safe)
    'red': '#DC2626'        # High contrast red (colorblind safe)
}

DEFAULT_FONT = dict(family='Inter, Montserrat, sans-serif', size=12, color='#1F2937')
TITLE_FONT = dict(family='Inter, Montserrat, sans-serif', size=15, color='#1F2937', weight=600)

def create_gender_distribution():
    query = """
    SELECT gender, COUNT(DISTINCT athleteid) as count
    FROM athlete
    GROUP BY gender
    """
    data = execute_query(query)
    
    # Map gender codes to full names
    gender_mapping = {'M': 'Male', 'F': 'Female'}
    data_mapped = []
    for row in data:
        data_mapped.append({
            'gender': gender_mapping.get(row['gender'], row['gender']),
            'count': row['count']
        })
    
    fig = px.pie(
        data_mapped,
        values='count',
        names='gender',
        title='Total Athletes by Gender',
        labels={'gender': 'Gender', 'count': 'Number of Athletes'},
        color='gender',
        color_discrete_map={'Male': OLYMPIC_COLORS['blue'], 'Female': OLYMPIC_COLORS['red']}
    )
    
    # Update traces for better tooltips
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>' +
                     'Athletes: %{value:,}<br>' +
                     'Percentage: %{percent}<br>' +
                     '<extra></extra>'
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
            title="Gender"
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        height=300
    )
    return fig

def create_filtered_gender_distribution(year=None, sport=None, country=None):
    """
    Create gender distribution chart with optional filters
    """
    base_query = """
    SELECT a.gender, COUNT(DISTINCT a.athleteid) as count
    FROM athlete a
    JOIN participation p ON a.athleteid = p.athleteid
    JOIN team t ON p.teamid = t.teamid
    JOIN country c ON t.noc = c.noc
    JOIN olympicgames og ON p.gamesid = og.gamesid
    JOIN event e ON p.eventid = e.eventid
    JOIN sport s ON e.sportid = s.sportid
    WHERE 1=1
    """
    
    conditions = []
    
    if year and year != 'All':
        conditions.append(f"og.year = {year}")
    
    if sport:
        conditions.append(f"s.sportname = '{sport.replace(chr(39), chr(39)+chr(39))}'")
    
    if country:
        conditions.append(f"c.countryname = '{country.replace(chr(39), chr(39)+chr(39))}'")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " GROUP BY a.gender"
    
    try:
        data = execute_query(base_query)
        if not data:
            return create_gender_distribution()  # Fallback to unfiltered
            
        # Map gender codes to full names
        gender_mapping = {'M': 'Male', 'F': 'Female'}
        data_mapped = []
        for row in data:
            data_mapped.append({
                'gender': gender_mapping.get(row['gender'], row['gender']),
                'count': row['count']
            })
        
        fig = px.pie(
            data_mapped,
            values='count',
            names='gender',
            title=f'Athletes by Gender{" (Filtered)" if any([year and year != "All", sport, country]) else ""}',
            labels={'gender': 'Gender', 'count': 'Number of Athletes'},
            color='gender',
            color_discrete_map={'Male': OLYMPIC_COLORS['blue'], 'Female': OLYMPIC_COLORS['red']}
        )
        
        # Update traces for better tooltips
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>' +
                         'Athletes: %{value:,}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
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
                title="Gender"
            ),
            margin=dict(l=40, r=20, t=60, b=40),
            paper_bgcolor="#fff",
            plot_bgcolor="#fff",
            height=300
        )
        return fig
        
    except Exception as e:
        print(f"Error in filtered gender distribution: {e}")
        return create_gender_distribution()

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
        title='Total Athlete Participation Over Time',
        labels={
            'year': 'Olympic Year', 
            'athlete_count': 'Number of Athletes'
        }
    )
    
    # Update traces for better styling and tooltips
    fig.update_traces(
        line_color=OLYMPIC_COLORS['blue'],
        line_width=3,
        hovertemplate='<b>Olympic Year: %{x}</b><br>' +
                     'Total Athletes: %{y:,}<br>' +
                     '<extra></extra>'
    )
    
    # Update axes
    fig.update_xaxes(
        title_text="Olympic Year",
        title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        showgrid=True,
        gridcolor='#f0f0f0'
    )
    
    fig.update_yaxes(
        title_text="Number of Athletes",
        title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        showgrid=True,
        gridcolor='#f0f0f0',
        tickformat=',d'  # Format numbers with commas
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

def create_filtered_participation_trend(gender=None, sport=None, country=None):
    """
    Create participation trend chart with optional filters
    """
    base_query = """
    SELECT og.year as year, COUNT(DISTINCT p.athleteid) as athlete_count
    FROM olympicgames og
    JOIN participation p ON og.gamesid = p.gamesid
    JOIN athlete a ON p.athleteid = a.athleteid
    JOIN team t ON p.teamid = t.teamid
    JOIN country c ON t.noc = c.noc
    JOIN event e ON p.eventid = e.eventid
    JOIN sport s ON e.sportid = s.sportid
    WHERE 1=1
    """
    
    conditions = []
    
    if gender:
        conditions.append(f"a.gender = '{gender}'")
    
    if sport:
        conditions.append(f"s.sportname = '{sport.replace(chr(39), chr(39)+chr(39))}'")
    
    if country:
        conditions.append(f"c.countryname = '{country.replace(chr(39), chr(39)+chr(39))}'")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " GROUP BY og.year ORDER BY og.year"
    
    try:
        data = execute_query(base_query)
        if not data:
            return create_participation_trend()  # Fallback
            
        fig = px.line(
            data,
            x='year',
            y='athlete_count',
            title=f'Athlete Participation Over Time{" (Filtered)" if any([gender, sport, country]) else ""}',
            labels={
                'year': 'Olympic Year', 
                'athlete_count': 'Number of Athletes'
            }
        )
        
        # Update traces for better styling and tooltips
        fig.update_traces(
            line_color=OLYMPIC_COLORS['blue'],
            line_width=3,
            hovertemplate='<b>Olympic Year: %{x}</b><br>' +
                         'Total Athletes: %{y:,}<br>' +
                         '<extra></extra>'
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="Olympic Year",
            title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            showgrid=True,
            gridcolor='#f0f0f0'
        )
        
        fig.update_yaxes(
            title_text="Number of Athletes",
            title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            showgrid=True,
            gridcolor='#f0f0f0',
            tickformat=',d'  # Format numbers with commas
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
        
    except Exception as e:
        print(f"Error in filtered participation trend: {e}")
        return create_participation_trend()

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
        labels={
            'name': 'Sport', 
            'athlete_count': 'Number of Athletes'
        },
        color='athlete_count',
        color_continuous_scale=[
            '#EFF6FF',      # Light blue
            '#3B82F6',      # Medium blue  
            '#1D4ED8',      # Darker blue
            '#1E40AF',      # Even darker blue
            '#1E3A8A'       # Darkest blue
        ]
    )
    
    # Update traces for better tooltips
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>' +
                     'Athletes: %{x:,}<br>' +
                     '<extra></extra>'
    )
    
    # Update axes
    fig.update_xaxes(
        title_text="Number of Athletes",
        title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        showgrid=True,
        gridcolor='#f0f0f0',
        tickformat=',d'  # Format numbers with commas
    )
    
    fig.update_yaxes(
        title_text="Sport",
        title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        showgrid=False
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
        height=300,
        showlegend=False  # Hide colorbar legend for cleaner look
    )
    return fig

def create_filtered_top_events(year=None, gender=None, country=None):
    """
    Create top events chart with optional filters
    """
    base_query = """
    SELECT s.sportname as name, COUNT(DISTINCT p.athleteid) as athlete_count
    FROM sport s
    JOIN event e ON s.sportid = e.sportid
    JOIN participation p ON e.eventid = p.eventid
    JOIN athlete a ON p.athleteid = a.athleteid
    JOIN team t ON p.teamid = t.teamid
    JOIN country c ON t.noc = c.noc
    JOIN olympicgames og ON p.gamesid = og.gamesid
    WHERE 1=1
    """
    
    conditions = []
    
    if year and year != 'All':
        conditions.append(f"og.year = {year}")
    
    if gender:
        conditions.append(f"a.gender = '{gender}'")
    
    if country:
        conditions.append(f"c.countryname = '{country.replace(chr(39), chr(39)+chr(39))}'")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += """
    GROUP BY s.sportname
    ORDER BY athlete_count DESC
    LIMIT 5
    """
    
    try:
        data = execute_query(base_query)
        if not data:
            return create_top_events()  # Fallback
            
        fig = px.bar(
            data,
            y='name',
            x='athlete_count',
            orientation='h',
            title=f'Top 5 Sports by Athletes{" (Filtered)" if any([year and year != "All", gender, country]) else ""}',
            labels={
                'name': 'Sport', 
                'athlete_count': 'Number of Athletes'
            },
            color='athlete_count',
            color_continuous_scale=[
                '#EFF6FF',      # Light blue
                '#3B82F6',      # Medium blue  
                '#1D4ED8',      # Darker blue
                '#1E40AF',      # Even darker blue
                '#1E3A8A'       # Darkest blue
            ]
        )
        
        # Update traces for better tooltips
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>' +
                         'Athletes: %{x:,}<br>' +
                         '<extra></extra>'
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="Number of Athletes",
            title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            showgrid=True,
            gridcolor='#f0f0f0',
            tickformat=',d'  # Format numbers with commas
        )
        
        fig.update_yaxes(
            title_text="Sport",
            title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            showgrid=False
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
            height=300,
            showlegend=False  # Hide colorbar legend for cleaner look
        )
        return fig
        
    except Exception as e:
        print(f"Error in filtered top events: {e}")
        return create_top_events()

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
        labels={
            'name': 'Sport',
            'event_count': 'Number of Events'
        },
        color='event_count',
        color_continuous_scale=["#F0FDF4", "#059669"]  # Light green to accessible dark green
    )
    
    # Update traces for better tooltips
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>' +
                     'Events: %{value:,}<br>' +
                     'Percentage: %{percentParent}<br>' +
                     '<extra></extra>',
        textinfo="label+value",
        textfont_size=10
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
        height=300,
        coloraxis_colorbar=dict(
            title="Number of Events",
            title_font=dict(size=12, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            tickfont=dict(size=10, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            tickformat=',d'
        )
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
                hovertemplate='<b>%{location}</b><br>' +
                             'Continent: ' + mapping['continent'] + '<br>' +
                             'Athletes: %{z:,}<br>' +
                             '<extra></extra>',
                hoverlabel=dict(bgcolor='white', font_size=11),
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
        title="Olympic Athlete Participation by Country and Continent",
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
            title="Continent"
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        showlegend=True, # Show continent legends
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
    
    # Map gender codes to full names
    gender_mapping = {'M': 'Male', 'F': 'Female'}
    data_mapped = []
    for row in data:
        data_mapped.append({
            'year': row['year'],
            'gender': gender_mapping.get(row['gender'], row['gender']),
            'athlete_count': row['athlete_count']
        })
    
    fig = px.line(
        data_mapped,
        x='year',
        y='athlete_count',
        color='gender',
        title='Gender Participation Evolution Over Time',
        labels={
            'year': 'Olympic Year', 
            'athlete_count': 'Number of Athletes', 
            'gender': 'Gender'
        },
        color_discrete_map={'Male': OLYMPIC_COLORS['blue'], 'Female': OLYMPIC_COLORS['red']}
    )
    
    # Update traces for better styling and tooltips
    fig.update_traces(
        line_width=3,
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Olympic Year: %{x}<br>' +
                     'Athletes: %{y:,}<br>' +
                     '<extra></extra>'
    )
    
    # Update axes
    fig.update_xaxes(
        title_text="Olympic Year",
        title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        showgrid=True,
        gridcolor='#f0f0f0'
    )
    
    fig.update_yaxes(
        title_text="Number of Athletes",
        title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
        showgrid=True,
        gridcolor='#f0f0f0',
        tickformat=',d'  # Format numbers with commas
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
            title="Gender"
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
        ('Oceania', 'blue'),
    ]
    # Updated accessible colors with better contrast ratios
    tactical_colors = {
        'green':  '#059669',  # Emerald green (colorblind safe)
        'red':    '#DC2626',  # High contrast red
        'yellow': '#F59E0B',  # Amber/Orange (better than pure yellow)
        'black':  '#1F2937',  # Dark gray (better readability)
        'blue':   '#2563EB',  # High contrast blue
    }
    metrics = []
    for continent, color_key in main_continents:
        # Improved text contrast logic
        text_color = '#FFFFFF' if color_key in ['black', 'green', 'red', 'blue'] else '#1F2937'
        metrics.append({
            'continent': continent,
            'athletes': athletes_dict.get(continent, 0),
            'medals': medals_dict.get(continent, 0),
            'color': tactical_colors[color_key],
            'text_color': text_color
        })
    metrics = sorted(metrics, key=lambda x: x['athletes'], reverse=True)
    return metrics

def get_athlete_participation_table():
    query = '''
        SELECT DISTINCT
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
        ORDER BY a.fullname, og.year, s.sportname
    '''
    data = execute_query(query)
    return data

def create_filtered_gender_participation_trend(year=None, sport=None, country=None, gender=None):
    """
    Create gender participation trend chart with optional filters
    This maintains the gender breakdown showing both male and female lines, unless a specific gender is filtered
    """
    base_query = """
    SELECT
        og.year as year,
        a.gender as gender,
        COUNT(DISTINCT p.athleteid) as athlete_count
    FROM olympicgames og
    JOIN participation p ON og.gamesid = p.gamesid
    JOIN athlete a ON p.athleteid = a.athleteid
    JOIN team t ON p.teamid = t.teamid
    JOIN country c ON t.noc = c.noc
    JOIN event e ON p.eventid = e.eventid
    JOIN sport s ON e.sportid = s.sportid
    WHERE 1=1
    """
    
    conditions = []
    
    # Note: We don't filter by year since year is the x-axis
    # If gender is specified, filter by that gender, otherwise show both
    
    if gender:
        conditions.append(f"a.gender = '{gender}'")
    
    if sport:
        conditions.append(f"s.sportname = '{sport.replace(chr(39), chr(39)+chr(39))}'")
    
    if country:
        conditions.append(f"c.countryname = '{country.replace(chr(39), chr(39)+chr(39))}'")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " GROUP BY og.year, a.gender ORDER BY og.year, a.gender"
    
    try:
        data = execute_query(base_query)
        if not data:
            return create_gender_participation_trend()  # Fallback
            
        # Map gender codes to full names
        gender_mapping = {'M': 'Male', 'F': 'Female'}
        data_mapped = []
        for row in data:
            data_mapped.append({
                'year': row['year'],
                'gender': gender_mapping.get(row['gender'], row['gender']),
                'athlete_count': row['athlete_count']
            })
        
        fig = px.line(
            data_mapped,
            x='year',
            y='athlete_count',
            color='gender',
            title=f'Gender Participation Over Time{" (Filtered)" if any([gender, sport, country]) else ""}',
            labels={
                'year': 'Olympic Year', 
                'athlete_count': 'Number of Athletes', 
                'gender': 'Gender'
            },
            color_discrete_map={'Male': OLYMPIC_COLORS['blue'], 'Female': OLYMPIC_COLORS['red']}
        )
        
        # Update traces for better styling and tooltips
        fig.update_traces(
            line_width=3,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Olympic Year: %{x}<br>' +
                         'Athletes: %{y:,}<br>' +
                         '<extra></extra>'
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="Olympic Year",
            title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            showgrid=True,
            gridcolor='#f0f0f0'
        )
        
        fig.update_yaxes(
            title_text="Number of Athletes",
            title_font=dict(size=13, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            tickfont=dict(size=11, color='#1F2937', family='Inter, Montserrat, sans-serif'),
            showgrid=True,
            gridcolor='#f0f0f0',
            tickformat=',d'  # Format numbers with commas
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
                title="Gender"
            ),
            margin=dict(l=40, r=20, t=60, b=40),
            paper_bgcolor="#fff",
            plot_bgcolor="#fff",
            height=300
        )
        return fig
        
    except Exception as e:
        print(f"Error in filtered gender participation trend: {e}")
        return create_gender_participation_trend()

def get_analytical_dashboard():
    return {
        'top_kpi_cards': create_top_kpi_cards(),
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