class ApiStatusError(Exception):
    """Статус запроса к эндпоинту отличается от 200."""


class NoTokensError(Exception):
    """Нет необходимого токена."""
