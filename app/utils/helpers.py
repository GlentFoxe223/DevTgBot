import re
from io import BytesIO
import requests
from dotenv import load_dotenv
import os

class Photo:
    def __init__(self):
        load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)

        proxy_address = os.getenv('proxy_address')
        proxy_username = os.getenv('proxy_username')
        proxy_password = os.getenv('proxy_password')

        self.proxies = {
            "http": f"http://{proxy_username}:{proxy_password}@{proxy_address}",
            "https": f"http://{proxy_username}:{proxy_password}@{proxy_address}"
        }

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def picture_to_bytes(self, img_url):
        try:
            img_resp = requests.get(img_url, headers=self.headers, proxies=self.proxies, timeout=30, verify=False)
            if img_resp.ok:
                img=BytesIO(img_resp.content)
                return img
        except Exception as e:
            print(f"[Ошибка изображения]: {e}")


class Cleaner:
    def clean_words(self, page):
        load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)

        bad_url1 = os.getenv('bad_url1')
        bad_url2 = os.getenv('bad_url2')
        bad_url3 = os.getenv('bad_url3')
        bad_word1 = os.getenv('bad_word1')
        bad_word2 = os.getenv('bad_word2')
        bad_word3 = os.getenv('bad_word3')
        bad_word4 = os.getenv('bad_word4')
        bad_words = [bad_url1, bad_url2, bad_url3, bad_word1, bad_word2, bad_word3, bad_word4]

        for word in bad_words:
            word_pattern = r'\b(?:' + '|'.join(re.escape(word)) + r')\b'
            page = re.sub(word_pattern, '', page, flags=re.IGNORECASE)
        url_patterns = [
            r'https?://(?:www\.)?[^ ]*pic\.twitter\.com[^ ]*',
            r'https?://(?:www\.)?[^ ]*\.org[^ ]*',
            r'https?://(?:www\.)?[^ ]*\.ru[^ ]*',
            r'https?://(?:www\.)?[^ ]*\.com[^ ]*',
            r'https?://(?:www\.)?[^ ]*\.net[^ ]*',
            r'https?://(?:www\.)?[^ ]*\.info[^ ]*',
            r'https?://(?:www\.)?[^ ]*\.xyz[^ ]*',
            r'https?://(?:www\.)?[^ ]*t\.me[^ ]*',
            r'https?://(?:www\.)?[^ ]*youtu[^ ]*',
            r'https?://(?:www\.)?[^ ]*facebook\.com[^ ]*',
            r'https?://(?:www\.)?[^ ]*vk\.com[^ ]*',
            r'https?://(?:www\.)?[^ ]*instagram\.com[^ ]*',
            r'[^ ]*pic\.twitter\.com[^ ]*',
            r'[^ ]*\.org[^ ]*',
            r'[^ ]*\.ru[^ ]*',
            r'[^ ]*\.com[^ ]*',
            r'[^ ]*\.net[^ ]*',
            r'[^ ]*\.info[^ ]*',
            r'[^ ]*\.xyz[^ ]*',
            r'[^ ]*t\.me[^ ]*',
            r'[^ ]*youtu[^ ]*',
            r'[^ ]*facebook\.com[^ ]*',
            r'[^ ]*vk\.com[^ ]*',
            r'[^ ]*instagram\.com[^ ]*'
        ]

        for pattern in url_patterns:
            page = re.sub(pattern, '', page, flags=re.IGNORECASE)
        page = re.sub(r'[@#]\w+', '', page)
        clean_text = re.sub(r'\s+', ' ', page).strip()
        return clean_text
    
class Player:
    def __init__(self, media_url):
        load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)

        self.media_url = media_url
        self.proxy_address = os.getenv('proxy_address')
        self.proxy_username = os.getenv('proxy_username')
        self.proxy_password = os.getenv('proxy_password')

        self.proxies = {
            "http": f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_address}",
            "https": f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_address}"
        }

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_media(self):
        try:
            response = requests.get(self.media_url, headers=self.headers, proxies=self.proxies, timeout=15, verify=False)
            if response.status_code == 200:
                ext = self.get_extension(self.media_url)
                media_type = self.get_media_type(ext)
                data = BytesIO(response.content)
                if media_type:
                    return {'bytes':data, 'type': media_type}
                else:
                    print(f"Неизвестный формат: {ext} — URL: {self.media_url}")
            else:
                print(f"Не удалось загрузить медиа: статус {response.status_code}")
        except Exception as e:
            print(f"Ошибка загрузки медиа: {e}")
        return None

    def get_extension(self, url):
        basename = os.path.basename(url)
        _, ext = os.path.splitext(basename)
        return ext.lower()

    def get_media_type(self, ext):
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'photo'
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            return 'video'
        elif ext in ['.mp3', '.wav', '.ogg']:
            return 'audio'
        return None