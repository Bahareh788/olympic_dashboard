import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from analytical_dashboard import get_analytical_dashboard
from tactical_dashboard import get_tactical_dashboard
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from db_utils import execute_query

# Initialize Flask app
server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Bahardb1234@localhost:5432/Olympicdb'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)

# Initialize Dash app
app = dash.Dash(__name__, server=server, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap'
])

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
                background-color: #FFFFFF;
                color: #000000;
            }
            .card {
                background-color: #FFFFFF !important;
                border: 1px solid #E0E0E0 !important;
                border-radius: 10px !important;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important;
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
                background-color: #F0F0F0 !important;
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
                html.Hr(className="my-2", style={'borderColor': 'rgba(0,0,0,.1)'}),
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
                dbc.Nav(
                    [
                        html.Div("Year", className="lead", 
                                style={'color': '#00274D', 'fontSize': '1rem', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id='year-filter',
                            options=[{'label': str(i), 'value': i} for i in range(1896, 2021, 2)] + 
                                   [{'label': 'All', 'value': 'All'}],
                            value='All',
                            clearable=False,
                            style={'marginBottom': '15px', 'borderRadius': '10px'}
                        ),
                    ],
                    vertical=True,
                    pills=True,
                ),
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
        "background": "#FFFFFF",
        "color": "#00274D",
        "zIndex": 1,
        "fontFamily": 'Montserrat, sans-serif'
    },
)

# Define the analytical dashboard content layout
analyical_content_layout = html.Div([
    # Analytical Summary Cards Row
    dbc.Row([
        dbc.Col(dcc.Graph(figure=analyical_figures['summary_cards'][0], 
                         config={'displayModeBar': False}), width=3),
        dbc.Col(dcc.Graph(figure=analyical_figures['summary_cards'][1], 
                         config={'displayModeBar': False}), width=3),
        dbc.Col(dcc.Graph(figure=analyical_figures['summary_cards'][2], 
                         config={'displayModeBar': False}), width=3),
        dbc.Col(dcc.Graph(figure=analyical_figures['summary_cards'][3], 
                         config={'displayModeBar': False}), width=3),
    ], className="mb-4"),
    
    # New Top Row: Map and Top Countries by Medals
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=analyical_figures['country_map'])
        ], width=7),
        dbc.Col([
            html.H4("Top 3 Countries by Medals", 
                   className="mb-2",
                   style={'color': '#00274D'}),
            html.Div([
                dcc.Graph(figure=analyical_figures['top_countries_by_medals'][0], 
                         config={'displayModeBar': False}, 
                         className="mb-2"),
                dcc.Graph(figure=analyical_figures['top_countries_by_medals'][1], 
                         config={'displayModeBar': False}, 
                         className="mb-2"),
                dcc.Graph(figure=analyical_figures['top_countries_by_medals'][2], 
                         config={'displayModeBar': False}),
            ])
        ], width=5)
    ], className="mb-4", align="center"),
    
    # Row 1: Total Athletes by Gender and Gender Participation Evolution Over Time
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=analyical_figures['gender_distribution']),
        ], width=6),
        dbc.Col([
            dcc.Graph(figure=analyical_figures['gender_participation_trend'])
        ], width=6)
    ], className="mb-4"),
    
    # Row 2: Events per Sport and Top 5 Events
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=analyical_figures['sport_distribution']),
        ], width=6),
        dbc.Col([
            dcc.Graph(figure=analyical_figures['top_events']),
        ], width=6)
    ])
])

# Define the tactical dashboard content layout
tactical_content_layout = html.Div([
    # Tactical Summary Cards
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=tactical_figures['summary_cards'][0], 
                     config={'displayModeBar': False}),
        ], width=3),
        dbc.Col([
            dcc.Graph(figure=tactical_figures['summary_cards'][1], 
                     config={'displayModeBar': False}),
        ], width=3),
        dbc.Col([
            dcc.Graph(figure=tactical_figures['summary_cards'][2], 
                     config={'displayModeBar': False}),
        ], width=3),
        dbc.Col([
            dcc.Graph(figure=tactical_figures['summary_cards'][3], 
                     config={'displayModeBar': False}),
        ], width=3)
    ], className="mb-4"),
    
    # Chart Rows
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=tactical_figures['medal_by_country_gender']),
            dcc.Graph(figure=tactical_figures['medalist_age'])
        ], width=6),
        dbc.Col([
            dcc.Graph(figure=tactical_figures['top_sports']),
            dcc.Graph(figure=tactical_figures['gold_medal_teams'])
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=tactical_figures['top_athletes'])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=tactical_figures['age_vs_medal_type'])
        ], width=12)
    ])
])

# Layout of the main content area
content = html.Div(id="page-content", 
                  style={'marginLeft': '15rem', 'padding': '2rem 1rem', 
                        'backgroundColor': '#FFFFFF', 'minHeight': '100vh',
                        'color': '#000000'})

# Overall App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
], style={'backgroundColor': '#FFFFFF'})

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
            return True, {'marginLeft': '15rem', 'padding': '2rem 1rem'}
    return is_open, content_style


if __name__ == '__main__':
    app.run(debug=True) 