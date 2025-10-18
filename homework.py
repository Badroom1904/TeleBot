
from dotenv import load_dotenv
import logging, sys, time, os, requests, pprint
from telebot import TeleBot


load_dotenv('.env')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


PRACTICUM_TOKEN = os.getenv('yaTOKEN')
TELEGRAM_TOKEN = os.getenv('tgbTOKEN')
TELEGRAM_CHAT_ID = os.getenv('idTOKEN')


RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN, 
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    
    missing_tokens = []
    
    for token_name, token_value in tokens.items():
        if not token_value:
            logging.critical(f'Отсутствует обязательная переменная окружения: {token_name}')
            missing_tokens.append(token_name)
    
    if missing_tokens:
        return False
    else:
        logging.debug('Все токены доступны')
        return True
    


def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено в Telegram')
    except TeleBot.apihelper.ApiException as error:
       logging.error(f'Ошибка отправки в Telegram: {error}')
       


def get_api_answer(timestamp):
    """Делает запрос к API Практикума."""
    try:
        params = {'from_date': timestamp}
        
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            logging.error(f'Эндпоинт {ENDPOINT} недоступен. Код ответа: {response.status_code}')
            raise Exception(f'API недоступен. Код: {response.status_code}')
        return response.json()
    except requests.RequestException as error:
        logging.error(f'Ошибка при запросе к API:{error}')
                          


def check_response(response):
    """Проверяет ответ API на соответствие документации."""

    if not isinstance(response, dict):
        logging.error('Ответ API не словарь')
        raise TypeError('Ответ API не является словарем')
    
    if 'homeworks' not in response:
        logging.error('В ответе нет ключа homeworks')
        raise KeyError('В ответе API отсутствует ключ "homeworks"')
    
    if not isinstance(response['homeworks'], list):
        logging.error('Homeworks не список')
        raise TypeError('Ключ "homeworks" не является списком')
    


def parse_status(homework):
    if 'homework_name' not in homework:
        logging.error('В домашней работе нет названия')
        raise Exception(f'Отсутствует ключ homework_name в домашней работе')
    if 'status' not in homework:
        logging.error('В домашней работе нет статуса')
        raise Exception(f'Отсутствует ключ status в домашней работе')
    homework_name = homework['homework_name']
    status = homework['status']
    
    if status not in HOMEWORK_VERDICTS:
        logging.error(f'Неизвестный статус работы: {status}')
        raise Exception(f'Неизвестный статус домашней работы: {status}')
    verdict = HOMEWORK_VERDICTS[status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if check_tokens() == False:
        logging.critical('Отсутствуют обязательные переменные окружения')
        raise SystemExit('Программа принудительно остановлена')
        
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_error = None
    logging.info('Бот запущен')
    
    while True:
        try:
            response = get_api_answer(timestamp)
            
            check_response(response)
            
            homeworks = response['homeworks']
            

            if homeworks:
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)
                    logging.info(f'Отправлено сообщение: {message}')
            else:
                logging.debug('Нет новых статусов')
            
        
            timestamp = response.get('current_date', timestamp)
            
            
        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'
            logging.error(error_message)
            
            if str(error) != last_error:
                try:
                    send_message(bot, error_message)
                    last_error = str(error)
                except Exception as e:
                    logging.error(f'Не удалось отправить сообщение об ошибке: {e}')
        
        time.sleep(RETRY_PERIOD)

if __name__ == '__main__':
    main()
