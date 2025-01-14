import pandas as pd
import mplfinance as mpf
from utils import time_frame_to_hours
import datetime

def analyze_and_visualize_candlesticks(fx, instrument, time_frame, start_time, end_time):
    try:
        # Получаем исторические данные
        history = fx.get_history(
            instrument, time_frame,
            start_time.replace(tzinfo=datetime.timezone.utc),
            end_time.replace(tzinfo=datetime.timezone.utc)
        )

        # Преобразуем данные в DataFrame
        data = pd.DataFrame(history)

        # Преобразуем столбец Date в формат datetime и устанавливаем как индекс
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)

        # Переименовываем колонки в формат, который ожидает mplfinance
        data.rename(columns={
            'BidOpen': 'Open',
            'BidHigh': 'High',
            'BidLow':  'Low',
            'BidClose': 'Close'
        }, inplace=True)

        # Анализ паттерна "бычье поглощение" (ордер блок)
        data['PrevOpen'] = data['Open'].shift(1)
        data['PrevClose'] = data['Close'].shift(1)
        data['BullishEngulfing'] = (
            (data['PrevClose'] < data['PrevOpen']) &  # Предыдущая свеча медвежья
            (data['Close'] > data['Open']) &          # Текущая свеча бычья
            (data['Open'] <= data['PrevClose']) &     # Тело текущей свечи начинается ниже или на уровне закрытия предыдущей
            (data['Close'] >= data['PrevOpen'])       # Тело текущей свечи закрывается выше или на уровне открытия предыдущей
        )

        # Создаем линии для ордер блоков
        alines = []
        line_offset = pd.Timedelta(hours=24)  # Смещение для длины линии вправо
        for date in data.index[data['BullishEngulfing']]:
            prev_close = data.loc[date - pd.Timedelta(hours=time_frame_to_hours(time_frame)), 'Close']
            if date + line_offset <= data.index[-1]:  # Проверка, что дата линии в пределах диапазона
                alines.append((
                    (date, prev_close),
                    (date + line_offset, prev_close)
                ))

        # Настраиваем цвета свечей
        mc = mpf.make_marketcolors(
            up='white', down='black', edge='black', wick='black', volume='inherit'
        )

        # Создаем собственный стиль
        my_style = mpf.make_mpf_style(
            base_mpf_style='yahoo', marketcolors=mc, rc={"axes.grid": False}
        )

        # Визуализация японских свечей с линиями ордер блоков
        mpf.plot(
            data,
            type='candle',
            style=my_style,
            title=f'Japanese Candlesticks for {instrument}',
            ylabel='Price',
            alines=dict(alines=alines, colors=['green'], linestyle='dashed'),
            figratio=(16, 9),
            figscale=1.2,
            volume=False
        )

    except Exception as e:
        print("Error during analysis or visualization: " + str(e))
