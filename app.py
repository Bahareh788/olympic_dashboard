import dash
from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from analytical_dashboard import get_analytical_dashboard, create_filtered_gender_distribution, create_filtered_participation_trend, create_filtered_top_events, create_filtered_gender_participation_trend
from tactical_dashboard import get_tactical_dashboard, get_filtered_noc_medal_table, create_filtered_medal_by_country_gender, create_filtered_top_sports
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
        'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
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
                color: #1F2937;  /* Improved contrast */
                font-size: 1.1rem;
            }
            .card {
                background-color: #FFFFFF !important;
                border: 1px solid #D1D5DB !important;  /* Better contrast border */
                border-radius: 10px !important;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08) !important;  /* Slightly stronger shadow */
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important;
                margin-bottom: 1.5rem !important;
                padding: 1rem !important;
            }
            .card:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;  /* Enhanced hover shadow */
            }
            .sidebar-link {
                transition: all 0.3s ease !important;
                color: #00274D !important;
                outline: none !important;
            }
            .sidebar-link:hover, .sidebar-link:focus {
                background-color: #E5E7EB !important;  /* Better contrast hover */
                transform: translateX(5px) !important;
                outline: 2px solid #2563EB !important;  /* Focus indicator */
                outline-offset: 2px !important;
            }
            .dropdown-menu {
                background-color: #FFFFFF !important;
                border: 1px solid #D1D5DB !important;  /* Better contrast border */
            }
            .dropdown-item {
                color: #1F2937 !important;  /* Better contrast text */
            }
            .dropdown-item:hover, .dropdown-item:focus {
                background-color: #F3F4F6 !important;  /* Better contrast hover */
                outline: 2px solid #2563EB !important;  /* Focus indicator */
            }
             .Select-control {
                background-color: #FFFFFF !important;
                border: 1px solid #D1D5DB !important;  /* Better contrast border */
                color: #1F2937 !important;  /* Better contrast text */
            }
            .Select-control:hover, .Select-control:focus {
                border-color: #2563EB !important;  /* Focus indicator */
                outline: 2px solid #2563EB !important;
                outline-offset: 2px !important;
            }
            .Select-value-label {
                color: #1F2937 !important;  /* Better contrast */
            }
            .Select-arrow {
                 color: #1F2937 !important;  /* Better contrast */
            }
            .Select-menu-outer {
                background-color: #FFFFFF !important;
                border: 1px solid #D1D5DB !important;  /* Better contrast border */
            }
            .Select-option {
                background-color: #FFFFFF !important;
                color: #1F2937 !important;  /* Better contrast */
            }
            .Select-option:hover, .Select-option:focus {
                background-color: #F3F4F6 !important;  /* Better contrast hover */
            }
            /* High contrast mode support */
            @media (prefers-contrast: high) {
                .card {
                    border: 2px solid #000000 !important;
                }
                .sidebar-link:focus {
                    outline: 3px solid #000000 !important;
                }
            }
            /* Reduced motion support */
            @media (prefers-reduced-motion: reduce) {
                .card, .sidebar-link {
                    transition: none !important;
                }
                .card:hover {
                    transform: none !important;
                }
                .sidebar-link:hover {
                    transform: none !important;
                }
            }
            /* Modern continent cards hover effects */
            .modern-continent-card {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            .modern-continent-card:hover {
                transform: translateY(-8px) scale(1.02) !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2), 0 8px 20px rgba(0, 0, 0, 0.15) !important;
            }
            .modern-continent-card:active {
                transform: translateY(-4px) scale(1.01) !important;
            }
            /* Glassmorphism effects */
            .glass-icon {
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
            }
            /* Card content animations */
            .modern-continent-card:hover .glass-icon {
                transform: scale(1.1) rotate(5deg) !important;
                transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
            }
            .modern-continent-card .continent-title {
                transition: all 0.3s ease !important;
            }
            .modern-continent-card:hover .continent-title {
                letter-spacing: 1px !important;
            }
            .modern-continent-card .athlete-count {
                transition: all 0.3s ease !important;
            }
            .modern-continent-card:hover .athlete-count {
                transform: scale(1.05) !important;
            }
            /* Glow effect for cards */
            .modern-continent-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: inherit;
                border-radius: inherit;
                filter: blur(20px);
                opacity: 0;
                transition: opacity 0.3s ease;
                z-index: -1;
            }
            .modern-continent-card:hover::before {
                opacity: 0.3;
            }
            /* Font Awesome icon styling for continent cards */
            .glass-icon i {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-style: normal !important;
                font-variant: normal !important;
                text-rendering: auto !important;
                -webkit-font-smoothing: antialiased !important;
            }
            /* KPI Cards styling */
            .kpi-card-container {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            .kpi-card-container:hover {
                transform: translateY(-5px) !important;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.18) !important;
            }
            /* Force visibility of KPI card text */
            .kpi-card-container .js-plotly-plot .plotly .svg-container svg text {
                fill: currentColor !important;
                opacity: 1 !important;
                visibility: visible !important;
            }
            .kpi-card-container .js-plotly-plot .plotly .svg-container svg .number {
                fill: currentColor !important;
                opacity: 1 !important;
                font-weight: bold !important;
            }
            .kpi-card-container .js-plotly-plot .plotly .svg-container svg .title {
                fill: currentColor !important;
                opacity: 1 !important;
                font-weight: 600 !important;
            }
            /* Ensure plotly indicator text is visible */
            .js-plotly-plot .plotly .svg-container svg g.indicatorlayer text {
                opacity: 1 !important;
                visibility: visible !important;
            }
            .js-plotly-plot .plotly .svg-container svg g.indicatorlayer .number {
                opacity: 1 !important;
                visibility: visible !important;
                font-weight: bold !important;
            }
            /* Reduced motion support for KPI cards */
            @media (prefers-reduced-motion: reduce) {
                .kpi-card-container {
                    transition: none !important;
                }
                .kpi-card-container:hover {
                    transform: none !important;
                }
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

# Olympic colors with accessibility improvements - colorblind-friendly palette
olympic_palette_accessible = [
    '#2563EB',  # Blue (high contrast, colorblind safe)
    '#F59E0B',  # Amber/Orange (replaces yellow, better contrast)
    '#1F2937',  # Dark gray (replaces pure black, better readability)
    '#059669',  # Emerald green (colorblind safe)
    '#DC2626'   # Red (high contrast, colorblind safe)
]

# Keep original palette for backward compatibility but use accessible one for new implementations
olympic_palette = olympic_palette_accessible

# Helper for summary card layout with improved accessibility
summary_card_data_analytical = [
    {"icon": "fas fa-globe-americas", "color": "#DC2626", "bgcolor": "#FEF2F2", "title": "AMERICAS", "value": analyical_figures['summary_cards'][0].data[0]['value']},
    {"icon": "fas fa-globe-europe", "color": "#059669", "bgcolor": "#F0FDF4", "title": "EUROPE", "value": analyical_figures['summary_cards'][1].data[0]['value']},
    {"icon": "fas fa-globe-africa", "color": "#1F2937", "bgcolor": "#F9FAFB", "title": "AFRICA", "value": analyical_figures['summary_cards'][2].data[0]['value']},
    {"icon": "fas fa-globe-asia", "color": "#F59E0B", "bgcolor": "#FFFBEB", "title": "ASIA", "value": analyical_figures['summary_cards'][3].data[0]['value']},
    {"icon": "fas fa-water", "color": "#2563EB", "bgcolor": "#EFF6FF", "title": "OCEANIA", "value": analyical_figures['summary_cards'][4].data[0]['value'] if len(analyical_figures['summary_cards']) > 4 else 0},
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
    'Oceania': 'fas fa-water',  # Using water icon as island-tropical might not exist
}

def make_continent_metric_card(continent, athletes, medals, color, text_color):
    # Modern Font Awesome icons for each continent
    icon_classes = {
        'Africa': 'fas fa-map-marker-alt',      # Location marker for Africa
        'Americas': 'fas fa-chart-bar',         # Chart for Americas (data-focused)
        'Asia': 'fas fa-star',                  # Star for Asia (excellence)
        'Europe': 'fas fa-chart-pie',           # Pie chart for Europe (analytics)
        'Oceania': 'fas fa-water',              # Water for Oceania (islands)
    }
    
    icon_class = icon_classes.get(continent, 'fas fa-globe')
    
    # Create gradient background based on the primary color
    gradient_colors = {
        '#059669': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',  # Green gradient
        '#DC2626': 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',  # Red gradient  
        '#F59E0B': 'linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%)',  # Orange gradient
        '#1F2937': 'linear-gradient(135deg, #374151 0%, #1F2937 100%)',  # Gray gradient
        '#2563EB': 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',  # Blue gradient
    }
    
    background_gradient = gradient_colors.get(color, f'linear-gradient(135deg, {color} 0%, {color} 100%)')
    
    return html.Div([
        # Icon section with modern styling
        html.Div([
            html.Div([
                html.I(className=icon_class, style={
                    "fontSize": "1.6rem", 
                    "color": "#FFFFFF",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "width": "100%",
                    "height": "100%"
                })
            ], style={
                "display": "flex",
                "alignItems": "center", 
                "justifyContent": "center",
                "width": "48px",
                "height": "48px",
                "background": "rgba(255, 255, 255, 0.2)",
                "borderRadius": "12px",
                "backdropFilter": "blur(10px)",
                "border": "1px solid rgba(255, 255, 255, 0.3)"
            }, className="glass-icon")
        ], style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "padding": "1rem 0.75rem"
        }),
        
        # Content section
        html.Div([
            # Continent title
            html.Div(continent, style={
                "fontSize": "0.95rem",
                "fontWeight": "600",
                "color": "#FFFFFF",
                "marginBottom": "0.3rem",
                "letterSpacing": "0.3px",
                "textTransform": "uppercase",
                "fontFamily": "Montserrat, sans-serif"
            }, className="continent-title"),
            
            # Athletes count with better typography
            html.Div([
                html.Span(f"{athletes:,}", style={
                    "fontSize": "1.5rem",
                    "fontWeight": "700",
                    "color": "#FFFFFF",
                    "lineHeight": "1.2",
                    "fontFamily": "Montserrat, sans-serif"
                }),
                html.Span(" Athletes", style={
                    "fontSize": "0.75rem",
                    "color": "rgba(255, 255, 255, 0.8)",
                    "marginLeft": "0.4rem",
                    "fontWeight": "500"
                })
            ], style={"marginBottom": "0.2rem"}, className="athlete-count"),
            
            # Medals with enhanced styling
            html.Div([
                html.I(className="fas fa-medal", style={
                    "color": "rgba(255, 255, 255, 0.9)",
                    "marginRight": "0.4rem",
                    "fontSize": "0.75rem"
                }),
                html.Span(f"{medals:,} Medals", style={
                    "fontSize": "0.85rem",
                    "color": "rgba(255, 255, 255, 0.9)",
                    "fontWeight": "500"
                })
            ])
        ], style={
            "flex": "1",
            "padding": "1rem 1rem 1rem 0",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center"
        }),
        
        # Decorative accent element
        html.Div(style={
            "position": "absolute",
            "top": "0",
            "right": "0",
            "width": "60px",
            "height": "60px",
            "background": "rgba(255, 255, 255, 0.1)",
            "borderRadius": "0 12px 0 100%",
            "pointerEvents": "none"
        }),
        
        # Subtle bottom accent line
        html.Div(style={
            "position": "absolute",
            "bottom": "0",
            "left": "0",
            "right": "0",
            "height": "2px",
            "background": "rgba(255, 255, 255, 0.3)"
        })
        
    ], style={
        "position": "relative",
        "display": "flex",
        "alignItems": "center",
        "width": "100%",
        "minWidth": "280px",
        "maxWidth": "350px",
        "height": "85px",
        "background": background_gradient,
        "borderRadius": "12px",
        "boxShadow": "0 6px 20px rgba(0, 0, 0, 0.12), 0 3px 8px rgba(0, 0, 0, 0.08)",
        "marginBottom": "0.8rem",
        "overflow": "hidden",
        "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        "cursor": "pointer",
        "border": "1px solid rgba(255, 255, 255, 0.2)"
    }, className="modern-continent-card")

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
                        options=[{'label': 'All', 'value': 'All'}] + [{'label': str(year), 'value': year} for year in unique_years],
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

