import psutil
import time
import json
import os
import yaml
import logging
from datetime import datetime


# Создание папок данных и логов
paths_to_create = [
    "logs",
    "data"
]

for path in paths_to_create:
    if path and not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Создана папка: {path}")
        except OSError as e:
            print(f"Ошибка создания папки {path}: {e}")
            exit(1)

# Проверка наличия config.yaml
if os.path.exists("config/config.yaml"):
    try:
        with open("config/config.yaml", "r", encoding="utf-8") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
    except:
        print("Ошибка чтения файла.")
else:
    print("Ошибка: config.yaml не найден!")
    exit(1)

# Настройка логов
logging.basicConfig(level=logging.INFO, filename=config["logs"],filemode="a", format="%(asctime)s %(levelname)s %(message)s")

monitor = {
    "TIMESTAMP": "0",
    "CPU": "0",
    "RAM": "0",
    "DISK": "0"
}

history = []


# Сбор метрик
def monitoring():
    psutil.cpu_percent()
    time.sleep(0.1)
    monitor["CPU"] = psutil.cpu_percent()
    monitor["RAM"] = psutil.virtual_memory().percent
    monitor["DISK"] = psutil.disk_usage('/').percent
    monitor["TIMESTAMP"] = datetime.now().isoformat()
    json_formatted_string = json.dumps(monitor, indent=4, sort_keys=True, ensure_ascii=False)
    print(json_formatted_string)


# Проверка наличия или создание monitoring.json
def check_exist_json():
    global history

    if os.path.exists(config["data"]): # Проверяем наличие monitoring.json
        try:
            with open(config["data"], "r", encoding="utf-8") as file: 
                history = json.load(file) # Загружаем в history прошлые логи
        except:
            logging.error("Ошибка чтения файла.")
    else:
        try:
            with open(config["data"], "w", encoding="utf-8") as file: # Создаем monitoring.json, если его нет
                file.write("[]")
        except:
            logging.error("Ошибка записи файла.")


TIME_INTERVAL = config["time_interval"]
MAX_FILE_SIZE = config["max_file_size"]

try:
    check_exist_json()

    while True:
        if os.path.getsize(config["data"]) >= MAX_FILE_SIZE:
            print(f"Превышен размер файла: {os.path.getsize(config["data"])}")
            os.rename(config["data"], f'data/monitoring-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json.old')
            check_exist_json()

        monitoring()
        history.append(monitor.copy())
        try:
            with open(config["data"], "w", encoding="utf-8") as file:
                json.dump(history, file, indent=4, sort_keys=True, ensure_ascii=False)
        except:
            logging.error("Ошибка записи файла.")
        time.sleep(TIME_INTERVAL)

except KeyboardInterrupt:
    logging.info("Программа успешно завершила выполнение.")
    print("Программа успешно завершила выполнение.")
    print(f"Всего сохранено записей: {len(history)}")
    print(f"Последняя запись: {history[-1]['TIMESTAMP'] if history else 'нет данных'}")