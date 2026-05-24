# <Visual-components>
from PyQt6.QtWidgets import (
    QDialog, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, 
    QMessageBox, QHeaderView, QSpinBox, QApplication,QMenu )
from PyQt6.QtCore import Qt, QSettings

# Импортируем связи из наших созданных ранее модулей
from crypto_engine import generate_key_from_password, generate_strong_password
from db_manager import add_record_to_db, load_records_from_db, delete_record_from_db, is_database_empty

#Темы оформления
BASE_STYLE = """
    QLabel { font-size: 13px; font-weight: bold; }
    
    /* кнопка-шестерёнка */
    QPushButton#btn_settings { padding: 0px; border-radius: 4px; font-size: 16px; }
    
    QTableWidget { border: 1px solid VAR_BORDER; gridline-color: VAR_GRID; font-size: 13px; }
    QHeaderView::section { border: 1px solid VAR_GRID; padding: 4px; font-weight: bold; }
    
    /* хитбокс QSpinBox */
    QSpinBox { padding-right: 25px; min-height: 24px; font-size: 13px; }
    
    /* --- КРАСИМ ЛЕВЫЙ ВЕРХНИЙ УГОЛ ТАБЛИЦЫ --- */
    QTableWidget QTableCornerButton::section {
        background-color: VAR_HEADER_BG;
        border: 1px solid VAR_GRID;
    }
"""



# Палитры цветов для каждой темы
THEMES = {
    # Системная (тёмная)
    "dark-grey": BASE_STYLE.replace("VAR_GRID", "#3f3f3f").replace("VAR_HEADER_BG", "#2d2d2d") + """
        QMainWindow { background-color: #1e1e1e; }
        QLabel { color: #ffffff; }
        QLineEdit, QSpinBox { background-color: #2d2d2d; color: #ffffff; }
        QPushButton { background-color: #3e3e42; color: #ffffff; }
        QPushButton:hover { background-color: #505054; }
        QTableWidget { background-color: #1e1e1e; color: #ffffff; }
        QHeaderView::section { background-color: #2d2d2d; color: #ffffff; }

    """,
    
    # Светлая
    "white": BASE_STYLE.replace("VAR_GRID", "#e0e0e0").replace("VAR_HEADER_BG", "#e1e1e1") + """
        QMainWindow { background-color: #f0f0f0; }
        QLabel { color: #000000; }
        QLineEdit, QSpinBox { background-color: #ffffff; color: #000000; }
        QPushButton { background-color: #e1e1e1; color: #000000; }
        QPushButton:hover { background-color: #d0d0d0; }
        QTableWidget { background-color: #ffffff; color: #000000; }
        QHeaderView::section { background-color: #e1e1e1; color: #000000; }
        
    """,
    
    # Серая
    "grey": BASE_STYLE.replace("VAR_BORDER", "#666666").replace("VAR_GRID", "#666666").replace("VAR_HEADER_BG", "#666666") + """
        QMainWindow { background-color: #444444; }
        QLabel { color: #ffffff; }
        QLineEdit, QSpinBox { background-color: #555555; color: #ffffff; }
        QPushButton { background-color: #666666; color: #ffffff; }
        QPushButton:hover { background-color: #777777; }
        QTableWidget { background-color: #555555; color: #ffffff; }
        QHeaderView::section { background-color: #666666; color: #ffffff; }
    """,
    
    # Глубокая тёмная
    "black": BASE_STYLE.replace("VAR_BORDER", "#404040").replace("VAR_GRID", "#333333").replace("VAR_HEADER_BG", "#262626") + """
        QMainWindow { background-color: #1a1a1a; }
        QLabel { color: #ffffff; }
        QLineEdit, QSpinBox { background-color: #262626; color: #ffffff; }
        QPushButton { background-color: #333337; color: #ffffff; }
        QPushButton:hover { background-color: #434346; }
        QTableWidget { background-color: #1a1a1a; color: #ffffff; }
        QHeaderView::section { background-color: #262626; color: #ffffff; }
    """
}

