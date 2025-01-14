import datetime
from forexconnect import ForexConnect
from analysis import analyze_and_visualize_candlesticks
from utils import session_status_changed
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env
load_dotenv()

def forex_trading_bot():
    try:
        with ForexConnect() as fx:
            # Данные для авторизации из .env
            user_id = os.getenv("USER_ID")
            password = os.getenv("PASSWORD")
            url = os.getenv("URL")
            connection = os.getenv("CONNECTION")

            # Авторизация
            fx.login(user_id, password, url, connection, session_status_callback=session_status_changed)
            print("Login successful")

            # Параметры анализа
            instrument = "EUR/USD"  # Валютная пара
            time_frame = "H4"       # Таймфрейм
            start_time = datetime.datetime.strptime("01.7.2023 00:00:00", "%d.%m.%Y %H:%M:%S")
            end_time = datetime.datetime.strptime("01.05.2024 12:00:00", "%d.%m.%Y %H:%M:%S")

            # Анализ графиков
            analyze_and_visualize_candlesticks(fx, instrument, time_frame, start_time, end_time)

            # Выход из системы
            fx.logout()
            print("Logged out successfully")

    except Exception as e:
        print("An error occurred: " + str(e))

if __name__ == "__main__":
    forex_trading_bot()
