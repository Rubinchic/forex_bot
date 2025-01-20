import pandas as pd

def detect_time_column(df):
    """
    Определяет столбец или индекс, содержащий временные данные.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        return "index"
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
        time_column = "Date"

    if not time_column:
        raise ValueError("The data does not contain a recognizable time column.")

    df.rename(columns={time_column: 'Open Time'}, inplace=True)
    df.rename(columns={
        'BidOpen': 'Open',
        'BidHigh': 'High',
        'BidLow': 'Low',
        'BidClose': 'Close'
    }, inplace=True)

    fvgs = []
    df = df.sort_values(by='Open Time').reset_index(drop=True)

    high_shift = df['High'].shift(2)
    low_shift = df['Low'].shift(2)
    time_shift = df['Open Time'].shift(2)

    for i in range(2, len(df)):
        current_row = df.iloc[i]
        if current_row['Low'] > high_shift[i]:
            fvgs.append({
                'Start Time': time_shift[i],
                'End Time': current_row['Open Time'],
                'Start Price': high_shift[i],
                'End Price': current_row['Low'],
                'Type': 'Bullish FVG'
            })
        elif current_row['High'] < low_shift[i]:
            fvgs.append({
                'Start Time': time_shift[i],
                'End Time': current_row['Open Time'],
                'Start Price': low_shift[i],
                'End Price': current_row['High'],
                'Type': 'Bearish FVG'
            })

    return pd.DataFrame(fvgs)

def identify_fractals(data):
    """
    Идентифицирует фракталы (Fractal High и Fractal Low) в данных свечей с учетом 3 свечей.
    """
    fractals = []
    for i in range(1, len(data) - 1):
        curr = data.iloc[i]
        prev = data.iloc[i - 1]
        next_ = data.iloc[i + 1]

        # Проверка на Fractal High
        if curr['High'] > prev['High'] and curr['High'] > next_['High']:
            fractals.append({'Time': curr.name, 'Type': 'High', 'Price': curr['High'] + 0.0005})

        # Проверка на Fractal Low
        if curr['Low'] < prev['Low'] and curr['Low'] < next_['Low']:
            fractals.append({'Time': curr.name, 'Type': 'Low', 'Price': curr['Low'] - 0.0005})

    return pd.DataFrame(fractals)
