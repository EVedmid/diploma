import tkinter as tk
import json
import os
import logging
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
        self.master.title("RoboteRRR")
        self.master.geometry("400x300")
        
        self.db_file = "users.json"
        self.username = None
        self.authorized = False
        self.sim_client = None
        self.sim = None

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

        tk.Label(self.master, text="Ласкаво просимо до RoboteRRR!").pack(pady=20)
        
        tk.Button(self.master, text="Увійти", command=self.create_login_window).pack(pady=10)
        tk.Button(self.master, text="Реєстрація", command=self.create_register_window).pack(pady=10)
        tk.Button(self.master, text="Вийти", command=self.exit_program).pack(pady=10)

    def exit_program(self):
        """Закриття програми"""
        logging.info("Програма завершує роботу.")
        self.master.destroy()

    def create_login_window(self):
        """Створення вікна авторизації"""
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
        for widget in self.master.winfo_children():
            if widget != self.status_label:
                widget.destroy()

        tk.Label(self.master, text=f"Ласкаво просимо, {self.username}!").pack(pady=20)
        
        tk.Button(self.master, text="Почати симуляцію", command=self.start_simulation).pack(pady=10)
        tk.Button(self.master, text="Зупинити симуляцію", command=self.stop_simulation).pack(pady=10)
        tk.Button(self.master, text="Зберегти карту", command=self.save_map).pack(pady=10)
        tk.Button(self.master, text="Вийти", command=self.exit_program).pack(pady=10)

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

    def register(self, username, password):
        """Реєстрація нового користувача"""
        if not username or not password:
            self.show_status("Будь ласка, заповніть всі поля!", "red")
            return

        users = self.load_users()

        if username in users:
            self.show_status("Користувач із таким ім'ям уже існує!", "red")
        else:
            users[username] = password
            self.save_users(users)
            self.show_status("Реєстрація успішна!", "green")
            self.create_main_window()

    def start_simulation(self):
        """Запуск CoppeliaSim і симуляції"""
        try:
            if not self.sim_client:
                self.sim_client = RemoteAPIClient()
            if not self.sim:
                self.sim = self.sim_client.getObject('sim')
            self.sim.startSimulation()
            self.show_status("Симуляцію розпочато!", "green")
        except Exception as e:
            logging.error(f"Помилка запуску симуляції: {e}")
            self.show_status(f"Помилка запуску симуляції: {e}", "red")

    def stop_simulation(self):
        """Зупинка симуляції і збереження карти"""
        try:
            if self.sim:
                # Надсилаємо команду для збереження карти
                self.sim.setStringSignal("saveMapCommand", "save")
                self.show_status("Збереження карти...", "green")
                self.master.after(1000)  # Затримка 1 секунда

                # Зупиняємо симуляцію
                self.sim.stopSimulation()
                self.show_status("Симуляцію зупинено!", "green")
            else:
                self.show_status("Симуляцію не розпочато!", "red")
        except Exception as e:
            logging.error(f"Помилка зупинки симуляції: {e}")
            self.show_status(f"Помилка зупинки симуляції: {e}", "red")

    def save_map(self):
        """Збереження карти через сигнал"""
        try:
            if self.sim:
                self.sim.setStringSignal("saveMapCommand", "save")
                self.show_status("Команда на збереження карти надіслана!", "green")
            else:
                self.show_status("Немає даних для збереження!", "red")
        except Exception as e:
            logging.error(f"Помилка збереження карти: {e}")
            self.show_status(f"Помилка збереження карти: {e}", "red")

    def show_status(self, message, color):
        """Оновлення тексту статусу"""
        self.status_label.config(text=message, fg=color)


# Запуск програми
if __name__ == "__main__":
    root = tk.Tk()
    app = AuthClientGUI(root)
    root.mainloop()
