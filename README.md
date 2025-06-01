# 🏅 Olympic Games Dashboard

A comprehensive Flask-based dashboard system for analyzing Olympic Games data with three specialized views: Strategic, Operational, and Analytical dashboards.

![Olympic Dashboard](https://img.shields.io/badge/Olympic-Dashboard-blue.svg?style=for-the-badge&logo=medal)

## 🌟 Features

### 🎯 Strategic Dashboard
- **Medal Analysis**: Country-wise medal distribution and trends
- **Performance Metrics**: Top performing countries and athletes
- **Participation Trends**: Historical data showing Olympic growth
- **Interactive Charts**: Bar charts, pie charts, and trend lines

### ⚙️ Operational Dashboard
- **Event Management**: Sports and events tracking
- **Athlete Performance**: Real-time performance monitoring
- **Operational Status**: System health and alerts
- **Resource Allocation**: Events distribution across sports

### 📊 Analytical Dashboard
- **Demographics Analysis**: Age and gender distribution
- **Deep Insights**: AI-generated insights and patterns
- **Predictive Analytics**: Growth projections and forecasts
- **Data Export**: CSV and JSON export capabilities

## 🎨 Design

The dashboard features the authentic **Olympic color palette**:
- 🔵 **Olympic Blue** (#0085C3)
- 🟡 **Olympic Yellow** (#FFB81C)
- ⚫ **Olympic Black** (#000000)
- 🟢 **Olympic Green** (#00A651)
- 🔴 **Olympic Red** (#EE334E)

## 🛠️ Technology Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Chart.js
- **Icons**: Font Awesome
- **Styling**: Custom CSS with Olympic themes

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Existing Olympic dataset in PostgreSQL database named **'Olympicdb'** with tables:
  - `athletes`
  - `countries`
  - `teams`
  - `sports`
  - `events`
  - `medals`
  - `games`
  - `participation`

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to your project directory
cd "3 Final Dashboard"

# Create virtual environment
python -m venv olympic_env

# Activate virtual environment
# Windows:
olympic_env\Scripts\activate
# macOS/Linux:
source olympic_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

The application is configured to connect to:
- **Database**: `Olympicdb`
- **Host**: `localhost:5432`
- **User**: `postgres`
- **Password**: `Bahardb1234`

To change the database configuration, modify the connection string in `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Bahardb1234@localhost:5432/Olympicdb'
```

### 3. Run the Application

```bash
python run.py
```
or
```bash
python app.py
```

The dashboard will be available at: `http://localhost:5000`

## 📱 Dashboard Navigation

### 🏠 Home Page
- Dashboard overview and selection
- Key statistics
- Olympic rings animation
- Quick access to all dashboards

### 📈 Strategic Dashboard (`/strategic`)
- High-level medal analytics
- Country performance comparison
- Participation trends over time
- Top performers table

### 🔧 Operational Dashboard (`/operational`)
- Events by sport analysis
- Athlete performance tracking
- Operational status monitoring
- Performance metrics

### 🧠 Analytical Dashboard (`/analytical`)
- Demographic breakdowns
- Age and gender analysis
- Predictive analytics
- Data export functionality

## 🎛️ Interactive Features

### Dynamic Filters
- **Year**: Filter by specific Olympic years
- **Country**: Focus on specific nations
- **Sport**: Analyze particular sports
- **Gender**: Demographic filtering

### Real-time Updates
- Live data refresh
- Animated counters
- Interactive charts
- Responsive design

### Data Export
- CSV format for spreadsheets
- JSON format for developers
- Real-time data snapshots

## 🏗️ Project Structure

```
3 Final Dashboard/
├── app.py                 # Main Flask application with SQLAlchemy
├── requirements.txt       # Python dependencies
├── env_example.txt       # Environment variables template (optional)
├── run.py                # Enhanced startup script
├── README.md             # Project documentation
└── templates/
    ├── base.html         # Base template with Olympic styling
    ├── index.html        # Home page
    ├── strategic.html    # Strategic dashboard
    ├── operational.html  # Operational dashboard
    └── analytical.html   # Analytical dashboard
```

## 🔧 Database Schema Expected

The application expects these table structures in your **Olympicdb** database:

```sql
-- Example table relationships
athletes(athlete_id, athlete_name, age, gender, country_id)
countries(country_id, country_name)
games(game_id, year, season, city)
sports(sport_id, sport_name)
events(event_id, event_name, sport_id)
participation(participation_id, athlete_id, event_id, game_id)
medals(medal_id, medal_type, participation_id)
```

## 📊 API Endpoints

- `GET /api/filters` - Get filter options
- `GET /api/strategic-data` - Strategic dashboard data
- `GET /api/operational-data` - Operational dashboard data
- `GET /api/analytical-data` - Analytical dashboard data

## 🎨 Customization

### Database Configuration
To modify the database connection, update the SQLAlchemy URI in `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@host:port/database_name'
```

### Styling
- Olympic color palette in CSS variables
- Responsive Bootstrap components
- Custom animations and transitions
- Font Awesome icons

### Charts
- Chart.js with Olympic themes
- Interactive tooltips
- Responsive design
- Custom color schemes

## 🔒 Security Features

- SQLAlchemy ORM for database security
- SQL injection protection via parameterized queries
- Error handling and validation
- Secure database connections

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL service is running
   - Verify database name 'Olympicdb' exists
   - Ensure credentials are correct (postgres:Bahardb1234)
   - Confirm database contains Olympic data tables

2. **Module Import Errors**
   - Activate virtual environment
   - Install all requirements: `pip install -r requirements.txt`

3. **Chart Not Loading**
   - Check browser console for JavaScript errors
   - Ensure internet connection for CDN resources

4. **SQLAlchemy Errors**
   - Ensure Flask-SQLAlchemy is installed
   - Check database table names match expected schema

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🏆 Credits

- **Olympic Colors**: Official IOC color palette
- **Icons**: Font Awesome
- **Charts**: Chart.js
- **Framework**: Bootstrap 5
- **Backend**: Flask with SQLAlchemy
- **Database**: PostgreSQL

---

**🎯 Ready to explore Olympic data like never before!**

For support or questions, please create an issue in the repository. 