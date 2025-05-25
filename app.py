import dash
from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from analytical_dashboard import get_analytical_dashboard
from tactical_dashboard import get_tactical_dashboard
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from db_utils import execute_query
from dash.dependencies import Input, Output, State

# Initialize Flask app
server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Bahardb1234@localhost:5432/Olympicdb'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)

# Initialize Dash app
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap'
    ],
    suppress_callback_exceptions=True
)

# Custom CSS for light theme
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Montserrat', sans-serif;
                background-color: #e9ecef;
                color: #000000;
                font-size: 1.1rem;
            }
            .card {
                background-color: #FFFFFF !important;
                border: 1px solid #E0E0E0 !important;
                border-radius: 10px !important;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important;
                margin-bottom: 1.5rem !important;
                padding: 1rem !important;
            }
            .card:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
            }
            .sidebar-link {
                transition: all 0.3s ease !important;
                color: #00274D !important;
            }
            .sidebar-link:hover {
                background-color: #E0E0E0 !important;
                transform: translateX(5px) !important;
            }
            .dropdown-menu {
                background-color: #FFFFFF !important;
                border: 1px solid #E0E0E0 !important;
            }
            .dropdown-item {
                color: #000000 !important;
            }
            .dropdown-item:hover {
                background-color: #F0F0F0 !important;
            }
             .Select-control {
                background-color: #FFFFFF !important;
                border: 1px solid #E0E0E0 !important;
                color: #000000 !important;
            }
            .Select-value-label {
                color: #000000 !important;
            }
            .Select-arrow {
                 color: #000000 !important;
            }
            .Select-menu-outer {
                background-color: #FFFFFF !important;
                border: 1px solid #E0E0E0 !important;
            }
            .Select-option {
                background-color: #FFFFFF !important;
                color: #000000 !important;
            }
            .Select-option:hover {
                background-color: #F0F0F0 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Print the result (for now, as requested)
# print("Distinct Canadian Athlete Count:", canada_athlete_count_result)

# Get dashboard figures
analyical_figures = get_analytical_dashboard()
tactical_figures = get_tactical_dashboard()

# Extract unique filter values from athlete participation data
athlete_participation_data = analyical_figures['athlete_participation_table']
unique_years = sorted({row['year'] for row in athlete_participation_data})
unique_genders = sorted({row['gender'] for row in athlete_participation_data})
unique_sports = sorted({row['sport'] for row in athlete_participation_data})
unique_countries = sorted({row['country'] for row in athlete_participation_data})

# Helper for summary card layout
summary_card_data_analytical = [
    {"icon": "fas fa-cogs", "color": "#DF0024", "bgcolor": "#FFE5E5", "title": "AMERICAS", "value": analyical_figures['summary_cards'][0].data[0]['value']},
    {"icon": "fas fa-users", "color": "#009F3D", "bgcolor": "#E5FFE5", "title": "EUROPE", "value": analyical_figures['summary_cards'][1].data[0]['value']},
    {"icon": "fas fa-globe-africa", "color": "#000000", "bgcolor": "#CCCCCC", "title": "AFRICA", "value": analyical_figures['summary_cards'][2].data[0]['value']},
    {"icon": "fas fa-globe-asia", "color": "#F4C300", "bgcolor": "#FFF9E5", "title": "ASIA", "value": analyical_figures['summary_cards'][3].data[0]['value']},
    # If you have Oceania as a card, add:
    # {"icon": "fas fa-water", "color": "#0085C3", "bgcolor": "#E5F5FF", "title": "OCEANIA", "value": ...},
]

def make_summary_card(icon, color, title, value, bgcolor):
    return html.Div([
        html.Div(html.I(className=icon), className="summary-card-icon", style={"background": color}),
        html.Div([
            html.Div(title, className="summary-card-title", style={"color": color}),
            html.Div(value, className="summary-card-value", style={"color": color}),
        ], className="summary-card-content")
    ], className="summary-card", style={"background": bgcolor})

# Analytical Summary Cards Row (custom layout)
analyical_summary_cards_row = html.Div([
    make_summary_card(card["icon"], card["color"], card["title"], card["value"], card["bgcolor"])
    for card in summary_card_data_analytical
], className="summary-cards-row")

# Add after analyical_figures = get_analytical_dashboard()
continent_icons = {
    'Africa': 'fas fa-globe-africa',
    'Americas': 'fas fa-globe-americas',
    'Asia': 'fas fa-globe-asia',
    'Europe': 'fas fa-globe-europe',
    'Oceania': 'fas fa-water',
}

def make_continent_metric_card(continent, athletes, medals, color, text_color):
    icon = continent_icons.get(continent, 'fas fa-globe')
    icon_style = {"color": color, "--icon": color}
    return html.Div([
        html.Div([
            html.I(className=icon)
        ], className="continent-metric-flat-icon", style=icon_style),
        html.Div([
            html.Div(continent, className="continent-metric-flat-title", style={"color": text_color}),
            html.Div(f"{athletes:,}", className="continent-metric-flat-value", style={"color": text_color}),
            html.Div(f"Medals: {medals:,}", className="continent-metric-flat-row", style={"color": text_color}),
        ], className="continent-metric-flat-content"),
        html.Div(className="continent-metric-flat-bar")
    ], className="continent-metric-flat-card", style={"background": color, "--bg": color})

continent_metrics_cards = [
    make_continent_metric_card(
        m['continent'], m['athletes'], m['medals'], m['color'], m['text_color']
    )
    for m in analyical_figures['continent_metrics']
]

# Define the sidebar layout
sidebar = html.Div(
    [
        html.Button(
            html.Span(className="navbar-toggler-icon"),
            className="navbar-toggler",
            id="sidebar-toggle",
            style={'color': '#00274D', 'borderColor': 'rgba(0,0,0,.1)'}
        ),
        dbc.Collapse(
            [
                html.Div(
                    html.Img(
                        src='/assets/Untitled design.png',
                        style={'width': '80%', 'margin': 'auto', 'display': 'block'}
                    ),
                    className="text-center my-3"
                ),
                html.H2("Olympic Dashboard", className="display-6 text-center my-2", 
                       style={'color': '#00274D', 'fontFamily': 'Montserrat, sans-serif', 'fontSize': '1.8rem'}),
                html.Hr(className="my-2", style={'borderColor': 'rgba(0,39,77,.1)'}),
                dbc.Nav(
                    [
                        dbc.NavLink(
                            [
                                html.I(className="fas fa-chart-bar me-2"),
                                "Analytical Dashboard"
                            ],
                            href="/analytical",
                            active="exact",
                            id="nav-analytical",
                            className="sidebar-link",
                            style={'backgroundColor': '#FFFFFF', 'color': '#00274D', 'borderRadius': '10px', 
                                  'margin': '5px 0', 'padding': '10px 15px'}
                        ),
                        dbc.NavLink(
                            [
                                html.I(className="fas fa-medal me-2"),
                                "Tactical Dashboard"
                            ],
                            href="/tactical",
                            active="exact",
                            id="nav-tactical",
                            className="sidebar-link",
                            style={'backgroundColor': '#FFFFFF', 'color': '#00274D', 'borderRadius': '10px', 
                                  'margin': '5px 0', 'padding': '10px 15px'}
                        ),
                    ],
                    vertical=True,
                    pills=True,
                    className="mb-4",
                ),
                html.Hr(className="my-2", style={'borderColor': 'rgba(0,0,0,.1)'}),
                html.P("Filters", className="lead", 
                      style={'color': '#00274D', 'fontSize': '1.2rem', 'marginTop': '15px'}),
                # Filter Dropdowns
                html.Div([
                    # Year Filter
                    html.Div("Year", className="lead", 
                           style={'color': '#00274D', 'fontSize': '1rem', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='athlete-table-year',
                        options=[{'label': str(i), 'value': i} for i in range(1896, 2021, 2)] + 
                               [{'label': 'All', 'value': 'All'}],
                        value='All',
                        clearable=False,
                        style={'marginBottom': '15px', 'borderRadius': '10px'}
                    ),
                    # Gender Filter
                    html.Div("Gender", className="lead", 
                           style={'color': '#00274D', 'fontSize': '1rem', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='athlete-table-gender',
                        options=[{'label': g, 'value': g} for g in unique_genders],
                        placeholder='Gender',
                        clearable=True,
                        style={'marginBottom': '15px', 'borderRadius': '10px'}
                    ),
                    # Sport Filter
                    html.Div("Sport", className="lead", 
                           style={'color': '#00274D', 'fontSize': '1rem', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='athlete-table-sport',
                        options=[{'label': s, 'value': s} for s in unique_sports],
                        placeholder='Sport',
                        clearable=True,
                        style={'marginBottom': '15px', 'borderRadius': '10px'}
                    ),
                     # Country Filter
                    html.Div("Country/NOC", className="lead", 
                           style={'color': '#00274D', 'fontSize': '1rem', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='athlete-table-country',
                        options=[{'label': c, 'value': c} for c in unique_countries],
                        placeholder='Country/NOC',
                        clearable=True,
                        style={'marginBottom': '15px', 'borderRadius': '10px'}
                    ),
                ])
            ],
            id="sidebar-collapse",
            is_open=True,
        ),
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "12rem",
        "padding": "1.5rem 1rem",
        "background": "#F8F9FA",
        "color": "#00274D",
        "zIndex": 1,
        "fontFamily": 'Montserrat, sans-serif'
    },
)

# --- Analytical Athlete Participation Table ---
athlete_participation_data = analyical_figures['athlete_participation_table']

# Extract unique filter values
unique_years = sorted({row['year'] for row in athlete_participation_data})
unique_genders = sorted({row['gender'] for row in athlete_participation_data})
unique_sports = sorted({row['sport'] for row in athlete_participation_data})
unique_countries = sorted({row['country'] for row in athlete_participation_data})

olympic_palette = ['#0085C3', '#F4C300', '#000000', '#009F3D', '#DF0024']

analyical_athlete_table_layout = html.Div([
    html.H4("Athlete Participation Table", style={
        "marginTop": "2rem",
        "marginBottom": "1rem",
        "fontWeight": "bold",
        "fontFamily": "Montserrat, sans-serif",
        "fontSize": "16px",
        "color": "#222"
    }),
    dash_table.DataTable(
        id='athlete-participation-table',
        columns=[
            {"name": "Athlete Name", "id": "athlete_name"},
            {"name": "Country", "id": "country"},
            {"name": "Year", "id": "year", "type": "numeric"},
            {"name": "Sport", "id": "sport"},
            {"name": "Gender", "id": "gender"},
        ],
        data=athlete_participation_data,
        page_size=15,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_selectable="single",
        style_table={
            "maxHeight": "400px",
            "overflowY": "auto",
            "minWidth": "100%",
            "background": "#fff",
            "borderRadius": "14px",
            "boxShadow": "0 2px 12px rgba(0,0,0,0.10)",
            "padding": "1.5rem 1.5rem 1rem 1.5rem"
        },
        style_cell={
            "padding": "0.7rem",
            "fontSize": "1.1rem",
            "textAlign": "left",
            "fontFamily": "Montserrat, Roboto, sans-serif",
            "background": "#fff"
        },
        style_header={
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold",
            "fontFamily": "Montserrat, Roboto, sans-serif",
            "fontSize": "1.1rem",
            "color": "#00274D"
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#f6f8fa"},
            {"if": {"state": "selected"}, "backgroundColor": olympic_palette[0], "color": "#fff"},
        ],
        page_action="native",
        fixed_rows={"headers": True},
        style_as_list_view=True,
    )
], style={"background": "#fff", "borderRadius": "14px", "boxShadow": "0 2px 12px rgba(0,0,0,0.10)", "padding": "1.5rem 1.5rem 1rem 1.5rem", "marginTop": "2rem", "marginBottom": "2rem"})

@app.callback(
    Output('athlete-participation-table', 'data'),
    [
        Input('athlete-table-year', 'value'),
        Input('athlete-table-gender', 'value'),
        Input('athlete-table-sport', 'value'),
        Input('athlete-table-country', 'value'),
    ]
)
def update_athlete_participation_table(year, gender, sport, country):
    filtered = athlete_participation_data
    if year and year != 'All':
        filtered = [row for row in filtered if row['year'] == year]
    if gender:
        filtered = [row for row in filtered if row['gender'] == gender]
    if sport:
        filtered = [row for row in filtered if row['sport'] == sport]
    if country:
        filtered = [row for row in filtered if row['country'] == country]
    return filtered

def extract_title_text(fig, prefix):
    title = getattr(getattr(fig.layout, 'title', None), 'text', None)
    if title and '<br>' in title:
        return f"{prefix}: {title.split('<br>')[1]}"
    return prefix

# Tactical summary card styles (defined before use)
tactical_summary_card_styles = [
    {"icon": "fas fa-medal", "color": "#00BCD4", "bgcolor": "#00BCD4", "title": "Total Medals"},
    {"icon": "fas fa-trophy", "color": "#F44336", "bgcolor": "#F44336", "title": "Gold Medals"},
    {"icon": "fas fa-flag", "color": "#4CAF50", "bgcolor": "#4CAF50", "title": "Top Country"},
    {"icon": "fas fa-user", "color": "#FFC107", "bgcolor": "#FFC107", "title": "Top Athlete"},
]

# Tactical summary cards
summary_card_data_tactical = [
    {"icon": "fas fa-medal", "color": "#00BCD4", "bgcolor": "#FFFFFF", "title": "Total Medals", "value_data": tactical_figures['summary_cards'][0]['value']},
    {"icon": "fas fa-trophy", "color": "#F44336", "bgcolor": "#FFFFFF", "title": "Gold Medals", "value_data": tactical_figures['summary_cards'][1]['value']},
    {"icon": "fas fa-flag", "color": "#4CAF50", "bgcolor": "#FFFFFF", "title": "Top Country", "value_data": {'name': tactical_figures['summary_cards'][2]['name'], 'count': tactical_figures['summary_cards'][2]['value']}},
    {"icon": "fas fa-user", "color": "#FFC107", "bgcolor": "#FFFFFF", "title": "Top Athlete", "value_data": {'name': tactical_figures['summary_cards'][3]['name'], 'count': tactical_figures['summary_cards'][3]['value']}},
]

def make_tactical_summary_card(icon, color, card_title, card_value, bgcolor):
    # Debugging print statement
    # print(f"Making card - Title: {card_title}, Value: {card_value}")
    
    display_title = card_title
    display_main_content = ""
    
    # Handle different types of card values
    if isinstance(card_value, dict) and 'name' in card_value and 'count' in card_value:
        # Complex card (Top Country or Top Athlete)
        display_main_content = f"{card_value['name']} ({card_value['count']:,})"
    else:
        # Simple card (Total Medals or Gold Medals)
        display_main_content = f"{card_value:,}"

    return html.Div([
        html.Div(html.I(className=icon), style={
            "background": color,
            "color": "#fff",
            "width": "56px",
            "height": "56px",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "fontSize": "2rem",
            "borderRadius": "12px 0 0 12px",
            "marginRight": "1rem"
        }),
        html.Div([
            html.Div(display_title, style={"fontWeight": "bold", "fontSize": "1.1rem", "color": "#fff", "marginBottom": "0.2rem"}),
            html.Div(display_main_content, style={"fontWeight": "bold", "fontSize": "1.3rem", "color": "#fff"}),
        ], style={"display": "flex", "flexDirection": "column", "justifyContent": "center"})
    ], style={
        "display": "flex",
        "alignItems": "center",
        "background": bgcolor,
        "borderRadius": "12px",
        "boxShadow": "0 2px 12px rgba(0,0,0,0.10)",
        "padding": "1rem 1.2rem",
        "marginBottom": "0.7rem",
        "minWidth": "220px",
        "maxWidth": "340px",
        "width": "100%"
    })

tactical_summary_cards_row = html.Div([
    make_tactical_summary_card(
        tactical_summary_card_styles[i]["icon"],
        tactical_summary_card_styles[i]["color"],
        tactical_summary_card_styles[i]["title"],
        card["value_data"],
        tactical_summary_card_styles[i]["bgcolor"]
    )
    for i, card in enumerate(summary_card_data_tactical)
], style={"display": "flex", "gap": "1.5rem", "marginBottom": "2rem"})

# Deep dive table for tactical dashboard
noc_medal_table = tactical_figures['noc_medal_table']
deep_dive_table = html.Div([
    html.H4("All NOC by Medals", style={
        "marginTop": "2rem",
        "marginBottom": "1rem",
        "fontWeight": "bold",
        "fontFamily": "Montserrat, Roboto, sans-serif",
        "fontSize": "16px",
        "color": "#222"
    }),
    html.Div([
        dash_table.DataTable(
            columns=[
                {"name": "Team/NOC", "id": "team_noc"},
                {"name": "Gold", "id": "gold", "type": "numeric"},
                {"name": "Silver", "id": "silver", "type": "numeric"},
                {"name": "Bronze", "id": "bronze", "type": "numeric"},
            ],
            data=noc_medal_table,
            sort_action="native",
            style_table={
                "maxHeight": "400px",
                "overflowY": "auto",
                "minWidth": "100%",
                "background": "#fff",
                "borderRadius": "14px",
                "boxShadow": "0 2px 12px rgba(0,0,0,0.10)",
                "padding": "1.5rem 1.5rem 1rem 1.5rem"
            },
            style_cell={
                "padding": "0.7rem",
                "fontSize": "1.1rem",
                "textAlign": "left",
                "fontFamily": "Montserrat, sans-serif",
                "background": "#fff"
            },
            style_header={
                "backgroundColor": "#f8f9fa",
                "fontWeight": "bold",
                "fontFamily": "Montserrat, sans-serif",
                "fontSize": "1.1rem",
                "color": "#00274D"
            },
            style_data_conditional=[
                {"if": {"column_id": "gold"}, "color": "#FFD700", "fontWeight": "bold"},
                {"if": {"column_id": "silver"}, "color": "#C0C0C0", "fontWeight": "bold"},
                {"if": {"column_id": "bronze"}, "color": "#CD7F32", "fontWeight": "bold"},
            ],
            page_action="none",
            fixed_rows={"headers": True},
        )
    ], style={
        "background": "#fff",
        "borderRadius": "14px",
        "boxShadow": "0 2px 12px rgba(0,0,0,0.10)",
        "padding": "1.5rem 1.5rem 1rem 1.5rem"
    })
], style={"marginTop": "2rem", "marginBottom": "2rem"})

# Move this block up, before analyical_content_layout and tactical_content_layout definitions:
dashboard_header = dbc.Row([
    # Left section: Breadcrumb and Title
    dbc.Col([
        html.Div([
            html.I(className="bi bi-house-door me-1"),
            html.Span("/", className="mx-1 text-secondary"),
            html.Span("Dashboard", className="fw-medium")
        ], className="d-flex align-items-center small"),
        html.H1("Dashboard", className="fw-bold fs-4 mb-0", style={"marginTop": "0.3rem"}),
    ], width=True, className="d-flex flex-column justify-content-center"), # Use width=True for auto-sizing and flex for alignment

    # Right section: Search and Icons
    dbc.Col([
        dbc.InputGroup(
            [
                dbc.Input(placeholder="Search", type="text", style={"fontFamily": "Montserrat, Roboto, sans-serif", "fontSize": "0.9rem", "borderRadius": "7px 0 0 7px"}),
                dbc.Button(html.I(className="bi bi-search"), outline=True, color="secondary", className="border border-start-0 rounded-end-pill", style={"border-color": "#d1d5db", "--bs-border-color": "#d1d5db", "--bs-btn-border-color": "#d1d5db"})
            ],
            className="me-3", style={"width": "250px"}
        ),
        html.I(className="bi bi-person fs-5 me-3"),
        html.I(className="bi bi-gear fs-5 me-3"),
        html.Span([
            html.I(className="bi bi-bell fs-5"),
            html.Span("", style={"display": "inline-block", "width": "8px", "height": "8px", "background": "#ff4d4f", "borderRadius": "50%", "position": "relative", "top": "-8px", "right": "8px"})
        ], className="position-relative"), # Added position-relative for red dot positioning
    ], width="auto", className="d-flex align-items-center"), # Use width="auto" and flex for alignment

], className="mb-4 border-bottom pb-3 d-flex align-items-center", style={"fontFamily": "Montserrat, Roboto, sans-serif"}) # Added d-flex align-items-center and border-bottom for styling

# Define the analytical dashboard content layout
analyical_content_layout = html.Div([
    dashboard_header,
    # Map and Continent Metric Cards Row - Updated with flexbox layout
    html.Div([
        # Map container
        html.Div([
            dcc.Graph(
                figure=analyical_figures['country_map'],
                style={
                    "height": "100%",
                    "minHeight": "500px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], style={
            "flex": "2",
            "minWidth": "0",  # Prevents flex item from overflowing
            "marginRight": "2rem"
        }),
        # Continent cards container
        html.Div([
            html.Div(
                continent_metrics_cards,
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "1rem",
                    "height": "100%",
                    "justifyContent": "space-between"
                }
            )
        ], style={
            "flex": "1",
            "minWidth": "300px",
            "maxWidth": "400px"
        })
    ], style={
        "display": "flex",
        "gap": "2rem",
        "marginBottom": "2rem",
        "flexWrap": "wrap",  # Allows wrapping on smaller screens
        "alignItems": "stretch"  # Makes both containers same height
    }),
    # Rest of the dashboard content
    # Row 1: Total Athletes by Gender and Gender Participation Evolution Over Time
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=analyical_figures['gender_distribution'],
                style={
                    "height": "440px",
                    "minHeight": "340px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], width={"size": 6, "sm": 12, "md": 6, "lg": 6}, style={"minWidth": 0}),
        dbc.Col([
            dcc.Graph(
                figure=analyical_figures['gender_participation_trend'],
                style={
                    "height": "440px",
                    "minHeight": "340px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], width={"size": 6, "sm": 12, "md": 6, "lg": 6}, style={"minWidth": 0})
    ], className="mb-4"),
    # Row 2: Events per Sport and Top 5 Events
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=analyical_figures['sport_distribution'],
                style={
                    "height": "440px",
                    "minHeight": "340px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], width={"size": 6, "sm": 12, "md": 6, "lg": 6}, style={"minWidth": 0}),
        dbc.Col([
            dcc.Graph(
                figure=analyical_figures['top_events'],
                style={
                    "height": "440px",
                    "minHeight": "340px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], width={"size": 6, "sm": 12, "md": 6, "lg": 6}, style={"minWidth": 0})
    ]),
    # Athlete Participation Table
    analyical_athlete_table_layout
], style={
    "maxWidth": "1800px",  # Maximum width for very large screens
    "margin": "0 auto",    # Center the content
    "padding": "0 1rem"    # Add some padding on the sides
})

# Define the tactical dashboard content layout
tactical_content_layout = html.Div([
    dashboard_header,
    tactical_summary_cards_row,
    # Row 1: Medals by Country and Gender (left), Teams with Most Gold Medals (right) - Updated with flexbox
    html.Div([
        # Medals by Country and Gender container
        html.Div([
            dcc.Graph(
                figure=tactical_figures['medal_by_country_gender'],
                config={"displayModeBar": False},
                style={
                    "height": "100%",
                    "minHeight": "500px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], style={
            "flex": "1.5",
            "minWidth": "0",  # Prevents flex item from overflowing
            "marginRight": "2rem"
        }),
        # Teams with Most Gold Medals container
        html.Div([
            dcc.Graph(
                figure=tactical_figures['gold_medal_teams'],
                config={"displayModeBar": False},
                style={
                    "height": "100%",
                    "minHeight": "500px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], style={
            "flex": "1",
            "minWidth": "300px",
            "maxWidth": "500px"
        })
    ], style={
        "display": "flex",
        "gap": "2rem",
        "marginBottom": "2rem",
        "flexWrap": "wrap",  # Allows wrapping on smaller screens
        "alignItems": "stretch"  # Makes both containers same height
    }),
    # Row 2: Top Performing Sports by Medal Count (left), Age Distribution of Medalists (right)
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=tactical_figures['top_sports'],
                config={"displayModeBar": False},
                style={
                    "height": "440px",
                    "minHeight": "340px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], width={"size": 12, "sm": 12, "md": 6, "lg": 6}, style={"minWidth": 0, "flexGrow": 1}),
        dbc.Col([
            dcc.Graph(
                figure=tactical_figures['medalist_age'],
                config={"displayModeBar": False},
                style={
                    "height": "440px",
                    "minHeight": "340px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], width={"size": 12, "sm": 12, "md": 6, "lg": 6}, style={"minWidth": 0, "flexGrow": 1})
    ], style={"gap": "2rem", "display": "flex", "flexWrap": "wrap", "alignItems": "stretch"}, className="mb-4"),
    # Next rows (if any)
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=tactical_figures['top_athletes'],
                style={
                    "height": "440px",
                    "minHeight": "340px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], width={"size": 12, "sm": 12, "md": 12, "lg": 12}, style={"minWidth": 0})
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=tactical_figures['age_vs_medal_type'],
                style={
                    "height": "440px",
                    "minHeight": "340px",
                    "background": "#fff",
                    "borderRadius": "14px",
                    "padding": "1rem",
                    "boxShadow": "0 2px 12px rgba(0,0,0,0.10)"
                }
            )
        ], width={"size": 12, "sm": 12, "md": 12, "lg": 12}, style={"minWidth": 0})
    ], className="mb-4"),
    # Deep dive table at the bottom
    deep_dive_table
], style={
    "maxWidth": "1800px",  # Maximum width for very large screens
    "margin": "0 auto",    # Center the content
    "padding": "0 1rem"    # Add some padding on the sides
})

# Layout of the main content area
content = html.Div(id="page-content", 
                  style={'marginLeft': '13rem', 'padding': '2rem 1.2rem 2rem 1.2rem', 
                        'backgroundColor': '#e9ecef', 'minHeight': '100vh',
                        'color': '#000000', 'fontFamily': 'Montserrat, Roboto, sans-serif'})

# Overall App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
], style={'backgroundColor': '#e9ecef'})

# Callback to update page content based on URL (sidebar navigation)
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/analytical":
        return analyical_content_layout
    elif pathname == "/tactical":
        return tactical_content_layout
    else:
        # Default to analytical dashboard
        return analyical_content_layout

# Callback to handle sidebar collapse
@app.callback(
    [Output("sidebar-collapse", "is_open"), Output("page-content", "style")],
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar-collapse", "is_open"), State("page-content", "style")],
)
def toggle_sidebar_collapse(n_clicks, is_open, content_style):
    if n_clicks:
        if is_open:
            # Close sidebar and adjust content margin
            return False, {'marginLeft': '2rem', 'padding': '2rem 1rem'}
        else:
            # Open sidebar and adjust content margin
            return True, {'marginLeft': '13rem', 'padding': '2rem 1.2rem'}
    return is_open, content_style


if __name__ == '__main__':
    app.run(debug=True) 