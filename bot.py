import asyncio
import io
import base64
import requests
import json

from telegram.ext import *
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import AuthenticationException



TOKEN = '99999999391:AAFgPAAATbCsYqQk_-kCqC2UWUcp38hhKAo'
BACKEND_URL = 'https://api.searchbooster.net/api/142a5f0d-0000-0000-0000-ba3fe46df1dd/search'


# BACKEND_URL="http://127.0.0.1:15999"
async def start(update, context):
    await update.message.reply_text('Привет! Пришли мне изображение, чтобы я нашел для тебя похожие товары.')

async def handle_image(update,context):
    print("Received image")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo['file_id'])
#    await file.download_to_drive('image.jpg')
    image_buffer = io.BytesIO()
    await file.download_to_memory(image_buffer);
    image_buffer.seek(0);
    image_data = image_buffer.read()
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    headers = {
            'accept': '*/*',
            'accept-language': 'ru,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'text/plain;charset=UTF-8',
            'dnt': '1',
            'origin': 'https://admin.searchbooster.io',
            'pragma': 'no-cache',
            'referer': 'https://admin.searchbooster.io/',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        }
    data = {
            'image': f'data:image/jpeg;base64,{encoded_image}'
        }

    response = requests.post(BACKEND_URL, headers=headers, json=data)

    if response.status_code == 200:
        data = json.loads(response.text)
        if data.get('offers'):
            # Отправляем результат в чат
            for offer in data['offers']:
                message = f"<b>{offer['name']}</b>\nЦена: {offer['price']} {offer['currency']}\n<a href='{offer['url']}'>Подробнее</a>"
                await context.bot.send_photo(chat_id=update.message.chat_id, photo=offer['pictures'][0], caption=message,
                                       parse_mode='HTML')
        else:
            print(response)
            await update.message.reply_text('К сожалению, товары не найдены.')
    else:
        print(response)
        await update.message.reply_text('Ошибка при обработке изображения. Пожалуйста, попробуйте еще раз.')

# msg = 'Starting a bot'; print(msg); data = { "text": msg }; es.index(index='searchbooster_telegram', doc_type='info', body=data)

async def start_commmand(update, context):
    await update.message.reply_text('Привет! Я бот концепт... отправь мне фотографию или изображение вещи, а я попробую предложить тебе чтото из нашего ассортимента ;)')

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()

    # Commands
    application.add_handler(CommandHandler('start', start_commmand))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    # Run bot
    application.run_polling(1.0)