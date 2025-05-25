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
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Print the result (for now, as requested)
# print("Distinct Canadian Athlete Count:", canada_athlete_count_result)

# Get dashboard figures
analytical_figures = get_analytical_dashboard()
tactical_figures = get_tactical_dashboard()

# Define the sidebar layout
sidebar = html.Div(
    [
        html.H2("Olympic Dashboard", className="display-4 text-center"),
        html.Hr(),
        # Dashboard navigation links
        dbc.Nav(
            [
                dbc.NavLink("Analytical Dashboard", href="/analytical", active="exact", id="nav-analytical"),
                dbc.NavLink("Tactical Dashboard", href="/tactical", active="exact", id="nav-tactical"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
        html.P(
            "Filters", className="lead"
        ),
        # Filter components
        dbc.Nav(
            [
                # Place your filter components here
                html.Div("Year", className="lead"),
                dcc.Dropdown(id='year-filter', options=[{'label': str(i), 'value': i} for i in range(1896, 2021, 2)] + [{'label': 'All', 'value': 'All'}], value='All', clearable=False),
                # Add other filters here (Season, Gender, Sport, Country)
            ],
            vertical=True,
            pills=True,
        ),
    ],
    # Style the sidebar
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "background-color": "#003366", # Olympic Blue
        "color": "white",
        "zIndex": 1 # Ensure sidebar is above content
    },
)

# Define the analytical dashboard content layout
analyical_content_layout = html.Div([
    # Analytical Summary Cards Row
    dbc.Row([
        dbc.Col(dcc.Graph(figure=analytical_figures['summary_cards'][0], config={'displayModeBar': False}), width=3),
        dbc.Col(dcc.Graph(figure=analytical_figures['summary_cards'][1], config={'displayModeBar': False}), width=3),
        dbc.Col(dcc.Graph(figure=analytical_figures['summary_cards'][2], config={'displayModeBar': False}), width=3),
        dbc.Col(dcc.Graph(figure=analytical_figures['summary_cards'][3], config={'displayModeBar': False}), width=3),
    ], className="mb-4"), # Add bottom margin to this row
    
    # New Top Row: Map and Top Countries by Medals
    dbc.Row([
        # Map (left)
        dbc.Col([
            dcc.Graph(figure=analytical_figures['country_map'])
        ], width=7), # Adjusted width for the map
        # Top Countries by Medals (right)
        dbc.Col([
            html.H4("Top 3 Countries by Medals", className="mb-2"), # Add bottom margin to title
            html.Div([
                dcc.Graph(figure=analytical_figures['top_countries_by_medals'][0], config={'displayModeBar': False}, className="mb-2"), # Add bottom margin
                dcc.Graph(figure=analytical_figures['top_countries_by_medals'][1], config={'displayModeBar': False}, className="mb-2"), # Add bottom margin
                dcc.Graph(figure=analytical_figures['top_countries_by_medals'][2], config={'displayModeBar': False}), # No bottom margin for the last card
            ])
        ], width=5) # Remaining width for the top countries card
    ], className="mb-4", align="center"), # Add bottom margin and vertical alignment
    
    # Row 1: Total Athletes by Gender and Gender Participation Evolution Over Time
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=analytical_figures['gender_distribution']),
        ], width=6), # Half width
        dbc.Col([
            dcc.Graph(figure=analytical_figures['gender_participation_trend'])
        ], width=6) # Half width
    ], className="mb-4"), # Add bottom margin
    
    # Row 2: Events per Sport and Top 5 Events
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=analytical_figures['sport_distribution']),
        ], width=6), # Half width
        dbc.Col([
            dcc.Graph(figure=analytical_figures['top_events']),
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
content = html.Div(id="page-content", style={'marginLeft': '16rem', 'padding': '2rem 1rem'})

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

if __name__ == '__main__':
    app.run(debug=True) 