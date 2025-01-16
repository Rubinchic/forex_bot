import os
import datetime
import pandas as pd
from forexconnect import ForexConnect
from dotenv import load_dotenv
from utils import session_status_changed
from historical_data import fetch_historical_data
from analysis import identify_fvgs
from visualisation import visualize_with_fvgs_and_trades
from trading import analyze_trades_with_fvg

# Загрузка переменных окружения из .env
load_dotenv()


def main():
    try:
        user_id = os.getenv("USER_ID")
        password = os.getenv("PASSWORD")
        url = os.getenv("URL")
        connection = os.getenv("CONNECTION")

        if not all([user_id, password, url, connection]):
            raise ValueError("Some required environment variables are missing. Please check your .env file.")

        with ForexConnect() as fx:
            fx.login(user_id, password, url, connection, session_status_callback=session_status_changed)
            print("Login successful")

            instrument = "EUR/USD"
            time_frame = ["D1"]
            start_time = datetime.datetime.strptime("01.01.2020 00:00:00", "%d.%m.%Y %H:%M:%S")
            end_time = datetime.datetime.strptime("01.01.2025 00:00:00", "%d.%m.%Y %H:%M:%S")

            # Получение исторических данных
            for i in time_frame:
                historical_data = fetch_historical_data(fx, instrument, i, start_time, end_time)
                print("Historical data fetched successfully.")

                # Переименование столбцов
                historical_data.rename(columns={
                    'BidOpen': 'Open',
                    'BidHigh': 'High',
                    'BidLow': 'Low',
                    'BidClose': 'Close'
                }, inplace=True)

                # Анализ FVG
                fvgs = identify_fvgs(historical_data)
                print(f"\n\nFor time frame: {i}\n")
                print(f"Found {len(fvgs)} FVG patterns.")

                # Анализ сделок
                trades, trade_results = analyze_trades_with_fvg(historical_data, fvgs)
                print("Trade analysis completed.")
                print(f"Total Trades: {trade_results['Total Trades']}")
                print(f"Winrate: {trade_results['Winrate (%)']:.2f}%")
                print(f"Final Balance: {trade_results['Final Balance (%)']:.2f}%")

            # Визуализация FVG и сделок
           # visualize_with_fvgs_and_trades(historical_data, fvgs, trades, instrument)

            fx.logout()
            print("Logged out successfully")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
