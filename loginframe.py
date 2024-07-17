import customtkinter as ctk
from tkinter import messagebox

class LoginFrame(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Login")
        
        self.geometry("300x200")
        self.iconbitmap("icon.ico")
        self.wm_minsize(300, 200)
        self.wm_maxsize(300, 200)
        self.resizable(False, False)

        self.create_widgets()

        # Centralizar a janela na tela
        window_width = 300
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    def create_widgets(self):
        login_label = ctk.CTkLabel(self, text="Login", font=("Arial", 20))
        login_label.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=200)
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=200, show="*")
        self.password_entry.pack(pady=5)

        login_button = ctk.CTkButton(self, text="Login", command=self.validate_login)
        login_button.pack(pady=20)

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Adicionar Lógica para validar o login
        if username == "admin" and password == "password":
            messagebox.showinfo("Login", "Login successful!")
            self.destroy()  # Fechar a janela de login após o login bem-sucedido
        else:
            messagebox.showerror("Login", "Invalid username or password.")
