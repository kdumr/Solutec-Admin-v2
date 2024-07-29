import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import os
import threading

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solutec Admin Updater")
        self.root.iconbitmap("icon.ico")
        self.root.resizable(False, False)

        self.default_window_height = 100
        self.extended_window_height = 150

        # Definir o tamanho inicial da janela
        self.set_window_size(400, self.default_window_height)

        self.url = "https://raw.githubusercontent.com/kdumr/Solutec-Admin-v2/main/solutecadmsetup.exe"
        self.save_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "setup.exe")
        
        # Criar janela
        self.label = tk.Label(root, text="Baixando o arquivo...")
        self.label.pack(pady=10)
        
        self.progress_frame = tk.Frame(root)
        self.progress_frame.pack(pady=10)

        self.progress = ttk.Progressbar(self.progress_frame, length=300, mode='determinate')
        self.progress.grid(row=0, column=0)
        
        self.percent_label = tk.Label(self.progress_frame, text="0%")
        self.percent_label.grid(row=0, column=1, padx=10)
        
        self.retry_button = None

        # Inicia download automaticamente
        self.start_download()
    
    def set_window_size(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        self.root.geometry(f'{width}x{height}+{position_right}+{position_top}')
        
    def start_download(self):
        if self.retry_button:
            self.retry_button.pack_forget()
            self.retry_button = None
            self.set_window_size(400, self.default_window_height)
        self.thread = threading.Thread(target=self.download_file)
        self.thread.start()
        
    def download_file(self):
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()  # Verifica erros HTTP

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(self.save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        progress_percent = (downloaded_size / total_size) * 100
                        self.update_progress(progress_percent)
            
            self.update_label("Download completo. Executando o arquivo...")
            self.root.after(1000, self.run_setup)

        except Exception as e:
            print(e)
            messagebox.showerror("Falha ao atualizar.", f"Não foi possível atualizar o software. Por favor, tente novamente mais tarde.\nSe estiver enfrentando dificuldades com a atualização, recomenda-se instalar o software manualmente no site.")
            self.show_retry_button()

    def update_progress(self, percent):
        self.root.after(0, lambda: self.progress.config(value=percent))
        self.root.after(0, lambda: self.percent_label.config(text=f"{percent:.2f}%"))

    def update_label(self, text):
        self.root.after(0, lambda: self.label.config(text=text))
    
    def show_retry_button(self):
        self.root.after(0, lambda: self.create_retry_button())
    
    def create_retry_button(self):
        self.retry_button = tk.Button(self.root, text="Tentar Novamente", command=self.start_download)
        self.retry_button.pack(pady=10)
        self.set_window_size(400, self.extended_window_height)
    
    def run_setup(self):
        if os.path.exists(self.save_path):
            os.startfile(self.save_path)
            self.root.destroy()
        else:
            messagebox.showerror("Erro", "Arquivo não encontrado.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
