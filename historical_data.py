import pandas as pd
import datetime
from forexconnect import fxcorepy, ForexConnect


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
        data = []
        for row in history:
            data.append({
                "Date": pd.to_datetime(str(row['Date'])),
                "BidOpen": row['BidOpen'],
                "BidHigh": row['BidHigh'],
                "BidLow": row['BidLow'],
                "BidClose": row['BidClose'],
                "Volume": row['Volume']
            })

        df = pd.DataFrame(data)
        df.set_index("Date", inplace=True)
        return df

    except Exception as e:
        raise RuntimeError(f"Failed to fetch historical data: {e}")
