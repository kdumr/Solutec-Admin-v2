# gerenciarcpe.py
import customtkinter as ctk

class GerenciarCPE(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gerenciar CPE's")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Centralizar a janela na tela
        window_width = 400
        window_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Frame principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True)

        # Rótulo de exemplo
        label = ctk.CTkLabel(self.main_frame, text="Gerenciar CPE's", font=("Arial", 20))
        label.pack(pady=20)

        # Botão de exemplo para fechar a janela
        close_button = ctk.CTkButton(self.main_frame, text="Fechar", command=self.on_close)
        close_button.pack(pady=10)

    def on_close(self):
        self.destroy()
        self.master.deiconify()  # Restaurar o frame principal
