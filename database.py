import sqlite3
from typing import List, Dict, Optional

def get_connection():
    return sqlite3.connect('game.db')


def get_balance() -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT balance FROM User WHERE id = 1')
    balance = c.fetchone()[0]
    conn.close()
    return balance


def get_all_levels() -> List[Dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM Level ORDER BY id')
    levels = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return levels


def level_win(level_id: int, 
              coins_collected: Optional[int] = None, 
              time_spent: Optional[float] = None):
    conn = get_connection()
    c = conn.cursor()

    # Разблокировка следующего уровня
    c.execute("UPDATE Level SET unlocked = 1 WHERE id = ? AND cost IS NULL", (level_id + 1,))
    
    update_fields = []
    params = []

    c.execute('SELECT coins_collected, time_spent FROM Level WHERE id = ?', (level_id,))
    old_coins, old_time = c.fetchone()
    old_coins = old_coins if old_coins is not None else -1
    old_time = old_time if old_time is not None else 1e999
    
    if coins_collected is not None and coins_collected > old_coins:
        update_fields.append('coins_collected = ?')
        params.append(coins_collected)

        # Update balance
        c.execute('SELECT balance FROM User WHERE id = 1')
        balance = c.fetchone()[0]
        balance += coins_collected - old_coins
        c.execute('UPDATE User SET balance = ? WHERE id = 1', (balance,))
        
    if time_spent is not None and time_spent < old_time:
        update_fields.append('time_spent = ?') 
        params.append(time_spent)
    
    if update_fields:
        query = f'UPDATE Level SET {", ".join(update_fields)} WHERE id = ?'
        params.append(level_id)
        c.execute(query, params)
    
    conn.commit()
    conn.close()


def set_balance(balance: int):
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('UPDATE User SET balance = ? WHERE id = 1', (balance,))
    
    conn.commit()
    conn.close()


def reset_all():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('UPDATE User SET balance = 0 WHERE id = 1')
    c.execute('UPDATE Level SET unlocked = 0')
    c.execute('UPDATE Level SET unlocked = 1 WHERE id = 1')
    c.execute('UPDATE Level SET coins_collected = NULL, time_spent = NULL')
    
    conn.commit()
    conn.close()


def unlock_level(level_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE Level SET unlocked = 1 WHERE id = ?", (level_id,))
    conn.commit()
    conn.close()

def purchase_level(level_id: int) -> bool:
    """Пытается купить бонусный уровень. Возвращает True при успехе"""
    conn = get_connection()
    c = conn.cursor()
    
    # Получаем стоимость уровня и текущий баланс
    c.execute("SELECT cost FROM Level WHERE id = ?", (level_id,))
    cost = c.fetchone()[0]
    c.execute("SELECT balance FROM User WHERE id = 1")
    balance = c.fetchone()[0]
    
    if balance >= cost:
        c.execute("UPDATE User SET balance = balance - ? WHERE id = 1", (cost,))
        c.execute("UPDATE Level SET unlocked = 1 WHERE id = ?", (level_id,))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False