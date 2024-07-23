import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import os
import threading

class DownloaderApp:
    def __init__(self, root):
        window_width = 400
        window_height = 100
        self.root = root
        self.root.title("Solutec Admin Updater")
        self.root.geometry("400x100")
        self.root.iconbitmap("icon.ico")
        self.root.resizable(False, False)

        # Centralizar a janela na tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        
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
        
        # Inicia download automaticamente
        self.start_download()
        
    def start_download(self):
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
            self.update_label(f"Falha ao baixar o arquivo: {e}")

    def update_progress(self, percent):
        self.root.after(0, lambda: self.progress.config(value=percent))
        self.root.after(0, lambda: self.percent_label.config(text=f"{percent:.2f}%"))

    def update_label(self, text):
        self.root.after(0, lambda: self.label.config(text=text))

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
