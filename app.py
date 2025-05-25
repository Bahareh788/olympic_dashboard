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
# For a truly modern font like Roboto or Montserrat, you would typically link a font file in your index.html or a CSS file.
# Example in index.html head:
# <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
# For FontAwesome icons, you need to include the library. Example in index.html head:
# <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
# For hover effects on sidebar links, you would typically use CSS classes.
# Example in a CSS file:
# .sidebar-link:hover { background-color: #e9ecef !important; color: #003366 !important; }
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Print the result (for now, as requested)
# print("Distinct Canadian Athlete Count:", canada_athlete_count_result)

# Get dashboard figures
analyical_figures = get_analytical_dashboard()
tactical_figures = get_tactical_dashboard()

# Define the sidebar layout
sidebar = html.Div(
    [
        # Toggle button for sidebar collapse
        html.Button(
            # Use a custom icon or text for the toggle
            html.Span(className="navbar-toggler-icon"),
            className="navbar-toggler",
            id="sidebar-toggle",
            style={'color': 'white', 'borderColor': 'rgba(255,255,255,.1)'}
        ),
        dbc.Collapse(
            [
                
                html.Div(
                    html.Img(
                        src='/assets/Untitled design.png', # Path to your image in the assets folder
                        style={'width': '80%', 'margin': 'auto', 'display': 'block'} # Adjust size and center
                    ),
                    className="text-center my-3" # Add some margin
                ),

                html.H2("Olympic Dashboard", className="display-6 text-center my-2", style={'color': 'white', 'fontFamily': 'Segoe UI, Arial, sans-serif'}),
                html.Hr(className="my-2"),
                # Dashboard navigation links
                dbc.Nav(
                    [
                        # Analytical Dashboard Link with Icon and Styling
                        dbc.NavLink(
                            [
                                html.I(className="fas fa-chart-bar me-2"), # Example icon (requires FontAwesome)
                                "Analytical Dashboard"
                            ],
                            href="/analytical",
                            active="exact",
                            id="nav-analytical",
                            className="sidebar-link", # Custom class for potential CSS styling
                            style={'backgroundColor': 'white', 'color': '#003366', 'borderRadius': '20px', 'margin': '5px 0', 'padding': '10px 15px'}
                        ),
                        # Tactical Dashboard Link with Icon and Styling
                        dbc.NavLink(
                            [
                                html.I(className="fas fa-medal me-2"), # Example icon (requires FontAwesome)
                                "Tactical Dashboard"
                            ],
                            href="/tactical",
                            active="exact",
                            id="nav-tactical",
                             className="sidebar-link", # Custom class for potential CSS styling
                            style={'backgroundColor': 'white', 'color': '#003366', 'borderRadius': '20px', 'margin': '5px 0', 'padding': '10px 15px'}
                        ),
                    ],
                    vertical=True,
                    pills=True,
                    className="mb-4", # Add margin below nav links
                ),
                html.Hr(className="my-2"),
                html.P(
                    "Filters", className="lead" , style={'color': 'white', 'fontSize': '1.2rem', 'marginTop': '15px'}
                ),
                # Filter components with improved styling
                dbc.Nav(
                    [
                        # Year Filter with larger label and padding
                        html.Div("Year", className="lead", style={'color': 'white', 'fontSize': '1rem', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id='year-filter',
                            options=[{'label': str(i), 'value': i} for i in range(1896, 2021, 2)] + [{'label': 'All', 'value': 'All'}],
                            value='All',
                            clearable=False,
                            style={'marginBottom': '15px', 'borderRadius': '5px'} # Add margin bottom and slight rounding
                            # For more significant rounded corners, custom CSS would be needed
                        ),
                        # Add other filters here with similar styling (Season, Gender, Sport, Country)
                        # html.Div("Season", className="lead", style={'color': 'white', 'fontSize': '1rem', 'marginBottom': '5px'}),
                        # dcc.Dropdown(id='season-filter', options=['Summer', 'Winter'], value='Summer', clearable=False, style={'marginBottom': '15px', 'borderRadius': '5px'}),
                         # html.Div("Gender", className="lead", style={'color': 'white', 'fontSize': '1rem', 'marginBottom': '5px'}),
                        # dcc.Dropdown(id='gender-filter', options=['M', 'F', 'All'], value='All', clearable=False, style={'marginBottom': '15px', 'borderRadius': '5px'}),

                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
            id="sidebar-collapse", # Add ID for collapse component
            is_open=True, # Sidebar is open by default
        ),
    ],
    # Style the sidebar with a gradient background and adjusted padding
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "14rem", # Reduced sidebar width
        "padding": "1.5rem 1rem", # Adjusted padding
        "background": "linear-gradient(to bottom, #003366, #001f3f)", # Darker blue gradient
        "color": "white",
        "zIndex": 1, # Ensure sidebar is above content
        "fontFamily": 'Segoe UI, Arial, sans-serif' # Apply a modern web-safe font
    },
)

# Define the analytical dashboard content layout
analyical_content_layout = html.Div([
    # Analytical Summary Cards Row
    dbc.Row([
        dbc.Col(dcc.Graph(figure=analyical_figures['summary_cards'][0], config={'displayModeBar': False}), width=3),
        dbc.Col(dcc.Graph(figure=analyical_figures['summary_cards'][1], config={'displayModeBar': False}), width=3),
        dbc.Col(dcc.Graph(figure=analyical_figures['summary_cards'][2], config={'displayModeBar': False}), width=3),
        dbc.Col(dcc.Graph(figure=analyical_figures['summary_cards'][3], config={'displayModeBar': False}), width=3),
    ], className="mb-4"), # Add bottom margin to this row
    
    # New Top Row: Map and Top Countries by Medals
    dbc.Row([
        # Map (left)
        dbc.Col([
            dcc.Graph(figure=analyical_figures['country_map'])
        ], width=7), # Adjusted width for the map
        # Top Countries by Medals (right)
        dbc.Col([
            html.H4("Top 3 Countries by Medals", className="mb-2"), # Add bottom margin to title
            html.Div([
                dcc.Graph(figure=analyical_figures['top_countries_by_medals'][0], config={'displayModeBar': False}, className="mb-2"), # Add bottom margin
                dcc.Graph(figure=analyical_figures['top_countries_by_medals'][1], config={'displayModeBar': False}, className="mb-2"), # Add bottom margin
                dcc.Graph(figure=analyical_figures['top_countries_by_medals'][2], config={'displayModeBar': False}), # No bottom margin for the last card
            ])
        ], width=5) # Remaining width for the top countries card
    ], className="mb-4", align="center"), # Add bottom margin and vertical alignment
    
    # Row 1: Total Athletes by Gender and Gender Participation Evolution Over Time
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=analyical_figures['gender_distribution']),
        ], width=6), # Half width
        dbc.Col([
            dcc.Graph(figure=analyical_figures['gender_participation_trend'])
        ], width=6) # Half width
    ], className="mb-4"), # Add bottom margin
    
    # Row 2: Events per Sport and Top 5 Events
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=analyical_figures['sport_distribution']),
        ], width=6), # Half width
        dbc.Col([
            dcc.Graph(figure=analyical_figures['top_events']),
        ], width=6) # Half width
    ])
])

