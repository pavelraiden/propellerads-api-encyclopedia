#!/usr/bin/env python3
"""
Конфігурація логування для PropellerAds API клієнтів
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


class PropellerAdsFormatter(logging.Formatter):
    """Кастомний форматер для PropellerAds логів"""
    
    def format(self, record):
        # Додаємо кольори для різних рівнів
        colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
        }
        reset = '\033[0m'
        
        # Форматуємо повідомлення
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level_color = colors.get(record.levelname, '')
        
        formatted = f"{level_color}[{timestamp}] {record.levelname:<8}{reset} "
        formatted += f"{record.name}: {record.getMessage()}"
        
        # Додаємо інформацію про виняток якщо є
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    console: bool = True,
    format_style: str = "detailed"
) -> logging.Logger:
    """
    Налаштування логування для PropellerAds API
    
    Args:
        level: Рівень логування (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Шлях до файлу логів (опціонально)
        console: Чи виводити логи в консоль
        format_style: Стиль форматування ('simple' або 'detailed')
    
    Returns:
        Налаштований logger
    """
    
    # Створюємо основний logger
    logger = logging.getLogger('propellerads')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Очищуємо існуючі handlers
    logger.handlers.clear()
    
    # Формати повідомлень
    if format_style == "simple":
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format_string)
    else:
        formatter = PropellerAdsFormatter()
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Створюємо директорію якщо не існує
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Отримання logger для модуля
    
    Args:
        name: Ім'я модуля (за замовчуванням використовується __name__)
    
    Returns:
        Logger для модуля
    """
    if name is None:
        name = 'propellerads'
    
    return logging.getLogger(f'propellerads.{name}')


# Налаштування за замовчуванням
default_logger = setup_logging(
    level="INFO",
    console=True,
    format_style="detailed"
)


class APIRequestLogger:
    """Логер для API запитів"""
    
    def __init__(self, logger_name: str = "api_requests"):
        self.logger = get_logger(logger_name)
    
    def log_request(self, method: str, endpoint: str, params: dict = None, **kwargs):
        """Логування API запиту"""
        params_str = f" params={params}" if params else ""
        self.logger.info(f"🔄 {method} {endpoint}{params_str}")
    
    def log_response(self, method: str, endpoint: str, status_code: int, 
                    response_time: float = None, **kwargs):
        """Логування API відповіді"""
        time_str = f" ({response_time:.3f}s)" if response_time else ""
        
        if status_code < 300:
            self.logger.info(f"✅ {method} {endpoint} -> {status_code}{time_str}")
        elif status_code < 500:
            self.logger.warning(f"⚠️ {method} {endpoint} -> {status_code}{time_str}")
        else:
            self.logger.error(f"❌ {method} {endpoint} -> {status_code}{time_str}")
    
    def log_error(self, method: str, endpoint: str, error: Exception, **kwargs):
        """Логування помилки API"""
        self.logger.error(f"💥 {method} {endpoint} -> {type(error).__name__}: {error}")
    
    def log_retry(self, method: str, endpoint: str, attempt: int, max_attempts: int):
        """Логування повторної спроби"""
        self.logger.warning(f"🔄 Retry {attempt}/{max_attempts}: {method} {endpoint}")


# Приклад використання
if __name__ == "__main__":
    # Тестування логування
    logger = setup_logging(level="DEBUG")
    api_logger = APIRequestLogger()
    
    logger.debug("Тестове debug повідомлення")
    logger.info("Тестове info повідомлення")
    logger.warning("Тестове warning повідомлення")
    logger.error("Тестове error повідомлення")
    
    # Тестування API логера
    api_logger.log_request("GET", "/adv/balance")
    api_logger.log_response("GET", "/adv/balance", 200, 0.345)
    api_logger.log_error("POST", "/adv/campaigns", Exception("Test error"))
    api_logger.log_retry("GET", "/adv/campaigns", 2, 3)