class LoginDialog(QDialog):
    def __init__(self, salt):
        super().__init__()
        self.salt = salt
        self.fernet = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("CryptoSafe")
        self.setFixedSize(350, 150)


        layout = QVBoxLayout()
        # --- ДИНАМИЧЕСКИЙ ТЕКСТ ИНСТРУКЦИИ ---
        # Проверяем, пользовался ли человек программой ранее
        if is_database_empty():
            # Если база пуста — это первый запуск
            text_instruction = "✨ Добро пожаловать! Придумайте и введите ваш\nГлавный (Мастер) пароль для создания сейфа:"
            button_text = "Создать новый сейф"
        else:
            # Если пароли уже есть — это обычный вход
            text_instruction = "🔒 Сейф заблокирован.\nВведите ваш Мастер-Пароль для доступа к данным:"
            button_text = "Открыть сейф"
        
        self.label = QLabel(text_instruction)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Минимум 12-14 символов для безопасности")

        self.btn_login = QPushButton(button_text)
        self.btn_login.clicked.connect(self.try_login)

        layout.addWidget(self.label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.btn_login)
        self.setLayout(layout)

        # Стилизуем окно входа под общую темную палитру приложения
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; }
            QLabel { color: #ffffff; font-size: 12px; font-weight: normal; line-height: 15px; }
            QLineEdit { background-color: #2d2d2d; color: #ffffff; border: 1px solid #3f3f3f; padding: 6px; border-radius: 3px; }
            QPushButton { background-color: #2b579a; color: white; font-weight: bold; padding: 6px; border-radius: 3px; }
            QPushButton:hover { background-color: #1e4785; }
        """)
        
    def try_login(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Ошибка", "Пароль пустой!")
            return
        key = generate_key_from_password(password, self.salt)
        from cryptography.fernet import Fernet
        self.fernet = Fernet(key)
        self.accept()

class PasswordManagerApp(QMainWindow):
    def __init__(self, fernet):
        super().__init__()
        self.fernet = fernet

        self.all_records = []

        self.target_row_idx = -1

        self.settings = QSettings("MyCryptoLab", "PasswordManager")
        self.init_ui()
        saved_theme = self.settings.value("theme", "system")
        self.apply_theme(saved_theme)

        self.refresh_table()
        
    def init_ui(self):
        self.setWindowTitle("CryptoSafe")
        self.setMinimumSize(850, 500) # Минимальное расширение окна при запуске
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Поля ввода
        form_layout = QHBoxLayout()
        self.input_title = QLineEdit(); self.input_title.setPlaceholderText("Название"); self.input_title.setMaxLength(64)
        self.input_site = QLineEdit(); self.input_site.setPlaceholderText("Сайт"); self.input_site.setMaxLength(64)
        self.input_login = QLineEdit(); self.input_login.setPlaceholderText("Логин"); self.input_login.setMaxLength(64)
        self.input_pass = QLineEdit(); self.input_pass.setPlaceholderText("Пароль"); self.input_pass.setMaxLength(64)
        form_layout.addWidget(self.input_title)
        form_layout.addWidget(self.input_site)
        form_layout.addWidget(self.input_login)
        form_layout.addWidget(self.input_pass)
        
        # Генератор
        gen_layout = QHBoxLayout()
        self.spin_length = QSpinBox()
        self.spin_length.setRange(10, 60)
        self.spin_length.setValue(14)

        btn_gen = QPushButton("Сгенерировать")
        btn_gen.clicked.connect(self.generate_password_field)

        gen_layout.addWidget(QLabel("Длина:"))
        gen_layout.addWidget(self.spin_length)
        gen_layout.addWidget(btn_gen)
        gen_layout.addStretch()
        
        btn_add = QPushButton("🔒 Зашифровать и добавить")
        btn_add.clicked.connect(self.add_record)
        
        #Поисковик
        search_layout = QHBoxLayout()
        self.input_search = QLineEdit() 
        self.input_search.setPlaceholderText("🔍 Быстрый поиск...")
        self.input_search.setMaximumWidth(300)
        self.input_search.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.input_search)
        
        #"пружина" между поисковиком и шестерёнкой
        search_layout.addStretch() 

        # Создаем кнопку-шестеренку
        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setFixedSize(32, 32)
        self.btn_settings.setToolTip("Настройки оформления")
        # Привязываем нажатие к вызову выпадающего меню
        self.btn_settings.clicked.connect(self.show_settings_menu)
        search_layout.addWidget(self.btn_settings)

        # Настройка таблицы. 5 колонок (последняя для кнопок действий)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Ресурс", "Сайт", "Логин", "Пароль", "Действия"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Колонка действий не должна сильно растягиваться
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(4, 180)
        
        main_layout.addLayout(form_layout) #поля для добавления пароля
        main_layout.addLayout(gen_layout) #Генератор пароля
        main_layout.addWidget(btn_add)
        main_layout.addLayout(search_layout) #Поисковик
        main_layout.addLayout(search_layout) # Поиск и шестеренка на одном уровне
        main_layout.addWidget(self.table) #Таблица

    def show_settings_menu(self):
        """Создает и показывает всплывающее окошко-меню возле шестеренки"""
        menu = QMenu(self)
        
        # Добавляем пункты выбора тем в меню
        action_system = menu.addAction("тёмно-серая тема")
        action_white = menu.addAction("Светлая тема")
        action_grey = menu.addAction("Серая тема")
        action_black = menu.addAction("Тёмная тема")
        
        # Связываем каждый пункт с передачей имени темы в функцию смены
        action_system.triggered.connect(lambda: self.apply_theme("dark-grey"))
        action_white.triggered.connect(lambda: self.apply_theme("white"))
        action_grey.triggered.connect(lambda: self.apply_theme("grey"))
        action_black.triggered.connect(lambda: self.apply_theme("black"))
        
        # Заставляем меню всплыть ровно под кнопкой-шестеренкой
        # Для этого переводим локальные координаты кнопки в глобальные координаты экрана
        button_pos = self.btn_settings.mapToGlobal(self.btn_settings.rect().bottomLeft())
        menu.exec(button_pos)

    #стилизация HUD
    def apply_theme(self, theme_name):
        """Применяет выбранную тему к приложению и записывает её в память ПК"""
        if theme_name in THEMES:
            # Применяем QSS-скрипт к главному окну программы
            self.setStyleSheet(THEMES[theme_name])
            
            # Сохраняем выбор в реестр ОС / файл конфигурации, чтобы настройки не слетели при перезапуске
            self.settings.setValue("theme", theme_name)

    def generate_password_field(self):
        self.input_pass.setText(generate_strong_password(self.spin_length.value()))


    #Добавление в список"
    def add_record(self):
        title, site = self.input_title.text(), self.input_site.text()
        login, password = self.input_login.text(), self.input_pass.text()
        
        if not password or not login:
            QMessageBox.warning(self, "Внимание", "Заполните Название и Пароль!")
            return
        
        elif not title:
            title = site

        add_record_to_db(title, site, login, password, self.fernet)
        
        self.input_title.clear(); self.input_site.clear()
        self.input_login.clear(); self.input_pass.clear()
        self.refresh_table()

    def filter_table(self):
        """Проверяет совпадение по колонкам Название (Ресурс) или (Сайт)"""
        # Переводим поисковый запрос в нижний регистр, чтобы поиск работал независимо от больших/маленьких букв
        search_text = self.input_search.text().lower().strip()
        
        # Если поисковая строка пустая, просто выводим весь блокнот записей целиком
        if not search_text:
            self.update_table_view(self.all_records)
            return
            
        filtered_list = []
        
        # Бежим по нашему кэшированному блокноту всех записей
        for row in self.all_records:
            db_id, dec_title, dec_site, dec_login, dec_pass = row
            
            # Переводим название и сайт в нижний регистр для корректного сравнения
            title_lower = dec_title.lower()
            site_lower = dec_site.lower()
            
            # Главное условие: если введенный текст есть внутри Названия ИЛИ внутри Сайта
            if search_text in title_lower or search_text in site_lower:
                # Добавляем эту строку в наш новый отфильтрованный список
                filtered_list.append(row)
                
        # Просим наш отрисовщик вывести на экран только те строки, которые подошли
        self.update_table_view(filtered_list)

    def refresh_table(self):
        records = load_records_from_db(self.fernet)
        self.all_records = records #Сохраняем скачанные записи в наш блокнот-кэш для мгновенного поиска

        self.update_table_view(self.all_records) # Вызываем функцию отрисовки, передавая ей ВСЕ записи


    def update_table_view(self, records_list):
        self.table.setRowCount(0)
        
        for row_idx, row in enumerate(records_list):

            # Извлекаем данные строки
            db_id, dec_title, dec_site, dec_login, dec_pass = row      #<================
            
            # Заполняем текстовые ячейки
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(dec_title))
            self.table.setItem(row_idx, 1, QTableWidgetItem(dec_site))
            self.table.setItem(row_idx, 2, QTableWidgetItem(dec_login))
            
            # Для пароля создаем скрытую версию (кружочки или точки)
            hidden_pass = "•" * len(dec_pass)
            pass_item = QTableWidgetItem(hidden_pass)
            # Сохраняем реальный пароль внутри самого объекта ячейки (скрыто от глаз)
            pass_item.setData(Qt.ItemDataRole.UserRole, dec_pass)
            self.table.setItem(row_idx, 3, pass_item)
            
            # --- Создаем блок кнопок управления ---
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(4)
            
            btn_show = QPushButton("👁️")
            btn_show.setToolTip("Показать/Скрыть пароль")
            # Связываем кнопку с функцией переключения видимости через lambda
            btn_show.clicked.connect(lambda checked, r=row_idx: self.toggle_password_visibility(r))
            
            btn_delete = QPushButton("❌")
            btn_delete.setFixedSize(36, 26)
            btn_delete.setToolTip("Удалить")
            btn_delete.setStyleSheet("background-color: #bd2130; border: 1px solid #b21f2d;")
            btn_delete.clicked.connect(lambda checked, id_to_del=db_id: self.delete_record(id_to_del))

            btn_copy = QPushButton("📋")
            btn_copy.setToolTip("Копировать в буфер")
            btn_copy.clicked.connect(lambda checked, r=row_idx: self.copy_password_to_clipboard(r))
            
            actions_layout.addWidget(btn_show)  #добавляет кнопку "скрыть/показать" в список
            actions_layout.addWidget(btn_copy)  #добавляет кноку "копировать в буфер обмена" в список
            actions_layout.addWidget(btn_delete) #добавляет кнопку "удалить" в список
            actions_widget.setLayout(actions_layout) #Отображает кнопки ранее добавленный в список actions_layout
            
            
            # Вставляем виджет с кнопками прямо в 4-ю колонку таблицы
            self.table.setCellWidget(row_idx, 4, actions_widget)


    def toggle_password_visibility(self, row_idx):
        """Высокопроизводительное переключение видимости пароля с автосменой иконок"""
        
        # 1. Если кликнули на строку, которая УЖЕ открыта — просто скрываем её
        if self.target_row_idx == row_idx:
            self.change_password_state(row_idx, hide=True)
            self.target_row_idx = -1  # Теперь все пароли снова скрыты
            return

        # 2. Если в программе БЫЛ открыт какой-то другой пароль — точечно закрываем только его
        if self.target_row_idx != -1:
            self.change_password_state(self.target_row_idx, hide=True)

        # 3. Открываем новый целевой пароль
        self.change_password_state(row_idx, hide=False)
        # Запоминаем текущую открытую строку
        self.target_row_idx = row_idx


    def change_password_state(self, row_idx, hide=True):
        """Точечно меняет текст и иконку в указанной строке без циклов перебора"""
        if row_idx < 0 or row_idx >= self.table.rowCount():
            return
            
        pass_item = self.table.item(row_idx, 3)
        actions_widget = self.table.cellWidget(row_idx, 4)
        
        if pass_item and actions_widget:
            real_password = pass_item.data(Qt.ItemDataRole.UserRole)
            # Достаем самую первую кнопку из горизонтального слоя ячейки действий (это наш глазик)
            btn_show = actions_widget.layout().itemAt(0).widget()
            
            if hide:
                pass_item.setText("•" * len(real_password))
                btn_show.setText("👁️")  # Ставим обычный глазик
                btn_show.setToolTip("Показать пароль")
            else:
                pass_item.setText(real_password)
                btn_show.setText("🙈")  # Ставим скрывающийся смайлик/перечеркнутый глаз
                btn_show.setToolTip("Скрыть пароль")


    def copy_password_to_clipboard(self, row_idx):
        """Копирует реальный пароль в буфер обмена ОС без его показа на экране"""
        pass_item = self.table.item(row_idx, 3)
        real_password = pass_item.data(Qt.ItemDataRole.UserRole)
        
        # Получаем объект буфера обмена операционной системы через QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(real_password)
        
        # Небольшое всплывающее уведомление в статус-баре или окне
        QMessageBox.information(self, "Успех", "Пароль скопирован в буфер обмена!")

    def delete_record(self, record_id):
        reply = QMessageBox.question(
            self, 'Подтверждение', 'Удалить эту запись безвозвратно?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_record_from_db(record_id)
            self.refresh_table()
            self.target_row_idx = -1
