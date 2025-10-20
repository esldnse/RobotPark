# Инструкция по запуску

## RobotParkBackend
cd RobotParkBackend
python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

### Применение миграций (если нужно)
flask db upgrade 

python run.py

## RobotParkClient
cd RobotParkClient

dotnet run
