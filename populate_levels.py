import json
import os
import sqlite3
from pathlib import Path

LEVELS_DIR = Path("levels")

def get_level_files():
    return sorted(LEVELS_DIR.glob("level_*.json"), key=lambda x: int(x.stem.split("_")[1]))

def parse_level(file_path):
    with open(file_path) as f:
        data = json.load(f)
    
    coins = data.get("map", {}).get("coins", [])
    return {
        "map_filepath": str(file_path),
        "max_coins": len(coins)
    }

def get_level_metadata():
    levels = []
    for file in get_level_files():
        try:
            levels.append(parse_level(file))
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing {file.name}: {str(e)}")
    return levels

def prompt_difficulty_and_cost(level_id):
    while True:
        try:
            input_str = input(f"Уровень {level_id} - введите сложность и стоимость (например: MEDIUM 50): ")
            parts = input_str.strip().split()
            
            if len(parts) < 1:
                print("Некорректный ввод!")
                continue
                
            difficulty = parts[0].upper()
            cost = None
            
            if len(parts) > 1:
                cost = int(parts[1])
                if cost <= 0:
                    cost = None
                    
            return difficulty, cost
        except ValueError:
            print("Некорректная стоимость!")

def main():
    levels = get_level_metadata()
    print("LEN:", len(levels))
    if not levels:
        print("Не найдено ни одного валидного уровня!")
        return

    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    try:
        bonus_count = 0
        for i, level in enumerate(levels, 1):
            print(f"\nОбработка уровня {i}:")
            print(f"Монет на уровне: {level['max_coins']}")
            print(f"Файл уровня: {level['map_filepath']}")
            
            difficulty, cost = prompt_difficulty_and_cost(i)
            bonus_count += bool(cost)
            
            c.execute('''INSERT OR REPLACE INTO Level 
                        (id, difficulty, map_filepath, max_coins, unlocked, cost)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                    (i - bonus_count if not cost else bonus_count + 1000,
                     difficulty,
                     level['map_filepath'],
                     level['max_coins'],
                     1 if i == 1 else 0,  # Разблокировать только первый уровень
                     cost))
        
        conn.commit()
        print("\nУспешно добавлено уровней:", len(levels))
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()