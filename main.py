import os
import datetime
from forexconnect import ForexConnect
from dotenv import load_dotenv
from utils import session_status_changed
from historical_data import fetch_historical_data
from analysis import identify_fvgs
from visualisation import visualize_with_fvgs

# Загрузка переменных окружения из .env
load_dotenv()

def main():
    try:
        # Получение конфигурации из .env
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

            # Параметры для получения данных
            instrument = "EUR/USD"
            time_frame = "H1"
            start_time = datetime.datetime.strptime("01.01.2023 00:00:00", "%d.%m.%Y %H:%M:%S")
            end_time = datetime.datetime.strptime("01.02.2023 00:00:00", "%d.%m.%Y %H:%M:%S")

            # Получение исторических данных
            historical_data = fetch_historical_data(fx, instrument, time_frame, start_time, end_time)
            print("Historical data fetched successfully.")

            # Анализ FVG
            fvgs = identify_fvgs(historical_data)
            print(f"Found {len(fvgs)} FVG patterns.")
            print(fvgs.head())

            # Визуализация
            visualize_with_fvgs(historical_data, fvgs, instrument)
            print("Visualization completed.")

            # Логаут
            fx.logout()
            print("Logged out successfully")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
