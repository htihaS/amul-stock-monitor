# Amul Stock Monitor

A Flask-based web application that monitors the availability of Amul Whey Protein on the Amul online store and sends Telegram notifications when the product becomes available.

## Features

- **Automated Monitoring**: Checks product availability every hour
- **Telegram Notifications**: Instant alerts when product becomes available
- **Web Dashboard**: Control monitoring and view activity logs
- **Robust Detection**: Multiple strategies to detect product availability
- **Error Handling**: Comprehensive logging and error recovery

## Setup

### Prerequisites

- Python 3.11+
- Telegram Bot Token and Chat ID

### Installation

1. Clone the repository:
```bash
git clone https://github.com/htihaS/amul-stock-monitor.git
cd amul-stock-monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
export SESSION_SECRET="your-secret-key"
```

4. Run the application:
```bash
python main.py
```

5. Open your browser to `http://localhost:5000`

### Getting Telegram Credentials

1. **Bot Token**: Message @BotFather on Telegram, create a new bot with `/newbot`
2. **Chat ID**: Message @userinfobot on Telegram to get your chat ID

## Usage

1. Open the web dashboard
2. Click "Start Monitoring" to begin hourly checks
3. Use "Check Now" for manual testing
4. View recent activity in the dashboard
5. Receive instant Telegram notifications when product is available

## Deployment

The application is ready for deployment on platforms like Replit, Heroku, or any Python hosting service.

## Technical Details

- **Framework**: Flask with SQLAlchemy
- **Scheduler**: APScheduler for background tasks
- **Web Scraping**: BeautifulSoup4 and Requests
- **Database**: SQLite (development) / PostgreSQL (production)
- **Notifications**: Telegram Bot API

## Project Structure

```
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── monitor.py          # Core monitoring logic
├── telegram_bot.py     # Telegram integration
├── models.py           # Database models
├── templates/          # HTML templates
│   ├── base.html
│   └── index.html
└── requirements.txt    # Python dependencies
```

## License

This project is for educational purposes.