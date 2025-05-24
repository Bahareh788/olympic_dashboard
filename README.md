# Olympic Games Analytics Dashboard

This project provides two interactive dashboards for analyzing Olympic Games data:
1. Analytical Dashboard - Focused on participation and diversity
2. Tactical Dashboard - Focused on medal performance and achievements

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your PostgreSQL database credentials:
```
DB_HOST=your_host
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

4. Run the application:
```bash
python app.py
```

The dashboard will be available at `http://localhost:8050`

## Features

### Analytical Dashboard
- Gender distribution analysis
- Participation trends over time
- Top events by participation
- Sport event distribution
- Geographic participation analysis

### Tactical Dashboard
- Medal distribution by country and gender
- Medalist age analysis
- Top performing sports
- Gold medal achievements
- Top performing athletes

## Color Palette
The visualizations use the Olympic ring colors:
- Blue (#0085C3)
- Yellow (#F4C300)
- Black (#000000)
- Green (#009F3D)
- Red (#DF0024) 