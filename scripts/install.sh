#!/bin/bash
set -e

# Проверка прав
if [ "$EUID" != 0 ]; then
    echo "Недостаточно прав."
    exit 1
fi

# Создаем пользователя и папку
id my-monitoring &>/dev/null || useradd my-monitoring -r -s /usr/sbin/nologin
mkdir -p /opt/monitoring/
chown -R my-monitoring:my-monitoring /opt/monitoring/
chmod 750 /opt/monitoring/

# Копируем папки и requirements
cp -r ../src /opt/monitoring/
cp -r ../config /opt/monitoring/
cp -r ../requirements.txt /opt/monitoring/
cp ../systemd/monitoring.service /etc/systemd/system/
cp -r ../scripts /opt/monitoring/
cd /opt/monitoring/ 

# Устанавливаем зависимости
python3 -m venv venv # Выполняется от root так как скрипт запускает root 
chown -R my-monitoring:my-monitoring venv # Меняем владельца для папки venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Настройка systemd
sudo systemctl daemon-reload
sudo systemctl enable monitoring
sudo systemctl start monitoring
