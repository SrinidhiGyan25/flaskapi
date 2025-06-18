#!/usr/bin/env bash
set -e

echo "🔧 Installing system dependencies..."

# Update package lists
apt-get update

# Install essential packages
apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxrandr2 \
    libxss1 \
    libxtst6

echo "🌐 Installing Google Chrome..."

# Add Google Chrome repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

# Install Chrome
apt-get update
apt-get install -y google-chrome-stable

echo "🚗 Installing ChromeDriver..."

# Get latest ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

# Download and install ChromeDriver
wget -O /tmp/chromedriver.zip "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Verify installations
echo "✅ Chrome version:"
google-chrome --version

echo "✅ ChromeDriver version:"
chromedriver --version

echo "🐍 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "🎉 Build completed successfully!"