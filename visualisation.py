import mplfinance as mpf
from analysis import detect_time_column


def visualize_with_fvgs(data, fvgs, instrument):
    """
    Визуализирует данные свечей с отображением FVG.
    """
    try:
        time_column = detect_time_column(data)

        if time_column == "index":
            data = data.reset_index()
            time_column = "Date"  # После сброса индекса столбец времени называется "Date"

        if not time_column:
            raise ValueError("The data does not contain a recognizable time column.")

        data.rename(columns={time_column: 'Open Time'}, inplace=True)

        # Подготовка данных для mplfinance
        data.rename(columns={
            'BidOpen': 'Open',
            'BidHigh': 'High',
            'BidLow': 'Low',
            'BidClose': 'Close'
        }, inplace=True)
        data.set_index('Open Time', inplace=True)

        # Подготовка FVG линий
        alines = []
        for _, row in fvgs.iterrows():
            alines.append((
                (row['Start Time'], row['Start Price']),
                (row['End Time'], row['Start Price'])
            ))

        # Настройка стиля графика
        mc = mpf.make_marketcolors(up='white', down='black', edge='black', wick='black', volume='inherit')
        style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc, rc={"axes.grid": False})

        # Построение графика с FVG линиями
        mpf.plot(
            data,
            type='candle',
            style=style,
            title=f'{instrument} with FVG Patterns',
            ylabel='Price',
            alines=dict(alines=alines, colors=['red'], linestyle='dotted'),
            figratio=(16, 9),
            figscale=1.2,
            volume=False
        )

    except Exception as e:
        print(f"Error during visualization: {e}")
