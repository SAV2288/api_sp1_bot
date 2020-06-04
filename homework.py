import os
import time

from dotenv import load_dotenv
import requests
import telegram


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# proxy для отправки сообщений
# proxy = telegram.utils.request.Request(proxy_url='socks5://5.133.202.167:19619')
# telegram bot
bot = telegram.Bot(
    token=TELEGRAM_TOKEN,
    # request=proxy
    )


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    data = {'from_date':current_timestamp}
    homework_statuses = requests.get(
        'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
        params=data,
        headers=headers,
    )
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp
    bot.send_message(chat_id=CHAT_ID, text='Мониторинг статуса проверки домашнего задания активирован')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(60*20)  # опрашивать раз в двадцать минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
