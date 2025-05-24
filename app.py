import dash
from dash import html, dcc
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

# Create tabs
tabs = dbc.Tabs([
    dbc.Tab(label="Analytical Dashboard", children=[
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=analytical_figures['gender_dist']),
                dcc.Graph(figure=analytical_figures['participation_trend'])
            ], width=6),
            dbc.Col([
                dcc.Graph(figure=analytical_figures['top_events']),
                dcc.Graph(figure=analytical_figures['sport_dist'])
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=analytical_figures['country_map'])
            ], width=12)
        ]),
        # Deep Dive Chart: Gender Participation Evolution Over Time
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=analytical_figures['gender_participation_trend'])
            ], width=12)
        ])
    ]),
    dbc.Tab(label="Tactical Dashboard", children=[
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=tactical_figures['medal_by_country_gender']),
                dcc.Graph(figure=tactical_figures['medalist_age'])
            ], width=6),
            dbc.Col([
                dcc.Graph(figure=tactical_figures['top_sports']),
                dcc.Graph(figure=tactical_figures['gold_medal_teams'])
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=tactical_figures['top_athletes'])
            ], width=12)
        ]),
        # Deep Dive Chart: Medal Type Distribution
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=tactical_figures['age_vs_medal_type'])
            ], width=12)
        ])
    ])
])

# App layout
app.layout = dbc.Container([
    html.H1("Olympic Games Analytics Dashboard", className="text-center my-4"),
    tabs
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True) 