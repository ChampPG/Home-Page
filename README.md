# Home Page & Uptime Tracker

A modern, real-time uptime monitoring system with a beautiful web interface built with Flask (backend) and React + Material-UI (frontend). Monitor your services, track downtime events, and visualize historical data with a sleek Catppuccin Mocha theme.

![Uptime Tracker](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![React](https://img.shields.io/badge/React-19.1.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 🔍 **Multi-Protocol Service Monitoring**
- **HTTP Services**: Web applications, APIs, and web services
- **WireGuard VPN**: UDP-based VPN monitoring (This doesn't actually tell you if it's up or down as wiregaurd drops all packets that don't contain the correct key data)
- **Host Monitoring**: Ping-based host availability
- **Services Monitoring**: Plex, Radarr, Sonarr, Tautulli, Overseerr, qBittorrent, Autobrr, Prowlarr, FlareSolverr, Nginx, Syncthing, Syncthing Relay
- **Redirect Services**: Quick access links

### 📊 **Real-Time Dashboard**
- **Live Status Updates**: Real-time service status monitoring
- **Response Time Tracking**: Monitor service performance
- **Historical Data**: 24-hour service history with charts
- **Downtime Events**: Track and display service outages
- **Service Grouping**: Organize services by hosts and categories

### 🎨 **Beautiful UI**
- **Catppuccin Mocha Theme**: Modern dark theme with beautiful colors
- **Service Logos**: Custom logos for each service
- **Responsive Design**: Works on desktop and mobile
- **Interactive Charts**: Historical data visualization
- **Material-UI Components**: Professional, accessible interface
- **Real-Time Duration**: Live uptime/downtime duration display
- **Status Indicators**: Color-coded status and duration information

### 🚀 **Advanced Features**
- **Automatic Scheduling**: Configurable check intervals
- **In-Memory Storage**: Fast, lightweight data storage with automatic cleanup
- **Docker Support**: Easy deployment with Docker Compose
- **Health Checks**: Built-in monitoring for the monitoring system
- **RESTful API**: JSON API for external integrations

## 🏗️ Architecture

```
uptime-tracker/
├── backend/                 # Flask backend
│   ├── apis/               # Service detection modules
│   │   ├── http_status.py
│   │   ├── ssh_status.py
│   │   ├── wireguard_status.py
│   │   ├── syncthing_status.py
│   │   ├── host_status.py
│   │   ├── port_status.py
│   │   ├── plex_status.py
│   │   ├── radarr_status.py
│   │   ├── sonarr_status.py
│   │   ├── tautulli_status.py
│   │   ├── overseerr_status.py
│   │   ├── qbit_status.py
│   │   ├── autobrr_status.py
│   │   ├── prowlarr_status.py
│   │   ├── flaresolverr_status.py
│   │   └── nginx_status.py
│   ├── external/           # Configuration
│   │   └── config.json     # Configuration file
│   ├── app.py             # Main Flask application
│   ├── sharedutil.py      # Shared utilities
│   ├── testing.py         # Testing utilities
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── ServiceHistoryChart.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   │   └── assets/
│   │       └── services/   # Service logos
│   └── package.json
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/uptime-tracker.git
   cd uptime-tracker
   ```

2. **Configure your services**
   ```bash
   cp backend/external/config-example.json backend/external/config.json
   # Edit config.json with your services
   ```

3. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Access the dashboard**
   Open your browser to `http://localhost:5000`

### Option 2: Local Development

#### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run build
```

#### Run the Application
```bash
# Terminal 1: Backend
cd backend
python app.py
```

## ⚙️ Configuration

### Service Configuration (`backend/external/config.json`)

```json
[
  {
    "interval": 60,
    "categories": ["media", "homelab", "downloads"],
    "instances": [
      {
        "name": "Plex Media Server",
        "type": "plex",
        "ping_url": "http://192.168.0.84:32400",
        "public_url": "https://plex.yourdomain.com",
        "category": "media",
        "host": "192.168.0.84",
        "icon_url": "assets/services/plex.svg"
      },
      {
        "name": "WireGuard VPN",
        "type": "wireguard",
        "ping_url": "192.168.0.84:51820",
        "public_url": "",
        "category": "homelab",
        "host": "192.168.0.84",
        "icon_url": "assets/services/wireguard.svg"
      },
      {
        "name": "qBittorrent",
        "type": "qbit",
        "ping_url": "http://192.168.0.84:8080",
        "public_url": "https://qbit.yourdomain.com",
        "category": "downloads",
        "host": "192.168.0.84",
        "icon_url": "assets/services/qbittorrent.svg"
      }
    ]
  }
]
```

### Service Types

| Type | Description | Example |
|------|-------------|---------|
| `http` | HTTP/HTTPS web services | `http://192.168.0.84:3000` |
| `ssh` | SSH services | `192.168.0.84:22` |
| `wireguard` | WireGuard VPN (UDP) | `192.168.0.84:51820` |
| `syncthing` | Syncthing services | `192.168.0.84:22067` |
| `host` | Host availability (ping) | `192.168.0.84` |
| `port` | Generic port monitoring | `192.168.0.84:8080` |
| `plex` | Plex Media Server | `http://192.168.0.84:32400` |
| `radarr` | Radarr | `http://192.168.0.84:7878` |
| `sonarr` | Sonarr | `http://192.168.0.84:8989` |
| `tautulli` | Tautulli | `http://192.168.0.84:8181` |
| `overseerr` | Overseerr | `http://192.168.0.84:5055` |
| `qbit` | qBittorrent | `http://192.168.0.84:8080` |
| `autobrr` | Autobrr | `http://192.168.0.84:7474` |
| `prowlarr` | Prowlarr | `http://192.168.0.84:9696` |
| `flaresolverr` | FlareSolverr | `http://192.168.0.84:8191` |
| `nginx` | Nginx | `http://192.168.0.84:80` |
| `redirect` | External links | No ping_url needed |

### Configuration Options

- **`interval`**: Check frequency in seconds (default: 60)
- **`categories`**: Service categories for organization
- **`host`**: Group services under specific hosts
- **`icon_url`**: Path to service logo (SVG recommended)
- **`public_url`**: External URL for service access

## 🎨 Customization

### Adding Service Logos

1. Add your SVG logo to `frontend/public/assets/services/`
2. Reference it in config.json: `"icon_url": "assets/services/yourlogo.svg"`
3. Logos are automatically styled for the dark theme

### Theme Customization

The frontend uses the Catppuccin Mocha color palette. You can customize colors in `frontend/src/App.jsx`:

```javascript
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#89b4fa', // Blue
    },
    // ... more color customizations
  }
})
```

### Adding New Service Types

1. Create a new service file in `backend/apis/`
2. Implement the detection logic
3. Add the service type to `app.py`
4. Update your config.json

## 📊 API Endpoints

### Get All Services
```http
GET /api/v1/services
```

Response:
```json
{
  "services": [
    {
      "name": "My Service",
      "status": "up",
      "response_time": 45,
      "last_check": "2025-01-14T10:30:00",
      "category": "homelab",
      "public_url": "https://myservice.com",
      "icon_url": "assets/services/myservice.svg"
    }
  ],
  "downtime_events": [...],
  "categories": ["media", "homelab", "downloads"]
}
```

### Get Service History
```http
GET /api/v1/services/history
```

## 🐳 Docker Deployment

### Production Deployment
```bash
# Build and run in production mode
docker-compose -f docker-compose.yml up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables
- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_APP`: Main application file (default: `app.py`)

## 🔧 Development

### Project Structure
- **Backend**: Flask application with modular service detection
- **Frontend**: React with Material-UI and Chart.js
- **In-Memory Storage**: Fast, lightweight data storage with automatic cleanup
- **Docker**: Multi-stage build for optimized containers

### Adding New Features
1. Backend changes: Modify Flask app and service modules
2. Frontend changes: Update React components
3. Configuration: Add new service types to config.json

### Testing
```bash
# Test WireGuard detection
cd backend
python testing.py

# Test individual services
python -c "import apis.wireguard_status; print(apis.wireguard_status.get_wireguard_status('192.168.0.84:51820'))"
```

## 📈 Monitoring Features

### Real-Time Monitoring
- **Automatic Checks**: Configurable intervals (default: 60 seconds)
- **3-Check System**: Services must fail 3 consecutive checks before being marked as down
- **Response Time Tracking**: Monitor service performance
- **Status History**: Track service availability over time
- **Downtime Detection**: Automatic detection of service outages
- **False Positive Prevention**: Reduces false alarms from temporary network issues

### Historical Data
- **24-Hour Charts**: Visualize service performance
- **Uptime Statistics**: Calculate service availability
- **Response Time Trends**: Monitor performance changes
- **Downtime Events**: Track and analyze outages

### Service Grouping
- **Host-Based Organization**: Group services by physical/virtual hosts
- **Category Organization**: Organize by service type or purpose
- **Visual Hierarchy**: Clear service relationships in the UI

### Logs and Debugging
```bash
# View application logs
docker-compose logs -f uptime-tracker

# Check service status
curl http://localhost:5000/api/v1/services

# Test individual service detection
cd backend
python -c "import apis.http_status; print(apis.http_status.get_http_status('http://localhost:3000'))"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Catppuccin** for the beautiful color palette
- **Material-UI** for the component library
- **Chart.js** for data visualization
- **Flask** for the backend framework
- **React** for the frontend framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ChampPG/Home-Page/issues)
- **Email**: ppgleason02@gmail.com
- **Website**: https://home.paulgleason.dev

---

**Built with ❤️ by Paul Gleason**