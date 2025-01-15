import pandas as pd

def analyze_trades_with_fvg(data, fvgs, initial_balance=100, stop_loss_tick=0.001, take_profit_tick=0.002):
    """
    Анализирует торговлю на основе FVG и возвращает статистику.
    :param data: DataFrame с данными свечей.
    :param fvgs: DataFrame с FVG.
    :param initial_balance: Начальный баланс.
    :param stop_loss_tick: Стоп-лосс в тиках от цены входа.
    :param take_profit_tick: Тейк-профит в тиках от цены входа.
    :return: Список сделок и статистика.
    """
    balance = initial_balance
    win_count = 0
    loss_count = 0
    trades = []

    risk_reward = round(take_profit_tick / stop_loss_tick, 2)  # Вычисление соотношения риска к прибыли

    for _, fvg in fvgs.iterrows():
        if fvg['End Time'] not in data.index:
            print(f"Skipping FVG with End Time {fvg['End Time']}: not in data index.")
            continue

        # Следующая свеча после FVG
        entry_idx = data.index.get_loc(fvg['End Time']) + 1
        if entry_idx >= len(data):
            print(f"Skipping FVG with End Time {fvg['End Time']}: no next candle available.")
            continue

        entry_time = data.index[entry_idx]
        entry_price = data.iloc[entry_idx]['Open']
        trade_type = 'short' if fvg['Start Price'] > fvg['End Price'] else 'long'
        take_profit = entry_price + take_profit_tick if trade_type == 'long' else entry_price - take_profit_tick
        stop_loss = entry_price - stop_loss_tick if trade_type == 'long' else entry_price + stop_loss_tick

        result = None
        closing_price = None

        # Итерируемся по свечам после входа, чтобы определить результат сделки
        for i in range(entry_idx, len(data)):
            high_price = data.iloc[i]['High']
            low_price = data.iloc[i]['Low']

            if trade_type == 'long':
                if high_price >= take_profit:
                    result = 'Win'
                    closing_price = take_profit
                    break
                elif low_price <= stop_loss:
                    result = 'Loss'
                    closing_price = stop_loss
                    break
            elif trade_type == 'short':
                if low_price <= take_profit:
                    result = 'Win'
                    closing_price = take_profit
                    break
                elif high_price >= stop_loss:
                    result = 'Loss'
                    closing_price = stop_loss
                    break

        if result is None:
            print(f"Trade for FVG ending at {fvg['End Time']} did not hit take profit or stop loss.")
            continue

        if result == 'Win':
            win_count += 1
            profit = abs(entry_price - closing_price) * 1000  # Перевод профита в пункты
            balance += profit
        else:
            loss_count += 1
            loss = abs(entry_price - closing_price) * 1000  # Перевод убытка в пункты
            balance -= loss

        trades.append({
            'Entry Time': entry_time,
            'Type': trade_type,
            'Entry Price': entry_price,
            'Take Profit': take_profit,
            'Stop Loss': stop_loss,
            'Closing Price': closing_price,
            'Result': result,
            'Profit/Loss': round(closing_price - entry_price, 4) if result == 'Win' else round(entry_price - closing_price, 4),
            'Balance': round(balance, 2),
            'Risk-Reward': risk_reward
        })

    total_trades = win_count + loss_count
    winrate = (win_count / total_trades) * 100 if total_trades > 0 else 0
    final_balance_percent = ((balance - initial_balance) / initial_balance) * 100

    trades_df = pd.DataFrame(trades)
    trades_df.to_csv('trade_results.csv', index=False)

    return trades, {
        'Total Trades': total_trades,
        'Winrate (%)': winrate,
        'Final Balance (%)': final_balance_percent,
        'Risk-Reward': risk_reward
    }
