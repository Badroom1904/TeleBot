from dotenv import dotenv_values

# Попробуйте этот способ
config = dotenv_values(".env")
print("Значения из dotenv_values:", config)

PRACTICUM_TOKEN = config.get('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = config.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = config.get('TELEGRAM_CHAT_ID')