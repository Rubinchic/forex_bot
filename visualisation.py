import mplfinance as mpf
import pandas as pd


def visualize_with_fvgs_and_trades(data, fvgs, trades, instrument):
    """
    Визуализирует данные свечей с отображением FVG и сделок на одном графике.
    """
    try:
        # Формирование линий FVG
        alines = []
        for _, row in fvgs.iterrows():
            alines.append(((row['Start Time'], row['Start Price']), (row['End Time'], row['Start Price'])))
            alines.append(((row['Start Time'], row['End Price']), (row['End Time'], row['End Price'])))

        # Формирование точек сделок
        addplots = []
        for trade in trades:
            entry_time = trade['Entry Time']
            entry_price = trade['Entry Price']
            take_profit = trade['Take Profit']
            stop_loss = trade['Stop Loss']
            result = trade['Result']

            color = 'green' if result == 'Win' else 'red'
            marker = '^' if trade['Type'] == 'long' else 'v'

            # Создание данных для точек
            entry_y = [entry_price if idx == entry_time else float('nan') for idx in data.index]
            tp_y = [take_profit if idx == entry_time else float('nan') for idx in data.index]
            sl_y = [stop_loss if idx == entry_time else float('nan') for idx in data.index]

            # Добавление точек
            addplots.append(mpf.make_addplot(entry_y, scatter=True, markersize=100, marker=marker, color=color))
            addplots.append(mpf.make_addplot(tp_y, scatter=True, markersize=50, marker='_', color='blue'))
            addplots.append(mpf.make_addplot(sl_y, scatter=True, markersize=50, marker='_', color='orange'))

        # Настройка графика
        mc = mpf.make_marketcolors(up='white', down='black', edge='black', wick='black', volume='inherit')
        style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc, rc={"axes.grid": False})

        # Построение графика
        mpf.plot(
            data,
            type='candle',
            style=style,
            title=f"{instrument} - FVG and Trades",
            ylabel='Price',
            figratio=(16, 9),
            figscale=1.2,
            volume=False,
            alines=dict(alines=alines, colors=['red', 'blue'], linestyle='dotted'),
            addplot=addplots
        )

        # Легенда
        print("\nExplanation of markers:")
        print("^ (green): Entry point of a winning trade")
        print("^ (red): Entry point of a losing trade")
        print("_ (blue): Take profit level")
        print("_ (orange): Stop loss level")

    except Exception as e:
        print(f"Error during visualization: {e}")

    pass


def visualize_with_fractals(data, fractals, instrument):
    """
    Визуализирует данные свечей с отображением фракталов и линий BOS.
    """
    try:
        from analysis import identify_bos_and_trend

        # Определяем линии BOS и тренд
        bos_lines, trend = identify_bos_and_trend(data, fractals)

        # Формирование точек для фракталов
        addplots = []
        for _, fractal in fractals.iterrows():
            time = fractal['Time']
            price = fractal['Price']
            marker = 'v' if fractal['Type'] == 'High' else '^'

            # Добавляем точки для каждого фрактала
            fractal_y = [price if idx == time else float('nan') for idx in data.index]
            addplots.append(
                mpf.make_addplot(fractal_y, scatter=True, markersize=50, marker=marker, color='black')
            )

        # Формирование линий BOS
        for bos_line in bos_lines:
            time = bos_line['Time']
            price = bos_line['Price']
            color = bos_line['Color']

            # Добавляем линии BOS
            bos_y = [price if idx >= time else float('nan') for idx in data.index]
            addplots.append(
                mpf.make_addplot(bos_y, color=color, linestyle='--')
            )

        # Настройка стиля графика
        mc = mpf.make_marketcolors(up='white', down='black', edge='black', wick='black', volume='inherit')
        style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc, rc={"axes.grid": False})

        # Построение графика
        mpf.plot(
            data,
            type='candle',
            style=style,
            title=f"{instrument} - Fractals and BOS",
            ylabel='Price',
            figratio=(16, 9),
            figscale=1.2,
            volume=False,
            addplot=addplots
        )

        # Легенда
        print("\nExplanation of markers:")
        print("v (black): Fractal High")
        print("^ (black): Fractal Low")
        print("-- (green): BOS Line from High Fractal")
        print("-- (red): BOS Line from Low Fractal")
        print(f"Current Trend: {trend}")

    except Exception as e:
        print(f"Error during visualization: {e}")