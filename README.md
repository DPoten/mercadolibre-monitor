# MercadoLibre Discount Monitor 🛒💸

This is a Flask-based web app that monitors MercadoLibre product URLs for discounts and sends alerts to a Discord webhook.

## Features

- Add/remove MercadoLibre URLs from a simple dashboard
- Tracks discounts in the background (every 1 hour)
- Sends updates to your Discord channel using a webhook

## Quick Start (Local)

```bash
git clone https://github.com/yourusername/mercadolibre-monitor.git
cd mercadolibre-monitor
pip install -r requirements.txt
python app.py
