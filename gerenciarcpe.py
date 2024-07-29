import customtkinter as ctk
import requests
import threading
from PIL import Image, ImageTk
from config import config

class GerenciarCPE(ctk.CTkToplevel):
    def __init__(self, master=None, mac_array=None):
        self.mac_array = mac_array if mac_array else []
        self.master = master  # Salva a referência da janela principal
        self.master.withdraw()
        
        def close():
            self.master.deiconify()
            self.destroy()

        super().__init__(master)
        self.title("Gerenciar CPE's")
        self.geometry("600x400")  # Aumentar o tamanho da janela
        #self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", close)

        # Centralizar a janela na tela
        window_width = 600
        window_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Frame principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        # Rótulo de título
        self.title_label = ctk.CTkLabel(self.main_frame, text="Gerenciar CPE's", font=("Arial", 20))
        self.title_label.pack(pady=20)

        # Frame para a tabela
        self.table_frame = ctk.CTkScrollableFrame(self.main_frame, width=550, height=250)
        self.table_frame.pack(pady=10, fill="both", expand=True)

        # Cabeçalho da tabela
        self.headers = ["Tipo de CPE", "Conexão", "Online/Offline", "MAC", "IPv6", "Versão Firmware", "License"]
        self.header_labels = []
        for col, header in enumerate(self.headers):
            header_label = ctk.CTkLabel(self.table_frame, text=header, font=("Arial", 12, "bold"))
            header_label.grid(row=0, column=col, padx=10, pady=5, sticky="ew")
            self.header_labels.append(header_label)

        # Frame para os botões
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(side="bottom", fill="x", pady=10)

        # Botão de Atualizar
        self.update_button = ctk.CTkButton(self.button_frame, text="Atualizar", command=self.update_data)
        self.update_button.pack(side="left", padx=5)

        # Botão de fechar
        close_button = ctk.CTkButton(self.button_frame, text="Fechar", command=self.on_close)
        close_button.pack(side="right", padx=5)

        # Carregar dados
        self.update_data()

    def update_data(self):
        # Bloquear o botão de atualização
        self.update_button.configure(state="disabled")

        # Ocultar a tabela e exibir o texto de carregamento
        self.table_frame.pack_forget()
        self.loading_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.loading_frame.pack(pady=10, fill="both", expand=True)
        self.loading_label = ctk.CTkLabel(self.loading_frame, text="Carregando dados...", font=("Arial", 12))
        self.loading_label.pack(expand=True)  # Centraliza vertical e horizontalmente

        # Atualizar os dados em uma nova thread
        self.data_to_display = []
        self.thread = threading.Thread(target=self.fetch_data)
        self.thread.start()

    def fetch_data(self):
        def showIcon(iconPath, width, height):
            license_image = Image.open(iconPath)
            license_image = license_image.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(license_image)

        # Coletar todos os dados antes de atualizar a interface
        for row, mac in enumerate(self.mac_array, start=1):
            try:
                response = requests.get(f"https://flashman.gigalink.net.br/api/v2/device/update/{mac}", auth=(config.credentials["username"], config.credentials["password"]))
                payloadLicense = {'id': mac}
                responseLicense = requests.put(f"https://flashman.gigalink.net.br/api/v2/device/license/get", auth=(config.credentials["username"], config.credentials["password"]), json=payloadLicense)
                exit = responseLicense.json().get("status")
                responseUP = requests.put(f"https://flashman.gigalink.net.br/api/v2/device/command/{mac}/upstatus", auth=(config.credentials["username"], config.credentials["password"]))
                
                # Verifica se o CPE está online ou offline
                status = responseUP.json().get("success")
                if status == True:
                    statusPath = "assets/img/circle-solid-green.png"
                    wStatus = 15
                    hStatus = 15
                elif status == False:
                    statusPath = "assets/img/circle-solid-red.png"
                    wStatus = 15
                    hStatus = 15
                else:
                    statusPath = "assets/img/question-solid.png"
                    wStatus = 10
                    hStatus = 15

                # Caso o cpe não exista:
                if response.status_code == 404:
                    online_status = "N/A"
                    firmware_version = "N/A"
                    license_status = "N/A"
                    ipv6Status = ""
                    conection_type = None
                    cpe_type = None
                    licensePath = "assets/img/question-solid.png"
                    wLicense = 10
                    hLicense = 15
                # Caso Exista:
                else:
                    response.raise_for_status()
                    apiJson = response.json()
                    firmware_version = apiJson.get("installed_release", "N/A")
                    is_license_active = apiJson.get("is_license_active", None)
                    useTr069 = apiJson.get("use_tr069")
                    ipv6Status = apiJson.get("ipv6_enabled")
                    conection_type = apiJson.get("connection_type")

                    if conection_type == "dhcp":
                        conection_type = "DHCP"
                    elif conection_type == "pppoe":
                        conection_type = "PPPoE"
                    else:
                        conection_type = None

                    # Verifica o tipo de CPE
                    if useTr069 == True:
                        cpe_type = "TR-069"
                    elif useTr069 == False:
                        cpe_type = "Firmware"
                    else:
                        cpe_type = None

                    # Verifica o status do IPv6            
                    if ipv6Status == 1:
                        ipv6Status = "IPv6"
                    if ipv6Status == 0:
                        ipv6Status = "IPv4"

                    # Verifca se a licença está bloqueada
                    if exit is None:
                        license_status = "N/A"
                        licensePath = "assets/img/question-solid.png"
                        wLicense = 10
                        hLicense = 15
                    elif exit:
                        license_status = "Active"
                        licensePath = "assets/img/lock-open-solid.png"
                        wLicense = 15
                        hLicense = 15
                    else:
                        license_status = "Inactive"
                        licensePath = "assets/img/lock-solid.png"
                        wLicense = 14
                        hLicense = 15

            except requests.HTTPError as http_err:
                online_status = "N/A"
                firmware_version = "N/A"
                conection_type = "N/A"
                license_status = "N/A"
                ipv6Status = ""
                cpe_type = "N/A"
                licensePath = "assets/img/question-solid.png"
                wLicense = 10
                hLicense = 15
            except Exception as err:
                online_status = "N/A"
                firmware_version = "N/A"
                conection_type = "N/A"
                license_status = "N/A"
                ipv6Status = ""
                cpe_type = "N/A"
                licensePath = "assets/img/question-solid.png"
                wLicense = 10
                hLicense = 15

            # Armazenar os dados coletados
            self.data_to_display.append((row, mac, cpe_type, conection_type, statusPath, wStatus, hStatus, ipv6Status, firmware_version, licensePath, wLicense, hLicense))

        # Atualizar a interface na thread principal
        self.after(0, self.display_data)

    def display_data(self):
        # Ocultar o texto de carregamento e exibir a tabela
        self.loading_frame.destroy()
        self.table_frame.pack(pady=10, fill="both", expand=True)

        # Atualizar a tabela com os dados armazenados
        for row_data in self.data_to_display:
            row, mac, cpe_type, conection_type, statusPath, wStatus, hStatus, ipv6Status, firmware_version, licensePath, wLicense, hLicense = row_data

            if cpe_type:
                cpe_type_label = ctk.CTkLabel(self.table_frame, text=cpe_type, font=("Arial", 12, "bold"), fg_color="#4db6ac", corner_radius=5, text_color="white", width=70, height=20)
                cpe_type_label.grid(row=row, column=0, padx=10, pady=5)
            
            if conection_type:
                conection_type_label = ctk.CTkLabel(self.table_frame, text=conection_type, font=("Arial", 11, "bold"), fg_color="#4db6ac", corner_radius=5, text_color="white", width=50, height=20)
                conection_type_label.grid(row=row, column=1, padx=10, pady=5)

            online_label = ctk.CTkLabel(self.table_frame, image=self.showIcon(statusPath, wStatus, hStatus), text="")
            online_label.grid(row=row, column=2, padx=10, pady=5, sticky="ew")

            mac_label = ctk.CTkLabel(self.table_frame, text=mac, font=("Arial", 12))
            mac_label.grid(row=row, column=3, padx=10, pady=5, sticky="ew")

            ipv6_label = ctk.CTkLabel(self.table_frame, text=ipv6Status, font=("Arial", 12))
            ipv6_label.grid(row=row, column=4, padx=10, pady=5, sticky="ew")

            firmware_label = ctk.CTkLabel(self.table_frame, text=firmware_version, font=("Arial", 12))
            firmware_label.grid(row=row, column=5, padx=10, pady=5, sticky="ew")

            license_label = ctk.CTkLabel(self.table_frame, image=self.showIcon(licensePath, wLicense, hLicense), text="")
            license_label.grid(row=row, column=6, padx=10, pady=5, sticky="ew")

        # Reabilitar o botão de atualização
        self.enable_update_button()

    def showIcon(self, iconPath, width, height):
        license_image = Image.open(iconPath)
        license_image = license_image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(license_image)

    def enable_update_button(self):
        self.update_button.configure(state="normal")

    def on_close(self):
        self.destroy()
        self.master.deiconify()  # Restaurar o frame principal

# Teste da aplicação
if __name__ == "__main__":
    root = ctk.CTk()
    root.iconbitmap("icon.ico")  # Certifique-se de que o caminho está correto e o formato do ícone está correto
    mac_list = ["MAC1", "MAC2", "MAC3"]  # Substitua com a lista real de MACs
    app = GerenciarCPE(master=root, mac_array=mac_list)
    app.mainloop()
