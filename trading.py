import pandas as pd
from tqdm import tqdm


def analyze_trades_with_fvg(data, fvgs, initial_balance=100, stop_loss_tick=0.001, take_profit_tick=0.003):
    """
    Оптимизированный анализ торговли с прогресс-баром.
    :param data: DataFrame с данными свечей.
    :param fvgs: DataFrame с FVG.
    :param initial_balance: Начальный баланс.
    :param stop_loss_tick: Стоп-лосс в тиках от цены входа.
    :param take_profit_tick: Тейк-профит в тиках от цены входа.
    :return: Список сделок и статистика.
    """
    balance = initial_balance
    trades = []
    win_count = 0
    loss_count = 0

    risk_reward = round(take_profit_tick / stop_loss_tick, 2)

    # Преобразуем данные для быстрого доступа
    data_dict = data.to_dict(orient="index")

    for _, fvg in tqdm(fvgs.iterrows(), total=len(fvgs), desc="Analyzing trades"):
        end_time = fvg['End Time']

        if end_time not in data.index:
            continue

        # Получаем индекс и следующую свечу
        entry_idx = data.index.get_loc(end_time) + 1
        if entry_idx >= len(data):
            continue

        entry_time = data.index[entry_idx]
        entry_data = data_dict[entry_time]
        entry_price = entry_data['Open']
        trade_type = 'short' if fvg['Start Price'] > fvg['End Price'] else 'long'
        take_profit = entry_price + take_profit_tick if trade_type == 'long' else entry_price - take_profit_tick
        stop_loss = entry_price - stop_loss_tick if trade_type == 'long' else entry_price + stop_loss_tick

        result, closing_price = None, None

        for i in range(entry_idx, len(data)):
            current_data = data_dict[data.index[i]]
            high_price = current_data['High']
            low_price = current_data['Low']

            if trade_type == 'long':
                if high_price >= take_profit:
                    result = 'Win'
                    closing_price = take_profit
                    break
                if low_price <= stop_loss:
                    result = 'Loss'
                    closing_price = stop_loss
                    break
            elif trade_type == 'short':
                if low_price <= take_profit:
                    result = 'Win'
                    closing_price = take_profit
                    break
                if high_price >= stop_loss:
                    result = 'Loss'
                    closing_price = stop_loss
                    break

        if result is None:
            continue

        profit_loss = abs(closing_price - entry_price) * 1000
        if result == 'Win':
            balance += profit_loss
            win_count += 1
        else:
            balance -= profit_loss
            loss_count += 1

        trades.append({
            'Entry Time': entry_time,
            'Type': trade_type,
            'Entry Price': entry_price,
            'Take Profit': take_profit,
            'Stop Loss': stop_loss,
            'Closing Price': closing_price,
            'Result': result,
            'Profit/Loss': round(profit_loss, 2),
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
