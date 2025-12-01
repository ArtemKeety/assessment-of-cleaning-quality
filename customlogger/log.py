import logging

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m', 'INFO': '\033[92m', 'WARNING': '\033[93m',
        'ERROR': '\033[91m', 'CRITICAL': '\033[95m'
    }

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, '')}%(asctime)s - %(levelname)s - %(message)s\033[0m"
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")  # Формат даты
        return formatter.format(record)


# Инициализация логгера
logger = logging.getLogger()

# Устанавливаем уровень логирования
logger.setLevel(logging.INFO)  # Устанавливаем уровень DEBUG для отображения всех сообщений

# Удаляем старые обработчики
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Создаём новый обработчик для вывода в консоль
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # Устанавливаем уровень для обработчика

# Устанавливаем цветной форматтер
ch.setFormatter(ColoredFormatter())

# Добавляем обработчик в логгер
logger.addHandler(ch)

def FabricLogger(code:int):
    match code//100:
        case 5:
            return logger.error
        case 4:
            return logger.warning
        case 3:
            return logger.warning
        case 2:
            return logger.info
        case _:
            return logger.debug


if __name__ == '__main__':
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
