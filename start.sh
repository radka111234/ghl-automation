#!/usr/bin/env bash

# Install Google Chrome
apt-get update
apt-get install -y wget unzip curl gnupg
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get update
apt-get install -y google-chrome-stable

# Download matching ChromeDriver
CHROME_VERSION=$(google-chrome-stable --version | grep -oP '\d+\.\d+\.\d+')
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip" || true
unzip /tmp/chromedriver.zip -d /usr/local/bin || true
