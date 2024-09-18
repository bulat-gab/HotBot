#!/bin/bash

install_chromedriver() {
    echo "Installing ChromeDriver"
    sudo apt install -y unzip || true  # Ensure unzip is installed
    wget https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.137/linux64/chromedriver-linux64.zip
    unzip chromedriver-linux64.zip
    rm chromedriver-linux64.zip
    sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver
}


install_google_chrome() {
    echo "Installing Google Chrome"
    wget -O /tmp/chrome.deb https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_128.0.6613.119-1_amd64.deb
    sudo dpkg -i /tmp/chrome.deb
    sudo apt-get install -f -y  # Fix any dependency issues
    rm /tmp/chrome.deb
}


# install_google_chrome
# install_chromedriver

if ! command -v google-chrome > /dev/null; then
    install_google_chrome
else
    echo "Google Chrome is already installed."
fi


if ! command -v chromedriver > /dev/null; then
    install_chromedriver
else
    echo "ChromeDriver is already installed."
fi

echo ""
echo "Google Chrome version: $(google-chrome --version | grep -oP '(?<=Google Chrome\s)[\d.]+')"
echo "Chrome driver version: $(chromedriver --version | grep -oP '(?<=ChromeDriver\s)[\d.]+')"
echo ""