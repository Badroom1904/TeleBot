"""Пользовательские исключения для бота."""


class APIRequestError(Exception):
    """Исключение для ошибок API запросов."""

    pass


class InvalidAPIResponseError(Exception):
    """Исключение для невалидного ответа API."""

    pass


class TelegramSendMessageError(Exception):
    """Исключение для ошибок отправки в Telegram."""

    pass
