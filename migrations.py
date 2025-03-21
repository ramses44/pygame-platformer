import sqlite3

def run_migrations():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS User (
                 id INTEGER PRIMARY KEY,
                 balance INTEGER NOT NULL DEFAULT 0
               )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Level (
                 id INTEGER PRIMARY KEY,
                 difficulty TEXT NOT NULL,
                 map_filepath TEXT NOT NULL,
                 max_coins INTEGER NOT NULL,
                 unlocked BOOLEAN NOT NULL DEFAULT 0,
                 cost INTEGER,
                 coins_collected INTEGER,
                 time_spent REAL
               )''')
    
    c.execute('INSERT OR IGNORE INTO User (id, balance) VALUES (1, 0)')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    run_migrations()