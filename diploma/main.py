import tkinter as tk
import json
import os
import threading
import logging
import subprocess
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

# Налаштування логування
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class AuthClientGUI:
    def __init__(self, master):
        """Ініціалізація GUI клієнта"""
        self.master = master
        self.master.title("Клієнт Авторизації")
        self.master.geometry("400x300")
        
        self.db_file = "users.json"
        self.username = None
        self.authorized = False
        self.sim_client = None
        self.sim = None
        self.coppelia_process = None  # Процес для запуску CoppeliaSim

        # Головний статус напис
        self.status_label = tk.Label(self.master, text="", fg="green")
        self.status_label.pack(side=tk.BOTTOM, pady=10)

        # Створюємо файл бази даних, якщо його ще немає
        if not self.db_file_exists():
            self.create_empty_user_db()

        # Головне вікно
        self.create_main_window()

    def db_file_exists(self):
        """Перевірка наявності файлу бази даних"""
        return os.path.exists(self.db_file)

    def create_empty_user_db(self):
        """Створення порожньої бази даних"""
        with open(self.db_file, "w") as file:
            json.dump({}, file)

    def load_users(self):
        """Завантаження користувачів із файлу"""
        with open(self.db_file, "r") as file:
            return json.load(file)

    def save_users(self, users):
        """Збереження користувачів до файлу"""
        with open(self.db_file, "w") as file:
            json.dump(users, file, indent=4)

    def create_main_window(self):
        """Створення головного вікна"""
        # Видаляємо всі попередні віджети, крім статусу
        for widget in self.master.winfo_children():
            if widget != self.status_label:
                widget.destroy()

        tk.Label(self.master, text="Ласкаво просимо до клієнта CoppeliaSim!").pack(pady=20)
        
        tk.Button(self.master, text="Увійти", command=self.create_login_window).pack(pady=10)
        tk.Button(self.master, text="Реєстрація", command=self.create_register_window).pack(pady=10)
        tk.Button(self.master, text="Вийти", command=self.exit_program).pack(pady=10)

    def exit_program(self):
        """Закриття програми"""
        logging.info("Програма завершує роботу.")
        # Завершуємо процес CoppeliaSim, якщо він запущений
        if self.coppelia_process:
            self.coppelia_process.terminate()
            logging.info("Процес CoppeliaSim зупинено.")
        self.master.destroy()

    def create_login_window(self):
        """Створення вікна авторизації"""
        # Видаляємо всі попередні віджети, крім статусу
        for widget in self.master.winfo_children():
            if widget != self.status_label:
                widget.destroy()

        tk.Label(self.master, text="Авторизація").pack(pady=10)

        tk.Label(self.master, text="Ім'я користувача").pack()
        username_entry = tk.Entry(self.master)
        username_entry.pack()

        tk.Label(self.master, text="Пароль").pack()
        password_entry = tk.Entry(self.master, show="*")
        password_entry.pack()

        tk.Button(self.master, text="Увійти", command=lambda: self.login(username_entry.get(), password_entry.get())).pack(pady=10)
        tk.Button(self.master, text="Назад", command=self.create_main_window).pack(pady=10)

    def create_register_window(self):
        """Створення вікна реєстрації"""
        # Видаляємо всі попередні віджети, крім статусу
        for widget in self.master.winfo_children():
            if widget != self.status_label:
                widget.destroy()

        tk.Label(self.master, text="Реєстрація").pack(pady=10)

        tk.Label(self.master, text="Ім'я користувача").pack()
        username_entry = tk.Entry(self.master)
        username_entry.pack()

        tk.Label(self.master, text="Пароль").pack()
        password_entry = tk.Entry(self.master, show="*")
        password_entry.pack()

        tk.Button(self.master, text="Зареєструватися", command=lambda: self.register(username_entry.get(), password_entry.get())).pack(pady=10)
        tk.Button(self.master, text="Назад", command=self.create_main_window).pack(pady=10)

    def create_simulation_window(self):
        """Вікно управління симуляцією"""
        # Видаляємо всі попередні віджети, крім статусу
        for widget in self.master.winfo_children():
            if widget != self.status_label:
                widget.destroy()

        tk.Label(self.master, text=f"Ласкаво просимо, {self.username}!").pack(pady=20)
        
        tk.Button(self.master, text="Почати симуляцію", command=self.start_simulation).pack(pady=10)
        tk.Button(self.master, text="Зупинити симуляцію", command=self.stop_simulation).pack(pady=10)
        tk.Button(self.master, text="Зберегти карту", command=self.save_map).pack(pady=10)
        tk.Button(self.master, text="Назад", command=self.create_main_window).pack(pady=10)

    def login(self, username, password):
        """Авторизація користувача"""
        if not username or not password:
            self.show_status("Будь ласка, заповніть всі поля!", "red")
            return

        users = self.load_users()

        if username in users and users[username] == password:
            self.authorized = True
            self.username = username
            self.show_status("Авторизація успішна!", "green")
            self.create_simulation_window()
        else:
            self.show_status("Невірне ім'я користувача або пароль!", "red")

    def start_simulation(self):
        """Запуск симуляції"""
        try:
            if not self.sim_client:
                self.sim_client = RemoteAPIClient()
            if not self.sim:
                self.sim = self.sim_client.getObject('sim')

            logging.info("Спроба запуску симуляції...")
            self.sim.startSimulation()
            self.show_status("Симуляцію розпочато!", "green")
        except Exception as e:
            logging.error(f"Помилка запуску симуляції: {e}")
            self.show_status(f"Помилка запуску симуляції: {e}", "red")

    def stop_simulation(self):
        """Зупинка симуляції"""
        try:
            if self.sim:
                logging.info("Спроба зупинки симуляції...")
                self.sim.stopSimulation()
                self.show_status("Симуляцію зупинено!", "green")
            else:
                self.show_status("CoppeliaSim не підключено!", "red")
        except Exception as e:
            logging.error(f"Помилка зупинки симуляції: {e}")
            self.show_status(f"Помилка зупинки симуляції: {e}", "red")

    
    def save_map(self):
        """Збереження карти"""
        def save_map_task():
            try:
                if self.sim:
                    logging.info("Спроба збереження карти...")
                    # Перевірка і виклик Lua-функції
                    result = self.sim.callScriptFunction(
                        'saveMap@PioneerP3DX',  # Замініть на точне ім'я вашого об'єкта
                        self.sim.scripttype_childscript,  # Змініть тип скрипта, якщо це потрібно
                        {"path": "C:/diploma/map.bmp"}
                    )
                    logging.info(f"Результат виклику Lua-функції: {result}")
                    self.show_status("Карту збережено в C:/diploma/map.bmp!", "green")
                else:
                    self.show_status("CoppeliaSim не підключено!", "red")
                    logging.warning("CoppeliaSim не підключено!")
            except Exception as e:
                logging.error(f"Помилка збереження карти: {e}")
                self.show_status(f"Помилка збереження карти: {e}", "red")
    
        # Запускаємо збереження карти в окремому потоці
        threading.Thread(target=save_map_task, daemon=True).start()
    


    def show_status(self, message, color):
        """Оновлення тексту статусу"""
        self.status_label.config(text=message, fg=color)


# Запуск програми
if __name__ == "__main__":
    root = tk.Tk()
    app = AuthClientGUI(root)
    root.mainloop()
