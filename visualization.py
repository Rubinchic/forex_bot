import pandas as pd
import mplfinance as mpf


def analyze_and_visualize_candlesticks(data, instrument, time_frame):
    """
    Анализ и визуализация японских свечей с учетом ордер блоков.
    """
    try:
        # Переименование столбцов для mplfinance
        data.rename(columns={
            'BidOpen': 'Open',
            'BidHigh': 'High',
            'BidLow':  'Low',
            'BidClose': 'Close'
        }, inplace=True)

        # Проверяем, что данные не пустые
        if data.empty:
            raise ValueError("No data available for visualization.")

        # Настраиваем цвета свечей
        mc = mpf.make_marketcolors(up='white', down='black', edge='black', wick='black', volume='inherit')

        # Создаем стиль графика
        style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc, rc={"axes.grid": False})

        # Построение графика
        mpf.plot(
            data,
            type='candle',
            style=style,
            title=f'{instrument} - {time_frame} Chart',
            ylabel='Price',
            figratio=(16, 9),
            figscale=1.2
        )

    except Exception as e:
        raise RuntimeError(f"Error during analysis or visualization: {e}")
