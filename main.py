import customtkinter as ctk
import pyperclip
import pyautogui
import pynput
import threading
import time
from tkinter import messagebox
from pynput.keyboard import Key, Listener
from PIL import Image
from loginframe import LoginFrame  # Importando a janela de login

version = "1.0"
keyboard_listener = None  # Variável global para armazenar o listener do teclado
keyboard_listenerCancel = None

class Main:
    @staticmethod
    def main():
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        root = ctk.CTk()
        root.title("Solutec Admin")
        root.iconbitmap("icon.ico")
        root.geometry("350x480")
        root.wm_minsize(350, 480)
        root.wm_maxsize(400, 480)

        # Frame principal para centralização
        frame = ctk.CTkFrame(root, fg_color="transparent")
        frame.pack()

        # Novo frame para colar macs
        paste_frame = ctk.CTkFrame(root, fg_color="transparent")
        paste_frame.pack_forget()

        one_label = ctk.CTkLabel(paste_frame, text="Use a tecla [END] para colar os mac's\nem sequência.", padx=10, pady=10, font=("Arial", 15))
        one_label.grid(row=0, column=0, pady=10, sticky="nsew")

        two_label = ctk.CTkLabel(paste_frame, text="Use a tecla [HOME] para colar\num mac por vez.", padx=10, pady=10, font=("Arial", 15))
        two_label.grid(row=1, column=0, pady=10, sticky="nsew")

        three_label = ctk.CTkLabel(paste_frame, text="Use a tecla [PAGE DOWN] para colar\nos mac's na vertical.", padx=10, pady=10, font=("Arial", 15))
        three_label.grid(row=2, column=0, pady=10, sticky="nsew")

        four_label = ctk.CTkLabel(paste_frame, text="Use a tecla [DELETE] para colar\nos mac's na vertical.", padx=10, pady=10, text_color="red", font=("Arial", 15))
        four_label.grid(row=3, column=0, pady=10, sticky="nsew")

        back_button = ctk.CTkButton(paste_frame, text="Voltar", height=40, command=lambda: showMainFrame(paste_frame))
        back_button.grid(row=4, column=0, pady=10, sticky="ns")

        # Ajustar as colunas e linhas para se expandirem
        paste_frame.grid_rowconfigure(0, weight=1)
        paste_frame.grid_rowconfigure(1, weight=1)
        paste_frame.grid_rowconfigure(2, weight=1)
        paste_frame.grid_columnconfigure(0, weight=1)

        # Funções:

        macArray = []
        def cancelar(key):
            if key == Key.home:
                return False

        def addMacToFrame(mac):
            appearance_mode = ctk.get_appearance_mode()
            mac_frame_color = "#2d3436" if appearance_mode == "Dark" else "#dfe6e9"
            mac_frame = ctk.CTkFrame(macDisplayFrame, height=30, fg_color=mac_frame_color)
            mac_frame.pack(fill="x", padx=5, pady=2)

            mac_label = ctk.CTkLabel(mac_frame, text=mac)
            mac_label.pack(side="left", padx=5)

            remove_button = ctk.CTkButton(mac_frame, text="X", width=30, command=lambda: removeMac(mac, mac_frame))
            remove_button.pack(side="right", padx=5)

            copy_button = ctk.CTkButton(mac_frame, text="Copiar", width=20, command=lambda m=mac: copyMac(m))
            copy_button.pack(side="right", padx=5)

        def removeMac(mac, frame):
            macArray.remove(mac)
            frame.destroy()
            macTotalRegister_label.configure(text=f"Mac's registrados: {len(macArray)}")

        def copyMac(mac):
            pyperclip.copy(mac)
            messagebox.showinfo("Copiado", f"MAC '{mac}' copiado para a área de transferência.")

        def sendMac(event=None):
            macInput = macEntry.get().replace(":", "").replace("-", "")
            if len(macInput) != 12:
                messagebox.showerror("Erro", "O Mac deve conter 12 caracteres.")
                macEntry.delete(0, "end")
            else:
                mac = '{}:{}:{}:{}:{}:{}'.format(macInput[:2], macInput[2:4], macInput[4:6], macInput[6:8], macInput[8:10], macInput[10:])
                if mac in macArray:
                    messagebox.showerror("Erro", "Este MAC já está na lista.")
                    macEntry.delete(0, "end")
                else:
                    macArray.append(mac)
                    macEntry.delete(0, "end")
                    addMacToFrame(mac)
                    macTotalRegister_label.configure(text=f"Mac's registrados: {len(macArray)}")

        def showPasteMacFrame():
            if macArray:
                frame.pack_forget()
                paste_frame.pack(fill="both", expand=True)

                thread = threading.Thread(target=start_listener)
                thread.start()
            else:
                messagebox.showerror(title="Error", message="A lista de Mac's está vazia.")

        def showMainFrame(paste_frame):
            global keyboard_listener
            if keyboard_listener:
                keyboard_listener.stop()  # Para o listener do teclado
                keyboard_listener = None  # Redefine a variável para None

            # Ocultar o frame de colar macs
            paste_frame.pack_forget()
            # Mostrar o frame principal novamente
            frame.pack()

        def keyFunction(key):
            if key == Key.delete:
                showMainFrame(paste_frame)
                return False
            
            if key == Key.end:
                # Bloquear Mouse
                original_position = pyautogui.position()
                pyautogui.FAILSAFE = False
                pyautogui.moveTo(-100, -100)
                mouse_listener = pynput.mouse.Listener(suppress=True)
                mouse_listener.start()

                for i in range(len(macArray)):
                    pyperclip.copy(macArray[i])
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl', 'v')
                    pyautogui.hotkey(',')
                pyautogui.hotkey('enter')

                # Desbloquear mouse
                mouse_listener.stop()
                pyautogui.moveTo(original_position)
                pyautogui.FAILSAFE = True
                messagebox.showinfo("OK", "Os MAC's foram colados com sucesso")
                showMainFrame(paste_frame)  # Retornar ao frame principal
                return False

            if key == Key.home:
                i = 0

                while True:
                    pyperclip.copy(macArray[i])
                    pyautogui.hotkey('ctrl', 'v')
                    pyautogui.hotkey('enter')
                    i += 1
                    if i == len(macArray):
                        break
                    else:
                        with Listener(on_press=cancelar) as listener:
                            listener.join()
                messagebox.showinfo("OK", "Os MAC's foram colados com sucesso")
                showMainFrame(paste_frame)  # Retornar ao frame principal
                return False
            
            if key == Key.page_down:
                # Bloquear Mouse
                original_position = pyautogui.position()
                pyautogui.FAILSAFE = False
                pyautogui.moveTo(-100, -100)
                mouse_listener = pynput.mouse.Listener(suppress=True)
                mouse_listener.start()

                for i in range(len(macArray)):
                    pyperclip.copy(macArray[i])
                    time.sleep(0.2)
                    pyautogui.hotkey('ctrl', 'v')
                    pyautogui.hotkey('enter')

                # Desbloquear mouse
                mouse_listener.stop()
                pyautogui.moveTo(original_position)
                pyautogui.FAILSAFE = True
                messagebox.showinfo("OK", "Os MAC's foram colados com sucesso")
                showMainFrame(paste_frame)  # Retornar ao frame principal
                return False

            if key == Key.delete:
                return False

        def start_listener():
            global keyboard_listener
            keyboard_listener = Listener(on_press=keyFunction)
            keyboard_listener.start()
            keyboard_listener.join()

        # Adicionar logo
        logo_path = "assets/img/logosolutecadmin.png"
        logo = Image.open(logo_path)

        # Redimensionar a imagem mantendo a proporção
        max_size = (150, 100)
        logo.thumbnail(max_size, Image.LANCZOS)

        ctk_logo = ctk.CTkImage(logo, size=logo.size)

        logo_label = ctk.CTkLabel(frame, image=ctk_logo, text="")
        logo_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="news")  # Centralizar o logo

        # Frame para rótulo e entrada de texto
        macEntry_Frame = ctk.CTkFrame(frame, fg_color="transparent")
        macEntry_Frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        # Rótulo para "Digite o MAC:"
        mac_label = ctk.CTkLabel(macEntry_Frame, text="Digite o MAC:", padx=10, pady=10)
        mac_label.grid(row=0, column=0, sticky="e")  # Alinhar à direita

        # Entrada de texto
        macEntry = ctk.CTkEntry(macEntry_Frame, placeholder_text="Ex.: 22:AA:44:GD:21:45", width=200)
        macEntry.grid(row=0, column=1, padx=10, sticky="we")  # Centralizar na coluna 1

        # Adiciona o mac da caixa de entrada ao apertar ENTER
        macEntry.bind("<Return>", sendMac)

        # Adiciona os MAC's copiados
        maclist_label = ctk.CTkLabel(frame, text="Lista de Mac's:", font=("Arial", 18))
        maclist_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")  # Centralizar na tela

        # Caixa com a Lista de MAC's com barra de rolagem
        macDisplayFrame = ctk.CTkScrollableFrame(frame, width=250, height=50)
        macDisplayFrame.grid(row=3, column=0, columnspan=2, padx=10, pady=5)  # Centralizar na tela

        # Texto de total de MAC's registrados
        macTotalRegister_label = ctk.CTkLabel(frame, text=f"Mac's registrados: {len(macArray)}")
        macTotalRegister_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")  # Centralizar na tela

        # Botão de abrir outro frame para colar mac's
        paste_button = ctk.CTkButton(frame, text="Colar Mac's", height=40, command=showPasteMacFrame)
        paste_button.grid(row=5, column=0, padx=10, pady=5, sticky="e")  # Alinhar à direita

        # Botão de abrir outro frame para gerenciar cpe's
        manageCpe_button = ctk.CTkButton(frame, text="Gerenciar CPE's ", height=40, command=show_login_frame)
        manageCpe_button.grid(row=5, column=1, padx=10, pady=5, sticky="w")  # Alinhar à esquerda

        # Texto de versão
        version_label = ctk.CTkLabel(frame, text_color="gray", text=f"Versão: {version}")
        version_label.grid(row=6, column=1, padx=5, sticky="e")  # Alinhar à direita

        # Definir o foco para macEntry após a GUI ser carregada
        root.after(100, lambda: macEntry.focus_set())

        # Iniciando a janela principal
        root.mainloop()

def show_login_frame():
    login_window = LoginFrame()
    login_window.grab_set()  # Faz a janela de login modal (foco exclusivo)

if __name__ == "__main__":
    try:
        Main.main()
    except Exception as e:
        print(e)
        messagebox.showerror("Erro", f"Houve um erro! {e}")