# tgpush

A script that allows you to receive notifications from Telegram using ntfy.sh

# Why?

Almost all Telegram clients for Android use Google's Firebase Cloud Messaging (which is proprietary software) to send push notifications.  If you use a custom ROM without Google services, your notifications may arrive with a delay. Apparently, some clients run background services which keep connection to Telegram's server. But this approach brings an another issue. You may get an increased battery consumption. That's why I created this script. It receives new messages for your account and sends them to a specified ntfy topic. 

# Usage

1. Clone repo to some directory and cd to it

2. Open main.py and set configuration options to your preferences

3. Run 
   
   ```shell
   pip install -r requirements.txt
   python3 main.py
   ```

# 
