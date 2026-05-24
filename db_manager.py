#<DataBase>
import os
import sqlite3
from crypto_engine import encrypt_data, decrypt_data

DB_NAME = "passwords.db"

def init_database() -> bytes:
    db_exists = os.path.exists(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS metadata (id INTEGER PRIMARY KEY, salt BLOB NOT NULL)')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, site TEXT, login TEXT, password TEXT NOT NULL
        )
    ''')
    conn.commit()
    
    if not db_exists:
        salt = os.urandom(16)
        cursor.execute("INSERT INTO metadata (id, salt) VALUES (1, ?)", (salt,))
        conn.commit()
    else:
        cursor.execute("SELECT salt FROM metadata WHERE id = 1")
        salt = cursor.fetchone()[0] # Исправлено: извлекаем байты из кортежа
    conn.close()
    return salt

def add_record_to_db(title: str, site: str, login: str, password: str, fernet) -> None:
    enc_title = encrypt_data(title, fernet)
    enc_site = encrypt_data(site, fernet)
    enc_login = encrypt_data(login, fernet)
    enc_pass = encrypt_data(password, fernet)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO credentials (title, site, login, password) VALUES (?, ?, ?, ?)",
        (enc_title, enc_site, enc_login, enc_pass)
    )
    conn.commit()
    conn.close()

def load_records_from_db(fernet) -> list:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Добавили ID в запрос
    cursor.execute("SELECT id, title, site, login, password FROM credentials")
    rows = cursor.fetchall()
    conn.close()
    
    decrypted_list = []
    for row in rows:
        db_id, enc_title, enc_site, enc_login, enc_pass = row
        try:
            dec_title = decrypt_data(enc_title, fernet)
            dec_site = decrypt_data(enc_site, fernet)
            dec_login = decrypt_data(enc_login, fernet)
            dec_pass = decrypt_data(enc_pass, fernet)
            # Передаем ID первым элементом
            decrypted_list.append((db_id, dec_title, dec_site, dec_login, dec_pass))
        except Exception:
            decrypted_list.append((db_id, "Ошибка декодирования", "", "", ""))
    return decrypted_list

def delete_record_from_db(record_id: int) -> None:
    """Удаляет запись из базы данных по её ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM credentials WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def is_database_empty() -> bool:
    """Возвращает True, если в сейфе еще нет ни одной записи, и False, если есть"""
    import sqlite3
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Запрашиваем количество строк в таблице паролей
    cursor.execute("SELECT COUNT(*) FROM credentials")
    count = cursor.fetchone()[0]
    
    conn.close()
    return count == 0