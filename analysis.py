import pandas as pd
from tqdm import tqdm

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
    Оптимизированный поиск FVG (Fair Value Gap) в предоставленных данных.
    """
    time_column = detect_time_column(df)

    if time_column == "index":
        df = df.reset_index()
        time_column = "Date"

    if not time_column:
        raise ValueError("The data does not contain a recognizable time column.")

    df.rename(columns={time_column: 'Open Time'}, inplace=True)

    # Переименование столбцов для согласования с ожидаемыми названиями
    df.rename(columns={
        'BidOpen': 'Open',
        'BidHigh': 'High',
        'BidLow': 'Low',
        'BidClose': 'Close'
    }, inplace=True)

    fvgs = []
    df = df.sort_values(by='Open Time').reset_index(drop=True)

    # Используем pandas для быстрого сдвига данных
    high_shift = df['High'].shift(2)
    low_shift = df['Low'].shift(2)
    time_shift = df['Open Time'].shift(2)

    # Вычисляем FVG с прогресс-баром
    for i in tqdm(range(2, len(df)), desc="Identifying FVG patterns"):
        current_row = df.iloc[i]

        # Bullish FVG
        if current_row['Low'] > high_shift[i]:
            fvgs.append({
                'Start Time': time_shift[i],
                'End Time': current_row['Open Time'],
                'Start Price': high_shift[i],
                'End Price': current_row['Low'],
                'Type': 'Bullish FVG'
            })

        # Bearish FVG
        elif current_row['High'] < low_shift[i]:
            fvgs.append({
                'Start Time': time_shift[i],
                'End Time': current_row['Open Time'],
                'Start Price': low_shift[i],
                'End Price': current_row['High'],
                'Type': 'Bearish FVG'
            })

    return pd.DataFrame(fvgs)
