import pandas as pd


def detect_time_column(df):
    """
    Определяет столбец или индекс, содержащий временные данные.
    """
    # Проверяем, есть ли индекс с временными метками
    if isinstance(df.index, pd.DatetimeIndex):
        return "index"

    # Проверяем столбцы
    for col in df.columns:
        if 'time' in col.lower() or 'date' in col.lower():
            return col

    return None


def identify_fvgs(df):
    """
    Определяет FVG (Fair Value Gap) в предоставленных данных.
    """
    time_column = detect_time_column(df)

    if time_column == "index":
        df = df.reset_index()
        time_column = "Date"  # После сброса индекса столбец времени называется "Date"

    if not time_column:
        raise ValueError("The data does not contain a recognizable time column.")

    df.rename(columns={time_column: 'Open Time'}, inplace=True)

    # Переименовываем столбцы, чтобы соответствовать ожидаемым названиям
    df.rename(columns={
        'BidOpen': 'Open',
        'BidHigh': 'High',
        'BidLow': 'Low',
        'BidClose': 'Close'
    }, inplace=True)

    fvgs = []
    df = df.sort_values(by='Open Time').reset_index(drop=True)
    df['Volume Before'] = df['Volume'].shift(-1)
    df['Volume After'] = df['Volume'].shift(1)

    for i in range(2, len(df) - 2):
        two_bars_ago = df.iloc[i - 2]
        current_row = df.iloc[i]

        # Bullish FVG
        if current_row['Low'] > two_bars_ago['High']:
            fvgs.append({
                'Start Time': two_bars_ago['Open Time'],
                'End Time': current_row['Open Time'],
                'Start Price': two_bars_ago['High'],
                'End Price': current_row['Low'],
                'Type': 'Bullish FVG'
            })

        # Bearish FVG
        elif current_row['High'] < two_bars_ago['Low']:
            fvgs.append({
                'Start Time': two_bars_ago['Open Time'],
                'End Time': current_row['Open Time'],
                'Start Price': two_bars_ago['Low'],
                'End Price': current_row['High'],
                'Type': 'Bearish FVG'
            })

    return pd.DataFrame(fvgs)

