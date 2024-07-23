import customtkinter as ctk
import requests
import threading
from PIL import Image
from gerenciarcpe import GerenciarCPE 

class LoginFrame(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Solutec Admin - Login")
        
        self.geometry("300x300")
        self.after(250, lambda: self.iconbitmap('icon.ico')) # Corrige bug do icon atrasando
        self.resizable(False, False)

        self.create_widgets()

        # Centralizar a janela na tela
        window_width = 300
        window_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True)

        login_label = ctk.CTkLabel(self.main_frame, text="Login", font=("Arial", 20))
        login_label.pack(pady=10)

        # Adicionar logo
        logo_path = "assets/img/circle-exclamation-solid.png"
        self.logo = Image.open(logo_path)

        # Redimensionar a imagem mantendo a proporção
        max_size = (30, 30)
        self.logo.thumbnail(max_size, Image.LANCZOS)

        self.error_frame = ctk.CTkFrame(self.main_frame, fg_color="lightcoral")
        
        self.icon_error = ctk.CTkImage(self.logo, size=self.logo.size)
        self.iconeError_label = ctk.CTkLabel(self.error_frame, image=self.icon_error, text="")
        self.iconeError_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.error_frame.grid_rowconfigure(0, weight=1)
        self.error_frame.grid_columnconfigure(0, weight=1)
        self.error_frame.grid_columnconfigure(1, weight=1)
        
        self.error_label = ctk.CTkLabel(self.error_frame, text="", font=("Arial", 14), text_color="#7b0006")
        self.error_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Esconder o frame de erro inicialmente
        self.error_frame.pack_forget()

        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username", width=200)
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", width=200, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self.main_frame, text="Login", command=self.start_login_thread)
        self.login_button.pack(pady=20)

    def start_login_thread(self):
        self.login_button.configure(state="disabled")
        threading.Thread(target=self.validate_login).start()

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Limpar qualquer mensagem de erro anterior
        self.hide_error_frame()

        # Validação de login
        if username == "" or password == "":
            self.show_error("Digite o usuário e a senha!", "lightcoral", "assets/img/circle-exclamation-solid.png")
            self.login_button.configure(state="normal")
            return
        elif username == "admin" or password == "admin":
            
            self.show_error("Você está logado.", "lightgreen", "assets/img/circle-check-regular.png")
            gerenciar_cpe_window = GerenciarCPE(master=self.master)  # Abrir a nova janela
            self.destroy()  # Fechar a janela de login
        else:
            try:
                response = requests.get(f"https://flashman.gigalink.net.br/api/v2/device/update/", auth=(username, password))
                responseLicense = response.status_code
                if responseLicense == 401:
                    self.show_error("Usuário ou senha inválidos.", "lightcoral", "assets/img/circle-exclamation-solid.png")
                elif responseLicense == 404: # Caso o login for sucedido
                    
                    self.show_error("Você está logado.", "lightgreen", "assets/img/circle-check-regular.png")

            except Exception as erro:
                self.show_error(f"Erro: {erro}", "lightcoral", "assets/img/circle-exclamation-solid.png")
            finally:
                self.login_button.configure(state="normal")

    def show_error(self, message, color, icon_path):
        self.error_frame.configure(fg_color=color)
        self.logo = Image.open(icon_path)

        # Redimensionar a imagem mantendo a proporção
        max_size = (30, 30)
        self.logo.thumbnail(max_size, Image.LANCZOS)

        self.icon_error = ctk.CTkImage(self.logo, size=self.logo.size)
        self.iconeError_label.configure(image=self.icon_error)

        self.error_label.configure(text=message, text_color="#7b0006" if color == "lightcoral" else "green")
        self.error_frame.pack(pady=5, padx=5, fill="x", expand=False)
        self.main_frame.pack_configure(pady=10)  # Ajusta a posição do frame principal
        # Ocultar o frame de erro após 5 segundos
        self.after(5000, self.hide_error_frame)

    def hide_error_frame(self):
        self.error_frame.pack_forget()
        self.main_frame.pack_configure(pady=0)  # Ajusta a posição do frame principal

# Teste da aplicação
if __name__ == "__main__":
    root = ctk.CTk()
    root.iconbitmap("icon.ico")  # Certifique-se de que o caminho está correto e o formato do ícone está correto
    app = LoginFrame(master=root)
    app.mainloop()
