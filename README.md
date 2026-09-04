# Telegram Price Tracker Bot 🛒

A Python-based Telegram bot that monitors product prices on e-commerce platforms like Jumia and Noon, sending automated hourly alerts to users when prices change.

## Features
- **Add Products:** Users can send product URLs to be tracked.
- **View List:** Users can see all the products they are currently tracking.
- **Delete Products:** Users can easily remove items from their tracking list.
- **Hourly Notifications:** Automated background tasks check prices every hour and notify the user via Telegram if there is an update.

## Tech Stack
- **Python 3.x**
- **python-telegram-bot** (v20+) - For handling Telegram API interactions and commands.
- **APScheduler** - For running asynchronous background tasks and hourly price checks.
- **BeautifulSoup / Selenium** - For scraping product prices from e-commerce sites.
- **SQLite3** - For storing users and products data.

## Project Structure
The project is modularized for easy maintenance:
- `main.py`: Entry point, bot setup, and polling loop.
- `config.py`: Environment variables, Telegram token, and constants.
- `handlers.py`: Telegram command functions.
- `scraper.py`: Web scraping logic to extract prices from URLs.
- `jobs.py`: APScheduler tasks for background price checking.
