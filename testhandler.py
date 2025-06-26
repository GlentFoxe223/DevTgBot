import requests
from bs4 import BeautifulSoup
from loguru import logger
import os


class ProxyHandler:
    def init(self):
        self.proxy_ip = os.getenv("PROXY_IP")
        self.proxy_port = os.getenv("PROXY_PORT")
        self.proxy_username = os.getenv("PROXY_USERNAME")
        self.proxy_password = os.getenv("PROXY_PASSWORD")

    def get_proxy(self):
        if self.proxy_ip and self.proxy_port:
            if self.proxy_username and self.proxy_password:
                return f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_ip}:{self.proxy_port}"
            else:
                return f"https://{self.proxy_ip}:{self.proxy_port}"
        else:
            return None


class ProxyRequest:
    def init(self):
        self.proxy_handler = ProxyHandler()

    def make_request(self, url):
        proxy_url = self.proxy_handler.get_proxy()
        if proxy_url:
            try:
                response = requests.get(url, proxies={"http": proxy_url, "https": proxy_url}, timeout=10)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error("Exception: {}", e)
                return None
        else:
            logger.error("No proxy available. Skipping request.")
            return None


class ArticleVideoExtractor:
    def init(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')

    def extract_videos(self):
        main_wrap_div = self.soup.find('div', class_='main-wrap')
        if main_wrap_div:
            videos = []

            # Extract videos from embedded <iframe> tags
            for iframe in main_wrap_div.find_all('iframe'):
                if 'src' in iframe.attrs and iframe['src'].startswith('https://'):
                    videos.append(iframe['src'])

            # Extract videos from <video> tags and their <source> tags
            for video_tag in self.soup.find_all('video'):
                sources = video_tag.find_all('source')
                for source in sources:
                    if 'src' in source.attrs:
                        videos.append(source['src'])

            return videos

        return []
def clean_article_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    unwanted_selectors = [
        "div.social", "div.subscribe", "div.comments", "div.account",
        "a[href*='facebook.com']", "a[href*='youtube.com']", "a[href*='x.com']",
        "a[href*='vk.com']", "a[href*='ok.ru']", "a[href*='instagram.com']",
        "a[href*='rss']", "a[href*='t.me']", "footer", ".b.opinion"
    ]

    for selector in unwanted_selectors:
        elements = soup.select(selector)
        for element in elements:
            element.decompose()

    unwanted_texts = [
        "PATREON Поддержите сайт  «Хартия-97»", "Написать комментарий",
        "Также следите за аккаунтами Charter97.org в социальных сетях",
        "Facebook", "YouTube", "X.com", "vkontakte", "ok.ru", "Instagram",
        "RSS", "Telegram"
    ]

    for text in unwanted_texts:
        elements = soup.find_all(string=lambda t: text in t)
        for element in elements:
            element.extract()

    # Replace HTML tags with Markdown equivalents
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        tag.string = f"*{tag.get_text()}*\n"

    article_text = ""
    for p in soup.find_all('p'):
        article_text += f"{p.get_text()}\n\n"

    images_and_videos = []
    base_url = "https://charter97.org"

    # Get all images directly in the article content
    for img in soup.select('article img'):
        if 'src' in img.attrs:
            img_src = img['src']
            if not img_src.startswith('http'):
                img_src = base_url + img_src
            images_and_videos.append(('photo', img_src))

    # Extract videos
    video_extractor = ArticleVideoExtractor(html)
    video_urls = video_extractor.extract_videos()

    return article_text.strip(), images_and_videos, video_urls
def parse_html(html):
    base_url = "https://charter97.org"
    soup = BeautifulSoup(html, 'html.parser')
    news_items = soup.find_all(class_='news news_latest')
    titles_links_images = []

    for item in news_items:
        li_elements = item.find_all('li')
        for li in li_elements:
            if 'google_ad' in li.get('class', []):
                continue

            a_tag = li.find('a')
            img_tag = li.find('div', class_='news__pic')

            if img_tag:
                img = img_tag.find('img')
                if img and 'src' in img.attrs:
                    img_classes = img.get('class', [])
                    if 'b' not in img_classes and 'opinion' not in img_classes:
                        img_src = base_url + img['src'] if not img['src'].startswith('http') else img['src']
                    else:
                        img_src = None
                        logger.debug(f"Excluded image with classes {img_classes}: {img['src']}")
                else:
                    img_src = None
            else:
                img_src = None

            time_tag = li.find('span', class_='news__time')
            if time_tag:
                time_tag.decompose()

            if a_tag:
                full_link = base_url + a_tag['href'] if not a_tag['href'].startswith('http') else a_tag['href']
                title = a_tag.get_text(strip=True)

                titles_links_images.append((title, full_link, img_src))

    return titles_links_images


def get_news():
    url = 'https://charter97.org/ru/news/p/1/'
    proxy_request = ProxyRequest()
    response = proxy_request.make_request(url)
    if response:
        return parse_html(response)
    else:
        logger.error("Failed to retrieve news.")
        return []


if __name__ == "__main__":
    news = get_news()
    for title, link, img_path in news:
        print(f"Title: {title}\nLink: {link}\nImage: {img_path}\n")

        # Extract and display article videos
        proxy_request = ProxyRequest()
        article_response = proxy_request.make_request(link)
        if article_response:
            article_text, media_urls, video_urls = clean_article_html(article_response)
            for video_url in video_urls:
                print(f"Video URL: {video_url}")
        else:
            print("Failed to retrieve article content.")
