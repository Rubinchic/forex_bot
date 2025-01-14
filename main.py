import datetime
import os
from forexconnect import ForexConnect
from utils import session_status_changed
from historical_data import fetch_historical_data
from visualization import analyze_and_visualize_candlesticks
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

def main():
    try:
        # Чтение конфигурации из .env
        user_id = os.getenv("USER_ID")
        password = os.getenv("PASSWORD")
        url = os.getenv("URL")
        connection = os.getenv("CONNECTION")

        if not all([user_id, password, url, connection]):
            raise ValueError("Some required environment variables are missing. Please check your .env file.")

        with ForexConnect() as fx:
            # Авторизация
            fx.login(user_id, password, url, connection, session_status_callback=session_status_changed)
            print("Login successful")

            # Настройки
            instrument = "EUR/USD"
            time_frame = "H4"
            start_time = datetime.datetime.strptime("07.01.2023 00:00:00", "%d.%m.%Y %H:%M:%S")
            end_time = datetime.datetime.strptime("05.01.2024 12:00:00", "%d.%m.%Y %H:%M:%S")

            # Получение исторических данных
            history = fetch_historical_data(fx, instrument, time_frame, start_time, end_time)

            # Анализ и визуализация
            analyze_and_visualize_candlesticks(history, instrument, time_frame)

            # Логаут
            fx.logout()
            print("Logged out successfully")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