# Extract unique filter values with error handling
try:
    unique_years = sorted(list({row['year'] for row in athlete_participation_data if row.get('year')}))
    unique_genders = sorted(list({row['gender'] for row in athlete_participation_data if row.get('gender')}))
    unique_sports = sorted(list({row['sport'] for row in athlete_participation_data if row.get('sport')}))
    unique_countries = sorted(list({row['country'] for row in athlete_participation_data if row.get('country')}))
    
    print(f"Filter options loaded:")
    print(f"Years: {len(unique_years)} options")
    print(f"Genders: {unique_genders}")
    print(f"Sports: {len(unique_sports)} options") 
    print(f"Countries: {len(unique_countries)} options")
    
except Exception as e:
    print(f"Error extracting filter values: {e}")
    # Fallback values
    unique_years = list(range(1896, 2021, 4))
    unique_genders = ['M', 'F']
    unique_sports = ['Athletics', 'Swimming', 'Gymnastics']
    unique_countries = ['USA', 'GER', 'FRA']

olympic_palette = ['#0085C3', '#F4C300', '#000000', '#009F3D', '#DF0024']

analyical_athlete_table_layout = html.Div([
    # Modern section header with Olympic styling
    html.Div([
        html.Div([
            html.H3("Athlete Participation Deep Dive", style={
                "fontSize": "1.5rem",
                "fontWeight": "700",
                "color": "#1F2937",
                "marginBottom": "0.3rem",
                "fontFamily": "Inter, Montserrat, sans-serif",
                "display": "inline-block"
            })
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "0.5rem"})
    ], style={
        "marginBottom": "1.5rem",
        "paddingBottom": "1rem",
        "borderBottom": "2px solid #E5E7EB"
    }),
    
    # Enhanced DataTable with modern styling
    dash_table.DataTable(
        id='athlete-participation-table',
        columns=[
            {
                "name": "Athlete Name", 
                "id": "athlete_name",
                "type": "text",
                "presentation": "markdown"
            },
            {
                "name": "Country", 
                "id": "country",
                "type": "text"
            },
            {
                "name": "Year", 
                "id": "year", 
                "type": "numeric",
                "format": {"specifier": "d"}
            },
            {
                "name": "Sport", 
                "id": "sport",
                "type": "text"
            },
            {
                "name": "Gender", 
                "id": "gender",
                "type": "text"
            }
        ],
        data=athlete_participation_data,
        
        # Enhanced functionality
        page_size=20,
        page_action="native",
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        selected_rows=[],
        
        # Fixed rows for better UX
        fixed_rows={"headers": True, "data": 0},
        
        # Modern styling for the table container
        style_table={
            "height": "350px",
            "overflowY": "auto",
            "overflowX": "auto",
            "minWidth": "100%",
            "background": "#FFFFFF",
            "borderRadius": "4px",  # Sharp corners matching dashboard
            "border": "1px solid #D1D5DB",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.15)"
        },
        
        # Enhanced cell styling
        style_cell={
            "padding": "1rem 0.75rem",
            "fontSize": "0.9rem",
            "textAlign": "left",
            "fontFamily": "Inter, Montserrat, sans-serif",
            "fontWeight": "400",
            "backgroundColor": "#FFFFFF",
            "color": "#1F2937",
            "border": "1px solid #F3F4F6",
            "whiteSpace": "normal",
            "height": "auto",
            "minWidth": "120px",
            "maxWidth": "200px",
            "textOverflow": "ellipsis"
        },
        
        # Professional header styling
        style_header={
            "backgroundColor": "#F8FAFC",
            "color": "#1F2937",
            "fontWeight": "600",
            "fontSize": "0.95rem",
            "fontFamily": "Inter, Montserrat, sans-serif",
            "textAlign": "center",
            "padding": "1rem 0.75rem",
            "border": "1px solid #E5E7EB",
            "borderBottom": "2px solid #2563EB",  # Olympic blue accent
            "textTransform": "uppercase",
            "letterSpacing": "0.5px"
        },
        
        # Enhanced conditional styling
        style_data_conditional=[
            # Alternating row colors
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#F9FAFB"
            },
            # Hover effect
            {
                "if": {"state": "active"},
                "backgroundColor": "#EFF6FF",
                "border": "1px solid #2563EB"
            },
            # Selected rows
            {
                "if": {"state": "selected"},
                "backgroundColor": "#2563EB",
                "color": "#FFFFFF",
                "fontWeight": "500"
            },
            # Gender-based styling
            {
                "if": {
                    "filter_query": "{gender} = M",
                    "column_id": "gender"
                },
                "backgroundColor": "#EBF8FF",
                "color": "#2563EB",
                "fontWeight": "600"
            },
            {
                "if": {
                    "filter_query": "{gender} = F", 
                    "column_id": "gender"
                },
                "backgroundColor": "#FEF2F2",
                "color": "#DC2626",
                "fontWeight": "600"
            },
            # Year-based highlighting for recent Olympics
            {
                "if": {
                    "filter_query": "{year} >= 2000",
                    "column_id": "year"
                },
                "backgroundColor": "#F0FDF4",
                "color": "#059669",
                "fontWeight": "600"
            }
        ],
        
        # Column-specific styling
        style_cell_conditional=[
            {
                "if": {"column_id": "athlete_name"},
                "textAlign": "left",
                "fontWeight": "500",
                "minWidth": "180px",
                "maxWidth": "250px"
            },
            {
                "if": {"column_id": "country"},
                "textAlign": "center",
                "minWidth": "120px",
                "maxWidth": "150px"
            },
            {
                "if": {"column_id": "year"},
                "textAlign": "center",
                "fontWeight": "600",
                "minWidth": "80px",
                "maxWidth": "100px"
            },
            {
                "if": {"column_id": "sport"},
                "textAlign": "left",
                "minWidth": "140px",
                "maxWidth": "180px"
            },
            {
                "if": {"column_id": "gender"},
                "textAlign": "center",
                "fontWeight": "600",
                "minWidth": "80px",
                "maxWidth": "100px"
            }
        ],
        
        # Pagination styling
        style_as_list_view=False,  # Use grid view for better appearance
        
        # Tooltip configuration
        tooltip_data=[
            {
                column: {
                    'value': f"**{row[column]}**" if column == 'athlete_name' 
                    else f"🏃‍♂️ Athlete: **{row['athlete_name']}**\n🌍 Country: **{row['country']}**\n📅 Year: **{row['year']}**\n🏅 Sport: **{row['sport']}**\n⚧ Gender: **{row['gender']}**",
                    'type': 'markdown'
                } for column in row.keys()
            } for row in athlete_participation_data[:100]  # Limit tooltips for performance
        ],
        tooltip_duration=None
    )
], style={
    "background": "#FFFFFF",
    "borderRadius": "4px",  # Sharp corners
    "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
    "border": "1px solid #D1D5DB",
    "padding": "2rem",
    "marginTop": "2rem",
    "marginBottom": "2rem"
})

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
    # Start with the full dataset
    filtered = athlete_participation_data.copy()
    
    # Apply year filter
    if year and year != 'All':
        filtered = [row for row in filtered if row['year'] == year]
    
    # Apply gender filter  
    if gender:
        filtered = [row for row in filtered if row['gender'] == gender]
    
    # Apply sport filter
    if sport:
        filtered = [row for row in filtered if row['sport'] == sport]
    
    # Apply country filter
    if country:
        filtered = [row for row in filtered if row['country'] == country]
    
    # Debug print to check filtering
    print(f"Filters applied - Year: {year}, Gender: {gender}, Sport: {sport}, Country: {country}")
    print(f"Filtered results count: {len(filtered)}")
    
    return filtered

