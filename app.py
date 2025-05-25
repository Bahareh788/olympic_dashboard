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
        "background": "#F8F9FA",
        "color": "#00274D",
        "zIndex": 1,
        "fontFamily": 'Montserrat, sans-serif'
    },
)

# Define the analytical dashboard content layout
analyical_content_layout = html.Div([
    # analyical_summary_cards_row,  # Removed summary cards from the top
    # Map and Continent Metric Cards Row
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=analyical_figures['country_map'])
        ], width=8),
        dbc.Col([
            html.Div(continent_metrics_cards)
        ], width=4)
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

def extract_title_text(fig, prefix):
    title = getattr(getattr(fig.layout, 'title', None), 'text', None)
    if title and '<br>' in title:
        return f"{prefix}: {title.split('<br>')[1]}"
    return prefix

# Tactical summary cards
summary_card_data_tactical = [
    {"icon": "fas fa-medal", "color": "#00BCD4", "bgcolor": "#FFFFFF", "title": "Total Medals", "value": tactical_figures['summary_cards'][0].data[0]['value']},
    {"icon": "fas fa-trophy", "color": "#F44336", "bgcolor": "#FFFFFF", "title": "Gold Medals", "value": tactical_figures['summary_cards'][1].data[0]['value']},
    {"icon": "fas fa-flag", "color": "#4CAF50", "bgcolor": "#FFFFFF", "title": extract_title_text(tactical_figures['summary_cards'][2], "Top Country"), "value": tactical_figures['summary_cards'][2].data[0]['value']},
    {"icon": "fas fa-user", "color": "#FFC107", "bgcolor": "#FFFFFF", "title": extract_title_text(tactical_figures['summary_cards'][3], "Top Athlete"), "value": tactical_figures['summary_cards'][3].data[0]['value']},
]

tactical_summary_card_styles = [
    {"icon": "fas fa-medal", "color": "#00BCD4", "bgcolor": "#00BCD4", "title": "Total Medals"},
    {"icon": "fas fa-trophy", "color": "#F44336", "bgcolor": "#F44336", "title": "Gold Medals"},
    {"icon": "fas fa-flag", "color": "#4CAF50", "bgcolor": "#4CAF50", "title": "Top Country"},
    {"icon": "fas fa-user", "color": "#FFC107", "bgcolor": "#FFC107", "title": "Top Athlete"},
]

def make_tactical_summary_card(icon, color, title, value, bgcolor):
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
            html.Div(title, style={"fontWeight": "bold", "fontSize": "1.1rem", "color": "#fff", "marginBottom": "0.2rem"}),
            html.Div(f"{value}", style={"fontWeight": "bold", "fontSize": "1.3rem", "color": "#fff"}),
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
        card["value"],
        tactical_summary_card_styles[i]["bgcolor"]
    )
    for i, card in enumerate(summary_card_data_tactical)
], style={"display": "flex", "gap": "1.5rem", "marginBottom": "2rem"})

# Define the tactical dashboard content layout
tactical_content_layout = html.Div([
    tactical_summary_cards_row,
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
                        'backgroundColor': '#e9ecef', 'minHeight': '100vh',
                        'color': '#000000'})

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
            return True, {'marginLeft': '15rem', 'padding': '2rem 1rem'}
    return is_open, content_style


if __name__ == '__main__':
    app.run(debug=True) 