import os
import datetime
import pandas as pd
from forexconnect import ForexConnect
from dotenv import load_dotenv
from utils import session_status_changed
from historical_data import fetch_historical_data
from analysis import identify_fvgs, identify_fractals, identify_bos_and_trend
from visualisation import visualize_with_fvgs_and_trades, visualize_with_fractals
from trading import analyze_trades_with_fvg

# Загрузка переменных окружения из .env
load_dotenv()

def main():
    try:
        # Загрузка параметров авторизации
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

            # Параметры анализа
            instrument = "EUR/USD"
            time_frame = "H4"
            start_time = "2023-02-02"
            end_time = "2023-03-31"

            start_time_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d")
            end_time_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d")

            # Получение исторических данных
            historical_data = fetch_historical_data(fx, instrument, time_frame, start_time_dt, end_time_dt)
            print("Historical data fetched successfully.")

            if historical_data.empty:
                print("Error: No historical data fetched.")
                return

            # Переименование столбцов
            historical_data.rename(columns={
                'BidOpen': 'Open',
                'BidHigh': 'High',
                'BidLow': 'Low',
                'BidClose': 'Close'
            }, inplace=True)

            # Анализ FVG
            fvgs = identify_fvgs(historical_data)
            print(f"Found {len(fvgs)} FVG patterns.")

            # Анализ фракталов
            fractals = identify_fractals(historical_data)
            print(f"Found {len(fractals)} fractals.")

            # Анализ линий BOS и тренда
            bos_lines, trend = identify_bos_and_trend(historical_data, fractals)
            print(f"Current Trend: {trend}")

            # Анализ сделок
            trades, trade_results = analyze_trades_with_fvg(
                historical_data, fvgs,
                time_frame=time_frame, start_time=start_time, end_time=end_time
            )
            print("Trade analysis completed.")
            print(f"Total Trades: {trade_results['Total Trades']}")
            print(f"Winrate: {trade_results['Winrate (%)']:.2f}%")
            print(f"Final Balance: {trade_results['Final Balance (%)']:.2f}%")
            print(f"Max Consecutive Losses: {trade_results['Max Consecutive Losses']}")

            # Визуализация
            #visualize_with_fvgs_and_trades(historical_data, fvgs, trades, instrument)
            visualize_with_fractals(historical_data, fractals, instrument)

            # Завершение сессии
            fx.logout()
            print("Logged out successfully")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