# Define the tactical dashboard content layout
tactical_content_layout = html.Div([
    # Tactical Summary Cards
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=tactical_figures['summary_cards'][0], config={'displayModeBar': False}),
        ], width=3),
        dbc.Col([
            dcc.Graph(figure=tactical_figures['summary_cards'][1], config={'displayModeBar': False}),
        ], width=3),
        dbc.Col([
            dcc.Graph(figure=tactical_figures['summary_cards'][2], config={'displayModeBar': False}),
        ], width=3),
        dbc.Col([
            dcc.Graph(figure=tactical_figures['summary_cards'][3], config={'displayModeBar': False}),
        ], width=3)
    ], className="mb-4"), # Add bottom margin to this row
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
    ], className="mb-4"), # Add bottom margin to this row
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=tactical_figures['top_athletes'])
        ], width=12)
    ], className="mb-4"), # Add bottom margin to this row
    # Deep Dive Chart: Medal Type Distribution
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=tactical_figures['age_vs_medal_type'])
        ], width=12)
    ])
])

# Layout of the main content area (to be updated by callback)
# Use a default margin-left that can be adjusted by a callback when the sidebar collapses
content = html.Div(id="page-content", style={'marginLeft': '17rem', 'padding': '2rem 1rem'})

# Overall App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])

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
            return True, {'marginLeft': '17rem', 'padding': '2rem 1rem'}
    return is_open, content_style


if __name__ == '__main__':
    app.run(debug=True) 