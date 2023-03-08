import requests

import os

import sys

import time

import logging

import telegram

from http import HTTPStatus

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s, %(levelname)s, %(message)s',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def check_tokens():
    """Проверка доступности переменных окружения."""
    return (
        PRACTICUM_TOKEN is not None
        and TELEGRAM_TOKEN is not None
        and TELEGRAM_CHAT_ID is not None
    )


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(
            f'Ошибка при отправке сообщения из бота: {error}'
        )
    logging.debug('Сообщение успешно отправлено')


def get_api_answer(timestamp):
    """Запрос к эндпоинту API-сервиса."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except Exception as error:
        message = f'Проблема с запросом к эндпоинту API-сервиса: {error}'
        logging.error(message)
    if response.status_code != HTTPStatus.OK:
        message = f'Неверный статус-код: {response.status_code}'
        logging.error(message)
        raise Exception
    return response.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        message = 'Ответ API не является словарем'
        logging.error(message)
        raise TypeError
    if 'homeworks' not in response:
        message = 'В ответе API нет ключа homeworks'
        logging.error(message)
        raise KeyError
    if not isinstance(response['homeworks'], list):
        message = 'Ключ homeworks не является списком'
        logging.error(message)
        raise TypeError
    return response['homeworks'][0]


def parse_status(homework):
    """Извлечение статуса из информации о конкретной домашней работе."""
    try:
        verdict = HOMEWORK_VERDICTS[homework['status']]
    except KeyError as error:
        message = f'В домашке нет ключа status: {error}'
        logging.error(message)
    try:
        homework_name = homework['homework_name']
    except KeyError as error:
        message = f'В домашке нет ключа homework_name: {error}'
        logging.error(message)
    return (
        f'Изменился статус проверки работы "{homework_name}".'
        f'{verdict}'
    )


def main():
    """Основная логика работы бота."""
    try:
        if not check_tokens():
            raise Exception
    except Exception as error:
        message = f'Отсутствует переменная окружения: {error}'
        logging.critical(message)

    if not TELEGRAM_TOKEN:
        raise Exception
    else:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    current_status = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework['status'] != current_status:
                current_status = homework['status']
                message = parse_status(homework)
                send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
