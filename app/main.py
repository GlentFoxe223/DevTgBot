import os
from dotenv import load_dotenv
import telebot
from telebot import types
import html as thtml

load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)
BOT_TOKEN = os.getenv("BOT_API1")

if not BOT_TOKEN:
    raise RuntimeError("Одна из переменных BOT_API не задана в .env")

bot = telebot.TeleBot(BOT_TOKEN)

from db.DBsearcher import DBsearcher
from handlers.WeatherHandler import WeatherHandler
from handlers.NewsHandler import NewsHandler
from handlers.IIHandler import IIHandler
from handlers.CurrencyHandler import CurrencyHandler
from utils.helpers import Cleaner
from utils.helpers import Photo
from utils.helpers import Player

class BotCore:
    def __init__(self):
        load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)
        
        self.db = DBsearcher('botdata.db')

        self.main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [
            types.KeyboardButton('Погода'),
            types.KeyboardButton('Конвертация валют'),
            types.KeyboardButton('Новости'),
            types.KeyboardButton('ИИ помощник'),
        ]
        self.main_kb.add(*buttons)

        self.remove_kb = types.ReplyKeyboardRemove()
        self.user_pages = {}

        self.register_handlers()

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

        self.user_data = {}
        

    def register_handlers(self):
        @bot.message_handler(commands=['start'])
        def cmd_start(message):
            user_id = message.from_user.id
            username = message.from_user.username
            self.db.add_user(user_id, username)
            bot.send_message(
                message.chat.id,
                "Привет! Выберите действие:",
                reply_markup=self.main_kb
            )

        @bot.message_handler(func=lambda m: m.text == 'Погода')
        def cmd_weather(message):
            msg = bot.send_message(
                message.chat.id,
                "Введите город:",
                reply_markup=self.remove_kb
            )
            bot.register_next_step_handler(msg, self.process_weather)

        @bot.message_handler(func=lambda m: m.text == 'Конвертация валют')
        def cmd_currency(message):
            bot.send_message(
                message.chat.id,
                'Введите валюту, которую вы будите переводить',
                reply_markup=self.remove_kb
            )
            bot.register_next_step_handler(message, self.process_currency_1)

        @bot.message_handler(func=lambda m: m.text == 'Новости')
        def cmd_news(message):
            user_id = message.from_user.id
            parser = NewsHandler()
            news = parser.get_news()
            if not news:
                bot.send_message(message.chat.id, "Не удалось получить новости.")
                return
            self.user_pages[user_id] = {
                'news': news,
                'page': 0
            }
            self.send_news_page(message.chat.id, user_id)

        @bot.message_handler(func=lambda m: m.text in ['Далее', 'Назад'])
        def news_navigation(message):
            user_id = message.from_user.id
            if user_id not in self.user_pages:
                bot.send_message(message.chat.id, "Сначала выберите раздел", reply_markup=self.main_kb)
                return
            if message.text == 'Далее':
                total_news = len(self.user_pages[user_id]['news'])
                current_page = self.user_pages[user_id]['page']
                if current_page < total_news - 1:
                    self.user_pages[user_id]['page'] += 1
                self.send_news_page(message.chat.id, user_id)
            elif message.text == 'Назад':
                self.user_pages.pop(user_id, None)
                bot.send_message(
                    message.chat.id,
                    "Возвращаемся в главное меню:",
                    reply_markup=self.main_kb
                )

        @bot.message_handler(func=lambda m: m.text == 'ИИ помощник')
        def cmd_ii(message):
            II_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons_for_II=[
            types.KeyboardButton('Назад'),
            # types.KeyboardButton('Очистить историю')
            ]
            II_kb.add(*buttons_for_II)
            bot.send_message(message.chat.id, 'Начните диалог с ИИ(обработка занимает время, поэтому после каждого запроса немного подождите, также ИИ не имеет памяти, но в будущем может быть добавлена)', reply_markup=II_kb)
            bot.register_next_step_handler(message, self.process_II)

        @bot.message_handler(func=lambda m: m.text == 'Назад')
        def cmd_back(message):
            bot.send_message(
                message.chat.id,
                "Возвращаемся в главное меню:",
                reply_markup=self.main_kb
            )

        @bot.callback_query_handler(func=lambda call: True)
        def handle_article_callback(call):
            news_url = call.data
            bot.answer_callback_query(call.id, "Открываю статью...")
            self.send_full_page(call.message.chat.id, news_url)

    def process_weather(self, message):
        city = message.text.strip()
        weather_text = WeatherHandler.get_weather(city)
        image = WeatherHandler.get_image(city)
        with open('./app/static/images/' + image, 'rb') as file:
            bot.send_photo(message.chat.id, file)
        bot.send_message(
            message.chat.id,
            weather_text,
            reply_markup=self.main_kb
        )

    def send_news_page(self, chat_id, user_id):
        page_data = self.user_pages[user_id]
        news = page_data['news']
        page = page_data['page']
        start = page * 10
        end = start + 10
        news_page = news[start:end]
        if not news_page:
            bot.send_message(chat_id, "Новостей больше нет.", reply_markup=self.main_kb)
            self.user_pages.pop(user_id, None)
            return
        total_news = len(news)
        for idx, item in enumerate(news_page, start=start + 1):
            text = f"{idx}. {item['title']}"
            photohandler=Photo()
            image=photohandler.picture_to_bytes(item['photo_link'])
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("Читать статью", callback_data=item['link'])
            markup.add(button)
            bot.send_photo(chat_id, image)
            bot.send_message(chat_id, text, reply_markup=markup)
        if end >= total_news:
            bot.send_message(chat_id, "Новостей на сегодня больше нет.", reply_markup=self.main_kb)
            self.user_pages.pop(user_id, None)
        else:
            news_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            news_kb.add(types.KeyboardButton('Далее'), types.KeyboardButton('Назад'))
            bot.send_message(chat_id, "Хотите ещё новостей?", reply_markup=news_kb)

    def send_full_page(self, chat_id, news_url):
        parser = NewsHandler()
        article = parser.get_deep_news(news_url)
        text = "\n\n".join(article.get('title', []))
        cleaner=Cleaner()
        text = cleaner.clean_words(text)
        text = thtml.unescape(text)
        bot.send_message(
            chat_id,
            text[:4093] + "..." if len(text) > 4096 else text,
            reply_markup=self.main_kb,
            parse_mode='HTML'
        )
        for img_url in article['images']:
            try:
                photohandler=Photo()
                image=photohandler.picture_to_bytes(img_url)
                bot.send_photo(chat_id, image)
            except:
                None
        for media_url in article['media']:
            player = Player(media_url)
            media = player.fetch_media()
            if media['type'] == 'photo':
                bot.send_photo(chat_id, photo=media['bytes'])
            elif media['type'] == 'video':
                bot.send_video(chat_id, video=media['bytes'])
            elif media['type'] == 'audio':
                bot.send_audio(chat_id, audio=media['bytes'])
            else:
                print('Ошибка медиа')
            
    def process_currency_1(self, message):
        currency = message.text.strip()
        if not currency:
            bot.send_message(message.chat.id, "Введите корректную валюту.")
            return
        self.user_data[message.chat.id] = {'from': currency}
        message = bot.send_message(message.chat.id, 'Введите валюту, в которую вы будете переводить:')
        bot.register_next_step_handler(message, self.process_currency_2)

    def process_currency_2(self, message):
        currency = message.text.strip()
        if not currency:
            bot.send_message(message.chat.id, "Введите корректную валюту.")
            return
        self.user_data[message.chat.id]['to'] = currency
        message = bot.send_message(message.chat.id, 'Введите количество первой валюты:')
        bot.register_next_step_handler(message, self.process_currency_3)

    def process_currency_3(self, message):
        amount = message.text.strip()
        from_currency = self.user_data[message.chat.id].get('from')
        to_currency = self.user_data[message.chat.id].get('to')

        currency_handler = CurrencyHandler()
        bot.send_message(message.chat.id, 'подождите, обработка информации')
        result = currency_handler.get_currency(from_currency, to_currency, amount)
        bot.send_message(message.chat.id, result, reply_markup=self.main_kb)
        self.user_data.pop(message.chat.id, None)

    def process_II(self, message):
        if message.text=='Назад':
            bot.send_message(
                message.chat.id,
                "Возвращаемся в главное меню:",
                reply_markup=self.main_kb
            )
        # elif message.text == 'Очистить историю':
        #     bot.send_message(
        #         message.chat.id,
        #         "Очищаем историю...",
        #     )
        #     self.answer.delete_history()
        #     bot.send_message(message.chat.id, 'Начните новую беседу с ИИ')
        #     bot.register_next_step_handler(message, self.process_II)
        else:
            if isinstance(message.text, str):
                answer=IIHandler()
                response = answer.answerII(message.text)
                bot.send_message(message.chat.id, response)
                bot.register_next_step_handler(message, self.process_II)
            else:
                bot.send_message(message.chat.id, 'Введите текст')
                bot.register_next_step_handler(message, self.process_II)

if __name__ == '__main__':
    bot_core = BotCore()
    bot.infinity_polling()