# Comprehensive callback for all analytical dashboard charts
@app.callback(
    [
        Output('gender-distribution-chart', 'figure'),
        Output('participation-trend-chart', 'figure'),
        Output('top-events-chart', 'figure'),
    ],
    [
        Input('athlete-table-year', 'value'),
        Input('athlete-table-gender', 'value'),
        Input('athlete-table-sport', 'value'),
        Input('athlete-table-country', 'value'),
    ]
)
def update_analytical_charts(year, gender, sport, country):
    # Update gender distribution (exclude gender filter to avoid empty results)
    gender_dist_fig = create_filtered_gender_distribution(
        year=year, 
        sport=sport, 
        country=country
    )
    
    # Update participation trend (exclude year filter since it's the x-axis)
    participation_trend_fig = create_filtered_gender_participation_trend(
        gender=gender,
        sport=sport, 
        country=country
    )
    
    # Update top events
    top_events_fig = create_filtered_top_events(
        year=year, 
        gender=gender, 
        country=country
    )
    
    print(f"Updated analytical charts with filters - Year: {year}, Gender: {gender}, Sport: {sport}, Country: {country}")
    
    return gender_dist_fig, participation_trend_fig, top_events_fig

# Callback for tactical dashboard NOC medal table
@app.callback(
    Output('noc-medal-table', 'data'),
    [
        Input('athlete-table-year', 'value'),
        Input('athlete-table-gender', 'value'),
        Input('athlete-table-sport', 'value'),
        Input('athlete-table-country', 'value'),
    ]
)
def update_noc_medal_table(year, gender, sport, country):
    # Get filtered NOC medal data
    filtered_data = get_filtered_noc_medal_table(year, gender, sport, country)
    
    # Debug print to check filtering
    print(f"NOC Table Filters applied - Year: {year}, Gender: {gender}, Sport: {sport}, Country: {country}")
    print(f"NOC Table filtered results count: {len(filtered_data)}")
    
    return filtered_data

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
    # Modern section header with Olympic styling
    html.Div([
        html.Div([
            html.H3("Olympic Medal Standings by NOC", style={
                "fontSize": "1.5rem",
                "fontWeight": "700",
                "color": "#1F2937",
                "marginBottom": "0.3rem",
                "fontFamily": "Inter, Montserrat, sans-serif",
                "display": "inline-block"
            })
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "0.5rem"})
    ], style={
        "marginBottom": "1.5rem",
        "paddingBottom": "1rem",
        "borderBottom": "2px solid #E5E7EB"
    }),
    
    # Enhanced DataTable with medal-specific styling
    dash_table.DataTable(
        id='noc-medal-table',
        columns=[
            {
                "name": "Team/NOC", 
                "id": "team_noc",
                "type": "text"
            },
            {
                "name": "Gold", 
                "id": "gold", 
                "type": "numeric",
                "format": {"specifier": ",d"}
            },
            {
                "name": "Silver", 
                "id": "silver", 
                "type": "numeric",
                "format": {"specifier": ",d"}
            },
            {
                "name": "Bronze", 
                "id": "bronze", 
                "type": "numeric",
                "format": {"specifier": ",d"}
            }
        ],
        data=noc_medal_table,
        
        # Enhanced functionality
        page_size=25,
        page_action="native",
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        selected_rows=[],
        
        # Fixed rows for better UX
        fixed_rows={"headers": True, "data": 0},
        
        # Modern styling for the table container
        style_table={
            "height": "600px",
            "overflowY": "auto",
            "overflowX": "auto",
            "minWidth": "100%",
            "background": "#FFFFFF",
            "borderRadius": "4px",  # Sharp corners matching dashboard
            "border": "1px solid #D1D5DB",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.15)"
        },
        
        # Enhanced cell styling
        style_cell={
            "padding": "1rem 0.75rem",
            "fontSize": "0.9rem",
            "textAlign": "left",
            "fontFamily": "Inter, Montserrat, sans-serif",
            "fontWeight": "400",
            "backgroundColor": "#FFFFFF",
            "color": "#1F2937",
            "border": "1px solid #F3F4F6",
            "whiteSpace": "normal",
            "height": "auto",
            "minWidth": "120px",
            "textOverflow": "ellipsis"
        },
        
        # Professional header styling
        style_header={
            "backgroundColor": "#F8FAFC",
            "color": "#1F2937",
            "fontWeight": "600",
            "fontSize": "0.95rem",
            "fontFamily": "Inter, Montserrat, sans-serif",
            "textAlign": "center",
            "padding": "1rem 0.75rem",
            "border": "1px solid #E5E7EB",
            "borderBottom": "2px solid #F59E0B",  # Olympic gold accent
            "textTransform": "uppercase",
            "letterSpacing": "0.5px"
        },
        
        # Enhanced conditional styling with medal colors
        style_data_conditional=[
            # Alternating row colors
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#F9FAFB"
            },
            # Hover effect
            {
                "if": {"state": "active"},
                "backgroundColor": "#FFFBEB",
                "border": "1px solid #F59E0B"
            },
            # Selected rows
            {
                "if": {"state": "selected"},
                "backgroundColor": "#F59E0B",
                "color": "#FFFFFF",
                "fontWeight": "500"
            },
            # Gold medal column styling
            {
                "if": {"column_id": "gold"},
                "backgroundColor": "#FFFBEB",
                "color": "#D97706",
                "fontWeight": "700",
                "textAlign": "center"
            },
            # Silver medal column styling
            {
                "if": {"column_id": "silver"},
                "backgroundColor": "#F8FAFC",
                "color": "#6B7280",
                "fontWeight": "600",
                "textAlign": "center"
            },
            # Bronze medal column styling
            {
                "if": {"column_id": "bronze"},
                "backgroundColor": "#FEF7F0",
                "color": "#C2410C",
                "fontWeight": "600",
                "textAlign": "center"
            },
            # Highlight high-performing countries
            {
                "if": {
                    "filter_query": "{gold} > 10"
                },
                "backgroundColor": "#FEF3C7",
                "fontWeight": "600"
            }
        ],
        
        # Column-specific styling
        style_cell_conditional=[
            {
                "if": {"column_id": "team_noc"},
                "textAlign": "left",
                "fontWeight": "500",
                "minWidth": "200px",
                "maxWidth": "300px"
            },
            {
                "if": {"column_id": "gold"},
                "textAlign": "center",
                "fontWeight": "700",
                "minWidth": "100px",
                "maxWidth": "120px"
            },
            {
                "if": {"column_id": "silver"},
                "textAlign": "center",
                "fontWeight": "600",
                "minWidth": "100px",
                "maxWidth": "120px"
            },
            {
                "if": {"column_id": "bronze"},
                "textAlign": "center",
                "fontWeight": "600",
                "minWidth": "100px",
                "maxWidth": "120px"
            }
        ],
        
        # Pagination styling
        style_as_list_view=False,  # Use grid view for better appearance
        
        # Tooltip configuration for medals
        tooltip_data=[
            {
                column: {
                    'value': f"**{row[column]}**" if column == 'team_noc' 
                    else f"🏆 **{row['team_noc']}** Medal Count\n🥇 Gold: **{row['gold']}**\n🥈 Silver: **{row['silver']}**\n🥉 Bronze: **{row['bronze']}**\n📊 Total: **{row['gold'] + row['silver'] + row['bronze']}**",
                    'type': 'markdown'
                } for column in row.keys()
            } for row in noc_medal_table[:100]  # Limit tooltips for performance
        ],
        tooltip_duration=None
    )
], style={
    "background": "#FFFFFF",
    "borderRadius": "4px",  # Sharp corners
    "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
    "border": "1px solid #D1D5DB",
    "padding": "2rem",
    "marginTop": "2rem",
    "marginBottom": "2rem"
})

