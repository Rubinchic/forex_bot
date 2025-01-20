import pandas as pd
from tqdm import tqdm
import datetime


def analyze_trades_with_fvg(data, fvgs, initial_balance=100, stop_loss_tick=0.001, take_profit_tick=0.003, time_frame="", start_time="", end_time=""):
    """
    Анализирует торговлю на основе FVG и возвращает статистику.
    """
    # Проверка наличия необходимых столбцов
    required_columns = ['Open', 'High', 'Low', 'Close']
    for column in required_columns:
        if column not in data.columns:
            raise ValueError(f"Missing required column: {column}")

    balance = initial_balance
    trades = []
    win_count = 0
    loss_count = 0
    max_consecutive_losses = 0
    current_losses = 0

    risk_reward = round(take_profit_tick / stop_loss_tick, 2)

    # Преобразуем данные для быстрого доступа
    data_dict = data.to_dict(orient="index")

    for _, fvg in tqdm(fvgs.iterrows(), total=len(fvgs), desc="Analyzing trades"):
        end_time_fvg = fvg['End Time']

        if end_time_fvg not in data.index:
            continue

        entry_idx = data.index.get_loc(end_time_fvg) + 1
        if entry_idx >= len(data):
            continue

        entry_time = data.index[entry_idx]
        entry_price = data_dict[entry_time]['Open']
        trade_type = 'short' if fvg['Start Price'] > fvg['End Price'] else 'long'
        take_profit = entry_price + take_profit_tick if trade_type == 'long' else entry_price - take_profit_tick
        stop_loss = entry_price - stop_loss_tick if trade_type == 'long' else entry_price + stop_loss_tick

        result = None
        closing_price = None

        for i in range(entry_idx, len(data)):
            high_price = data_dict[data.index[i]]['High']
            low_price = data_dict[data.index[i]]['Low']

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
            win_count += 1
            balance += profit_loss
            current_losses = 0
        else:
            loss_count += 1
            balance -= profit_loss
            current_losses += 1
            max_consecutive_losses = max(max_consecutive_losses, current_losses)

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
            'Risk-Reward': risk_reward,
            'Max Consecutive Losses': max_consecutive_losses
        })

    total_trades = win_count + loss_count
    winrate = (win_count / total_trades) * 100 if total_trades > 0 else 0
    final_balance_percent = ((balance - initial_balance) / initial_balance) * 100

    trades_df = pd.DataFrame(trades)

    # Сохранение результата в файл с уникальным именем
    current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{time_frame}_{start_time}_{end_time}_{current_datetime}.csv"
    trades_df.to_csv(filename, index=False)

    return trades, {
        'Total Trades': total_trades,
        'Winrate (%)': winrate,
        'Final Balance (%)': final_balance_percent,
        'Risk-Reward': risk_reward,
        'Max Consecutive Losses': max_consecutive_losses
    }
