import pandas as pd
import datetime
from forexconnect import ForexConnect


def fetch_historical_data(fx: ForexConnect, instrument: str, time_frame: str, start_time: datetime.datetime, end_time: datetime.datetime):
    """
    Получает исторические данные для указанного инструмента и временного интервала.
    """
    try:
        # Получение исторических данных с помощью ForexConnect
        history = fx.get_history(
            instrument, time_frame,
            start_time.replace(tzinfo=datetime.timezone.utc),
            end_time.replace(tzinfo=datetime.timezone.utc)
        )

        # Форматирование данных в DataFrame
        data = [
            {
                "Date": pd.to_datetime(str(row['Date'])),
                "BidOpen": row['BidOpen'],
                "BidHigh": row['BidHigh'],
                "BidLow": row['BidLow'],
                "BidClose": row['BidClose'],
                "Volume": row['Volume']
            }
            for row in history
        ]

        df = pd.DataFrame(data)
        df.set_index("Date", inplace=True)

        # Предварительная фильтрация данных
        if len(df) == 0:
            raise ValueError("No data fetched for the given parameters.")
        return df

    except Exception as e:
        raise RuntimeError(f"Failed to fetch historical data: {e}")
