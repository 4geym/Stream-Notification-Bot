# Twitch to Discord Notifier Bot
A Python-based bot that checks whether a Twitch stream is live and sends an automated message to a specified Discord channel. Runs as a systemd service on Ubuntu.

## Project Structure
├── bot.py<br>
├── .env<br>
└── README.md

## Tech Stack
- Python 3.10  
- Twitch API  
- Discord API  
- Ubuntu  
- systemd

---

## Run as a systemd service (Ubuntu)

Create a service file `twitch_bot.service`:
```ini
[Unit]
Description=Twitch Discord Bot
After=network.target

[Service]
User=server
WorkingDirectory=/home/server/Desktop/twitch_bot
ExecStart=/home/server/Desktop/twitch_bot/venv/bin/python /home/server/Desktop/twitch_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
sudo systemctl daemon-reload<br>
sudo systemctl start twitch_bot<br>
sudo systemctl status twitch_bot<br><br>
Logs:<br>
sudo journalctl -u twitch-bot -f<br>
sudo journalctl -u twitch-bot --since today

## Result
Once running, the bot will automatically check if a Twitch stream is live and notify a Discord channel whenever the stream starts.
