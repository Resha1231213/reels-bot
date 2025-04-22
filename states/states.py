import requests
from bs4 import BeautifulSoup
import re

def parse_reel_metadata(url: str) -> dict:
    if 'tiktok.com' in url:
        return parse_tiktok(url)
    elif 'instagram.com' in url:
        return parse_instagram(url)
    elif 'youtube.com' in url or 'youtu.be' in url:
        return parse_youtube(url)
    else:
        return {"error": "Unsupported platform"}

def parse_tiktok(url: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text
        return {
            "platform": "TikTok",
            "title": title,
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}

def parse_instagram(url: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text
        return {
            "platform": "Instagram",
            "title": title,
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}

def parse_youtube(url: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text
        return {
            "platform": "YouTube",
            "title": title,
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}