# Comprehensive callback for tactical dashboard charts
@app.callback(
    [
        Output('medal-by-country-gender-chart', 'figure'),
        Output('tactical-top-sports-chart', 'figure'),
    ],
    [
        Input('athlete-table-year', 'value'),
        Input('athlete-table-gender', 'value'),
        Input('athlete-table-sport', 'value'),
        Input('athlete-table-country', 'value'),
    ]
)
def update_tactical_charts(year, gender, sport, country):
    # Update medal by country gender (exclude gender filter to show comparison)
    medal_country_gender_fig = create_filtered_medal_by_country_gender(
        year=year, 
        sport=sport, 
        country=country
    )
    
    # Update top sports
    top_sports_fig = create_filtered_top_sports(
        year=year, 
        gender=gender, 
        country=country
    )
    
    print(f"Updated tactical charts with filters - Year: {year}, Gender: {gender}, Sport: {sport}, Country: {country}")
    
    return medal_country_gender_fig, top_sports_fig

# Move this block up, before analyical_content_layout and tactical_content_layout definitions:
dashboard_header = dbc.Row([
    # Left section: Breadcrumb and Title
    dbc.Col([
        html.Div([
            html.I(className="bi bi-house-door me-1"),
            html.Span("/", className="mx-1 text-secondary"),
            html.Span("Dashboard", className="fw-medium")
        ], className="d-flex align-items-center small"),
        html.H1(id="dashboard-title", className="fw-bold fs-4 mb-0", style={"marginTop": "0.3rem"}),
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
    
    # NEW: Top KPI Cards Section for Sports Researchers
    html.Div([
        html.H2("🎯 Sports Research Overview", 
               style={"fontSize": "1.6rem", "fontWeight": "bold", "color": "#00274D", 
                     "marginBottom": "1.5rem", "fontFamily": "Montserrat, sans-serif",
                     "borderBottom": "3px solid #2563EB", "paddingBottom": "0.5rem"}),
        
        # KPI Cards Row - Using Direct HTML for Better Visibility
        dbc.Row([
            # Total Athletes Card
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H6("Total Athletes", style={
                            "color": "#2563EB", 
                            "fontSize": "1.1rem", 
                            "fontWeight": "600",
                            "marginBottom": "0.5rem",
                            "fontFamily": "Montserrat, sans-serif"
                        }),
                        html.H2(f"{analyical_figures['summary_cards'][0].data[0]['value']:,}", style={
                            "color": "#2563EB", 
                            "fontSize": "2.5rem", 
                            "fontWeight": "bold",
                            "marginBottom": "0",
                            "fontFamily": "Montserrat, sans-serif",
                            "lineHeight": "1.2"
                        })
                    ], style={
                        "textAlign": "center",
                        "padding": "2rem 1rem"
                    })
                ], style={
                    "background": "white",
                    "borderRadius": "4px",  # Sharp corners
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                    "border": f"2px solid #2563EB",
                    "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                    "height": "140px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }, className="kpi-card-container")
            ], width=3, className="mb-3"),
            
            # Gender Ratio Card
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H6("Gender Ratio", style={
                            "color": "#DC2626", 
                            "fontSize": "1.1rem", 
                            "fontWeight": "600",
                            "marginBottom": "0.3rem",
                            "fontFamily": "Montserrat, sans-serif"
                        }),
                        html.H2("69.5% ♂", style={
                            "color": "#DC2626", 
                            "fontSize": "2.2rem", 
                            "fontWeight": "bold",
                            "marginBottom": "0.2rem",
                            "fontFamily": "Montserrat, sans-serif",
                            "lineHeight": "1.2"
                        }),
                        html.P("♂ 69.5% | ♀ 30.5%", style={
                            "color": "#666", 
                            "fontSize": "0.9rem", 
                            "marginBottom": "0",
                            "fontFamily": "Montserrat, sans-serif"
                        })
                    ], style={
                        "textAlign": "center",
                        "padding": "1.5rem 1rem"
                    })
                ], style={
                    "background": "white",
                    "borderRadius": "4px",  # Sharp corners
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                    "border": f"2px solid #DC2626",
                    "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                    "height": "140px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }, className="kpi-card-container")
            ], width=3, className="mb-3"),
            
            # Number of Sports Card
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H6("Number of Sports", style={
                            "color": "#059669", 
                            "fontSize": "1.1rem", 
                            "fontWeight": "600",
                            "marginBottom": "0.5rem",
                            "fontFamily": "Montserrat, sans-serif"
                        }),
                        html.H2(f"{analyical_figures['summary_cards'][1].data[0]['value']:,}", style={
                            "color": "#059669", 
                            "fontSize": "2.5rem", 
                            "fontWeight": "bold",
                            "marginBottom": "0",
                            "fontFamily": "Montserrat, sans-serif",
                            "lineHeight": "1.2"
                        })
                    ], style={
                        "textAlign": "center",
                        "padding": "2rem 1rem"
                    })
                ], style={
                    "background": "white",
                    "borderRadius": "4px",  # Sharp corners
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                    "border": f"2px solid #059669",
                    "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                    "height": "140px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }, className="kpi-card-container")
            ], width=3, className="mb-3"),
            
            # Median Athlete Age Card
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H6("Median Athlete Age", style={
                            "color": "#F59E0B", 
                            "fontSize": "1.1rem", 
                            "fontWeight": "600",
                            "marginBottom": "0.5rem",
                            "fontFamily": "Montserrat, sans-serif"
                        }),
                        html.H2("24.2 yrs", style={
                            "color": "#F59E0B", 
                            "fontSize": "2.5rem", 
                            "fontWeight": "bold",
                            "marginBottom": "0",
                            "fontFamily": "Montserrat, sans-serif",
                            "lineHeight": "1.2"
                        })
                    ], style={
                        "textAlign": "center",
                        "padding": "2rem 1rem"
                    })
                ], style={
                    "background": "white",
                    "borderRadius": "4px",  # Sharp corners
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                    "border": f"2px solid #F59E0B",
                    "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                    "height": "140px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }, className="kpi-card-container")
            ], width=3, className="mb-3")
        ], className="mb-4")
    ], style={"marginBottom": "3rem"}),
    
    # Section 1: Geographic Analysis
    html.Div([
        html.H2("Geographic Analysis", 
               style={"fontSize": "1.4rem", "fontWeight": "bold", "color": "#00274D", 
                     "marginBottom": "1.5rem", "fontFamily": "Montserrat, sans-serif",
                     "borderBottom": "2px solid #00274D", "paddingBottom": "0.5rem"}),
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
                        "borderRadius": "4px",  # Sharp corners
                        "padding": "1rem",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                        "border": "1px solid #D1D5DB"
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
            "marginBottom": "3rem",
            "flexWrap": "wrap",  # Allows wrapping on smaller screens
            "alignItems": "stretch"  # Makes both containers same height
        })
    ], style={"marginBottom": "3rem"}),
    
    # Section 2: Gender & Demographics
    html.Div([
        html.H2("Gender & Demographics", 
               style={"fontSize": "1.4rem", "fontWeight": "bold", "color": "#00274D", 
                     "marginBottom": "1.5rem", "fontFamily": "Montserrat, sans-serif",
                     "borderBottom": "2px solid #00274D", "paddingBottom": "0.5rem"}),
        # Gender Distribution and Participation Trend
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='gender-distribution-chart',  # Added ID for callback
                    figure=analyical_figures['gender_distribution'],
                    style={
                        "height": "440px",
                        "minHeight": "340px",
                        "background": "#fff",
                        "borderRadius": "4px",  # Sharp corners
                        "padding": "1rem",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                        "border": "1px solid #D1D5DB"
                    }
                )
            ], width=4, style={"minWidth": 0}),  # Smaller pie chart
            dbc.Col([
                dcc.Graph(
                    id='participation-trend-chart',  # Added ID for callback
                    figure=analyical_figures['gender_participation_trend'],
                    style={
                        "height": "440px",
                        "minHeight": "340px",
                        "background": "#fff",
                        "borderRadius": "4px",  # Sharp corners
                        "padding": "1rem",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                        "border": "1px solid #D1D5DB"
                    }
                )
            ], width=8, style={"minWidth": 0})  # Larger line chart
        ], className="mb-4")
    ], style={"marginBottom": "3rem"}),
    
    # Section 3: Sport & Participation Trends
    html.Div([
        html.H2("Sport & Participation Trends", 
               style={"fontSize": "1.4rem", "fontWeight": "bold", "color": "#00274D", 
                     "marginBottom": "1.5rem", "fontFamily": "Montserrat, sans-serif",
                     "borderBottom": "2px solid #00274D", "paddingBottom": "0.5rem"}),
        # Sport Distribution and Top Events
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='sport-distribution-chart',  # Added ID for callback
                    figure=analyical_figures['sport_distribution'],
                    style={
                        "height": "440px",
                        "minHeight": "340px",
                        "background": "#fff",
                        "borderRadius": "4px",  # Sharp corners
                        "padding": "1rem",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                        "border": "1px solid #D1D5DB"
                    }
                )
            ], width={"size": 7, "sm": 12, "md": 7, "lg": 7}, style={"minWidth": 0}),
            dbc.Col([
                dcc.Graph(
                    id='top-events-chart',  # Added ID for callback
                    figure=analyical_figures['top_events'],
                    style={
                        "height": "440px",
                        "minHeight": "340px",
                        "background": "#fff",
                        "borderRadius": "4px",  # Sharp corners
                        "padding": "1rem",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                        "border": "1px solid #D1D5DB"
                    }
                )
            ], width={"size": 5, "sm": 12, "md": 5, "lg": 5}, style={"minWidth": 0})
        ], className="mb-4"),
        # Athlete Participation Table
        analyical_athlete_table_layout
    ], style={"marginBottom": "3rem"})
    
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
                id='medal-by-country-gender-chart',  # Added ID for callback
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
                id='tactical-top-sports-chart',  # Added ID for callback
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

@app.callback(
    Output('dashboard-title', 'children'),
    [Input('url', 'pathname')]
)
def update_dashboard_title(pathname):
    if pathname == "/tactical":
        return "Tactical Dashboard"
    elif pathname == "/analytical":
        return html.Div([
            html.H1("Olympic Analytical Dashboard", 
                   className="fw-bold mb-1", 
                   style={"fontSize": "1.5rem", "color": "#00274D", "fontFamily": "Montserrat, sans-serif"}),
            html.P("A historical and demographic analysis for sports researchers", 
                  className="text-muted mb-0", 
                  style={"fontSize": "0.9rem", "fontFamily": "Montserrat, sans-serif"})
        ])
    else:
        return html.Div([
            html.H1("Olympic Analytical Dashboard", 
                   className="fw-bold mb-1", 
                   style={"fontSize": "1.5rem", "color": "#00274D", "fontFamily": "Montserrat, sans-serif"}),
            html.P("A historical and demographic analysis for sports researchers", 
                  className="text-muted mb-0", 
                  style={"fontSize": "0.9rem", "fontFamily": "Montserrat, sans-serif"})
        ])  # Default

if __name__ == '__main__':
    app.run(debug=True) 