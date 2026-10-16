# GI4C Python Backend Integration

## Overview

The GI4C website now includes a comprehensive Python backend with Flask, database integration, AI/ML capabilities, GIS processing, and automated task scheduling.

## Features

### 1. **Flask Web Server**
- Serves static HTML/CSS/JS files
- RESTful API endpoints for all features
- CORS enabled for frontend integration

### 2. **Database (SQLAlchemy)**
- SQLite (default) or PostgreSQL support
- Models for: Users, Programs, ImpactData, TeamMembers, Donations, GISLocations, AIConversations, Reports, ScheduledTasks

### 3. **AI Assistant**
- OpenAI GPT integration (with demo fallback)
- Knowledge base about GI4C programs and mission
- Conversation history tracking
- Sentiment analysis and entity extraction

### 4. **Payment Processing**
- Monetbil integration for FCFA payments
- Orange Money support
- Webhook handling for payment notifications
- Demo mode for testing

### 5. **Data Processing & Analytics**
- KPI calculation and dashboard data
- Impact metrics and trend analysis
- Automated report generation (situation, policy, warning)
- Data export (CSV, JSON)

### 6. **GIS/Geospatial**
- GeoJSON conversion
- Interactive map generation (Folium)
- Heatmaps and vulnerability maps
- Distance calculations
- Location import/export

### 7. **Task Scheduling**
- Automated data synchronization
- Scheduled report generation
- Alert monitoring
- Database backups
- Cron-based scheduling

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start (Windows)

1. **Run the startup script:**
   ```bash
   start-python.bat
   ```

   This will:
   - Create a virtual environment
   - Install all dependencies
   - Start the Flask server on http://localhost:5000

### Manual Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env` and update:
   ```env
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///gi4c.db
   OPENAI_API_KEY=your-openai-api-key  # Optional
   MONETBIL_SERVICE_KEY=your-key       # Optional
   ```

5. **Run the server:**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### AI Assistant
- `POST /api/ai-assistant` - Send message to AI
- `GET /api/ai-assistant/history/<session_id>` - Get conversation history

### Payments
- `POST /api/payment/create` - Create payment
- `POST /api/payment/notify` - Payment webhook
- `GET /api/payment/status/<transaction_id>` - Check status

### Dashboard
- `GET /api/dashboard/kpi` - Get KPI data
- `GET /api/dashboard/programs` - Get programs data
- `GET /api/dashboard/impact` - Get impact data
- `GET /api/dashboard/reports` - Get published reports

### GIS
- `GET /api/gis/locations` - Get all locations (GeoJSON)
- `POST /api/gis/locations` - Add new location
- `GET /api/gis/map` - Generate interactive map

### Data Management
- `GET /api/data/programs` - Get all programs
- `POST /api/data/programs` - Create program
- `GET /api/data/team` - Get team members

### Reports
- `POST /api/reports` - Create report
- `POST /api/reports/<id>/publish` - Publish report

## Database Models

### Program
- name, description, category, status
- beneficiaries, region, dates
- metadata (JSON)

### ImpactData
- program_id, metric_name, metric_value
- metric_unit, date_recorded, region
- metadata (JSON)

### Donation
- donor_name, donor_email, amount
- payment_method, transaction_id, status
- metadata (JSON)

### GISLocation
- program_id, name, latitude, longitude
- location_type, properties (JSON)

### AIConversation
- session_id, user_message, bot_response
- timestamp, metadata (JSON)

## Frontend Integration

The frontend has been updated to connect to the Python backend:

1. **AI Assistant** - Now calls `/api/ai-assistant` with session management
2. **Dashboard** - Can load data from `/api/dashboard/kpi` and other endpoints
3. **GIS Maps** - Can fetch locations from `/api/gis/locations`

## Optional Features

### OpenAI Integration
Add your API key to `.env`:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

Without this, the AI assistant runs in demo mode with keyword matching.

### PostgreSQL Database
Change in `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost/gi4c
```

### GIS Libraries
Install for full map functionality:
```bash
pip install geopandas folium shapely
```

## Task Scheduling

The scheduler can automate tasks like:
- Daily data sync: `0 2 * * *` (2 AM daily)
- Weekly reports: `0 8 * * 1` (8 AM Monday)
- Hourly alerts: `0 * * * *` (every hour)

Add tasks programmatically or via database.

## Development

### Adding New API Endpoints
1. Add route in `routes.py`
2. Add business logic in appropriate service file
3. Update database models if needed in `models.py`

### Adding New Services
Create a new service file (e.g., `new_service.py`) and import in `routes.py`.

### Database Migrations
For production, use Flask-Migrate:
```bash
flask db init
flask db migrate -m "description"
flask db upgrade
```

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
Set in production:
- `FLASK_ENV=production`
- `DEBUG=False`
- Strong `SECRET_KEY`
- Production database URL
- API keys for services

## Troubleshooting

### Python not found
Install Python from https://python.org and ensure it's in PATH.

### Port already in use
Change port in `.env`:
```env
PORT=5001
```

### Database errors
Delete `gi4c.db` and restart to recreate with new schema.

### Import errors
Ensure virtual environment is activated and dependencies installed.

## File Structure

```
GI4C-RT/
├── app.py              # Main Flask application
├── models.py           # Database models
├── routes.py           # API endpoints
├── ai_service.py       # AI/ML integration
├── payment_service.py  # Payment processing
├── data_processor.py   # Data analytics
├── gis_service.py      # GIS processing
├── scheduler.py        # Task automation
├── requirements.txt    #pip dependencies
├── .env                # Environment variables
├── start-python.bat    # Windows startup script
├── index.html          # Frontend (served by Flask)
├── styles.css          # Styles
├── nav.js              # Frontend JavaScript
└── [other HTML pages]
```

## Support

For issues or questions:
- Email: info@gi4c.org
- Check logs in console for errors
- Review API responses in browser DevTools
