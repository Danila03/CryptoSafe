#<Main>  
import sys
from PyQt6.QtWidgets import QApplication, QDialog
from db_manager import init_database
from gui_components import LoginDialog, PasswordManagerApp

def main():
    app = QApplication(sys.argv)
    
    # 1. Шаг из модуля БД: Инициализируем хранилище
    db_salt = init_database()
    
    # 2. Шаг из модуля GUI: Запрашиваем мастер-пароль
    login_dialog = LoginDialog(db_salt)
    
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # 3. Шаг из модуля GUI: Открываем главное окно, передавая созданный ключ
        main_window = PasswordManagerApp(login_dialog.fernet)
        main_window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
