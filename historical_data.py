import datetime
import pandas as pd
from forexconnect import ForexConnect


def fetch_historical_data(fx: ForexConnect, instrument: str, time_frame: str, start_time: datetime.datetime, end_time: datetime.datetime):
    """
    Получить исторические данные для указанного инструмента и временного интервала.
    """
    try:
        history = fx.get_history(
            instrument, time_frame,
            start_time.replace(tzinfo=datetime.timezone.utc),
            end_time.replace(tzinfo=datetime.timezone.utc)
        )

        # Преобразование в DataFrame
        data = pd.DataFrame(history)
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)
        return data

    except Exception as e:
        raise RuntimeError(f"Failed to fetch historical data: {e}")
