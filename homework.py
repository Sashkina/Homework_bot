import requests
import sys
import time
import logging
import telegram
from http import HTTPStatus
from dotenv import dotenv_values

from exceptions import ApiStatusError, NoTokensError

config = dotenv_values('.env')


PRACTICUM_TOKEN = config.get('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = config.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = config.get('TELEGRAM_CHAT_ID')


RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    handlers=[
        logging.FileHandler('main.log', 'w'),
        logging.StreamHandler(sys.stdout)
    ],
    format='%(asctime)s, %(levelname)s, %(message)s',
    level=logging.DEBUG)


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения из бота: {error}')
    logging.debug('Сообщение успешно отправлено')


def get_api_answer(timestamp):
    """Запрос к эндпоинту API-сервиса."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.exceptions.RequestException as error:
        raise Exception(f'Ошибка запроса к эндпоинту API-сервиса: {error}')
    if response.status_code != HTTPStatus.OK:
        raise ApiStatusError
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
    return response['homeworks']


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
            raise NoTokensError
    except NoTokensError as error:
        message = f'Отсутствует переменная окружения: {error}'
        logging.critical(message)
        sys.exit('Отсутствует переменная окружения')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            timestamp = response.get('current_date', timestamp)
            if homework:
                message = parse_status(homework[0])
                send_message(bot, message)
        except ApiStatusError as error:
            message = f'Статус запроса к эндпоинту отличается от 200: {error}'
            logging.error(message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
