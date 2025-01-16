import pandas as pd
from tqdm import tqdm
import datetime
from forexconnect import ForexConnect


def fetch_historical_data(fx: ForexConnect, instrument: str, time_frame: str, start_time: datetime.datetime, end_time: datetime.datetime):
    """
    Оптимизированное получение исторических данных с прогресс-баром.
    """
    try:
        # Получение исторических данных с использованием ForexConnect
        history = fx.get_history(
            instrument, time_frame,
            start_time.replace(tzinfo=datetime.timezone.utc),
            end_time.replace(tzinfo=datetime.timezone.utc)
        )

        # Инициализация DataFrame для прямого добавления данных
        data = pd.DataFrame(
            [{
                "Date": pd.to_datetime(str(row['Date'])),
                "BidOpen": row['BidOpen'],
                "BidHigh": row['BidHigh'],
                "BidLow": row['BidLow'],
                "BidClose": row['BidClose'],
                "Volume": row['Volume']
            } for row in tqdm(history, desc="Processing historical data")]
        )

        # Установка индекса
        data.set_index("Date", inplace=True)

        # Проверка на наличие данных
        if data.empty:
            raise ValueError("No data fetched for the given parameters.")
        return data

    except Exception as e:
        raise RuntimeError(f"Failed to fetch historical data: {e}")
