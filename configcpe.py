import customtkinter as ctk
import requests
import threading
import json
from config import config
from tkinter import messagebox
from PIL import Image, ImageTk

class ConfigCPE(ctk.CTkToplevel):
    def __init__(self, master=None, mac=None):  
        
        super().__init__(master)
        self.title("Configurações do CPE")
        self.geometry("900x400")
        self.minsize(900, 400)
        self.after(250, lambda: self.iconbitmap('icon.ico'))  # Corrige bug do ícone atrasando

        self.mac = mac

        # Carregar imagens:
        self.online_image = ImageTk.PhotoImage(Image.open("assets/img/circle-solid-green.png").resize((15, 15), Image.LANCZOS))

        # Frame principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        # Adicione widgets conforme necessário para a configuração
        self.label = ctk.CTkLabel(self.main_frame, text="Configurações do CPE", font=("Arial", 16))
        self.label.pack(pady=20)

        # Frame para os botões
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(side="bottom", fill="x", pady=10)

        # Configurar o grid da button_frame
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)

        # Botão de Atualizar
        self.update_button = ctk.CTkButton(self.button_frame, text="Atualizar", command=self.update_data)
        self.update_button.grid(row=1, column=0, padx=5, pady=5)

        # Botão de fechar
        close_button = ctk.CTkButton(self.button_frame, text="Fechar", command=self.destroy)
        close_button.grid(row=1, column=1, padx=5, pady=5)

        # Botão de salvar configurações
        self.save_button = ctk.CTkButton(self.button_frame, text="Salvar configurações", state="disabled")
        self.save_button.grid(row=1, column=2, padx=5, pady=5)

        # Frame para a tabela
        self.table_frame = ctk.CTkScrollableFrame(self.main_frame, width=550, height=250)
        self.table_frame.pack(pady=10, fill="both", expand=True)

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
        self.thread = threading.Thread(target=self.fetch_data)
        self.thread.start()

    def fetch_data(self):
        try:
            response = requests.get(f"https://flashman.gigalink.net.br/api/v2/device/update/{self.mac}", auth=(config.credentials["username"], config.credentials["password"]))
            response.raise_for_status()
            apiJson = response.json()

            # Extraindo informações
            firmware_version = apiJson.get("installed_release", "N/A")
            online_status = apiJson.get("online_status", "N/A")  # Verifica se o CPE está online
            identificador_unico = apiJson.get("_id", "N/A") # Exibe o mac do cpe
            ip_wan = apiJson.get("wan_ip", "N/A")
            ip_publico = apiJson.get("ip", "N/A")
            useTr069 = apiJson.get("use_tr069")
            operation_type = apiJson.get("bridge_mode_enabled")
            conection_type = apiJson.get("connection_type")
            mesh_mode = apiJson.get("mesh_mode")
            pppoe_user = apiJson.get("pppoe_user")
            pppoe_password= apiJson.get("pppoe_password")

            ssid_24ghz = apiJson.get("wifi_ssid")
            password_24ghz = apiJson.get("password_ssid")
            wifi_chanell_24ghz = apiJson.get("wifi_channel")

            ssid_5ghz = apiJson.get("wifi_ssid_5ghz")
            password_5ghz = apiJson.get("password_ssid_5ghz")

             # Verifica o tipo de CPE
            if useTr069 == True:
                useTr069 = "TR-069"
            elif useTr069 == False:
                useTr069 = "Firmware"
            else:
                useTr069 = None

            if online_status == True:
                online_status_label = "Online"
                online_status = ctk.CTkImage(Image.open("assets/img/circle-solid-green.png"))
            elif online_status == False:
                online_status_label = "Offline"
                online_status = ctk.CTkImage(Image.open("assets/img/circle-solid-red.png"))
            else:
                online_status_label = "N/A"
                online_status = ctk.CTkImage(Image.open("assets/img/question-solid.png"))

            # Armazenar os dados coletados
            self.data_to_display = (self.mac, online_status, identificador_unico, ip_wan, ip_publico, firmware_version, useTr069, online_status_label, operation_type, conection_type, mesh_mode, pppoe_user, pppoe_password)

        except requests.HTTPError as http_err:
            self.data_to_display = (self.mac, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")
        except Exception as err:
            self.data_to_display = (self.mac, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")

        # Atualizar a interface na thread principal
        self.after(0, self.display_data)

    def display_data(self):
        # Atualizar a tabela com os dados armazenados
        mac, online_status, identificador_unico, ip_wan, ip_publico, firmware_version, useTr069, online_status_label, operation_type, conection_type, mesh_mode, pppoe_user, pppoe_password = self.data_to_display
        # Ocultar o texto de carregamento e exibir a tabela
        self.loading_frame.destroy()
        self.table_frame.pack(pady=10, fill="both", expand=True)
        self.options = [
            firmware_version,
            "0092-gik"
        ]

        # Configurar o grid do table_frame para centralização
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(2, weight=1)
        self.table_frame.grid_columnconfigure(3, weight=1)
        self.table_frame.grid_columnconfigure(4, weight=1)
        self.table_frame.grid_columnconfigure(5, weight=1)

        # Header 1
        ctk.CTkLabel(self.table_frame, text="Infos", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Status", font=("Arial", 12, "bold")).grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Identificador Único", font=("Arial", 12, "bold")).grid(row=1, column=2, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="IP Wan", font=("Arial", 12, "bold")).grid(row=1, column=3, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="IP Público", font=("Arial", 12, "bold")).grid(row=1, column=4, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Firmware Instalado", font=("Arial", 12, "bold")).grid(row=1, column=5, padx=10, pady=5)

        # Header 2
        ctk.CTkLabel(self.table_frame, text="Modo de operação", font=("Arial", 12, "bold")).grid(row=5, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Mesh", font=("Arial", 12, "bold")).grid(row=5, column=2, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Tipo de conexão", font=("Arial", 12, "bold")).grid(row=5, column=3, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Usuário PPPoE", font=("Arial", 12, "bold")).grid(row=5, column=4, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Senha PPPoE", font=("Arial", 12, "bold")).grid(row=5, column=5, padx=10, pady=5)

        # Titulo Wi-Fi 2.4 GHz
        ctk.CTkLabel(self.table_frame, text="Wi-Fi 2.4 GHz", font=("Arial", 15, "bold")).grid(row=10, column=0, columnspan=6, padx=10, pady=10, sticky="ew")

        # Header 3
        ctk.CTkLabel(self.table_frame, text="Canal do Wi-Fi", font=("Arial", 12, "bold")).grid(row=11, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Largura de banda", font=("Arial", 12, "bold")).grid(row=11, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Modo de operação", font=("Arial", 12, "bold")).grid(row=11, column=2, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="SSID do Wi-Fi", font=("Arial", 12, "bold")).grid(row=11, column=3, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Senha do Wi-Fi", font=("Arial", 12, "bold")).grid(row=11, column=4, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Potência do sinal", font=("Arial", 12, "bold")).grid(row=11, column=5, padx=10, pady=5)

        # Header 4
        ctk.CTkLabel(self.table_frame, text="Canal do Wi-Fi", font=("Arial", 12, "bold")).grid(row=14, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Largura de banda", font=("Arial", 12, "bold")).grid(row=14, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Modo de operação", font=("Arial", 12, "bold")).grid(row=14, column=2, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="SSID do Wi-Fi", font=("Arial", 12, "bold")).grid(row=14, column=3, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Senha do Wi-Fi", font=("Arial", 12, "bold")).grid(row=14, column=4, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Potência do sinal", font=("Arial", 12, "bold")).grid(row=14, column=5, padx=10, pady=5)
        
        # Dados Header 1
        ctk.CTkLabel(self.table_frame, text=useTr069, font=("Arial", 11, "bold"), fg_color="#4db6ac", corner_radius=5, text_color="white", width=65, height=20).grid(row=4, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Mesh", font=("Arial", 11, "bold"), fg_color="#4db6ac", corner_radius=5, text_color="white", width=65, height=20).grid(row=5, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text=online_status_label, compound="left", image=online_status, font=("Arial", 12), padx=5).grid(row=4, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text=identificador_unico, font=("Arial", 12)).grid(row=4, column=2, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text=ip_wan, font=("Arial", 12)).grid(row=4, column=3, padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text=ip_publico, font=("Arial", 12)).grid(row=4, column=4, padx=10, pady=5)
        self.previous_option = firmware_version
        self.firmware_menu = ctk.CTkOptionMenu(self.table_frame, values=self.options, width=100, height=20, command=self.firmware_update)
        self.firmware_menu.grid(row=4, column=5, padx=10, pady=5)

        # Dados Header 2
        self.operation_type_menu = ctk.CTkOptionMenu(self.table_frame, values=["Modo Roteador", "Modo Bridge / AP"], command=self.update_entry_state, width=100, height=20)
        self.operation_type_menu.grid(row=6, column=1, padx=10, pady=5)

        self.mesh_mode_menu = ctk.CTkOptionMenu(self.table_frame, values=["Desabilitado", "Cabo", "Cabo e Wi-Fi 2.4 GHz", "Cabo e Wi-Fi 5 GHz", "Cabo e ambos Wi-Fi"], width=150, height=20)
        self.mesh_mode_menu.grid(row=6, column=2, padx=10, pady=5)

        self.connection_type_menu = ctk.CTkOptionMenu(self.table_frame, values=["PPPoE", "DHCP"], width=100, height=20)
        self.connection_type_menu.grid(row=6, column=3, padx=10, pady=5)

        self.pppoe_user_entry = ctk.CTkEntry(self.table_frame)
        self.pppoe_user_entry.insert(0, pppoe_user)
        self.pppoe_user_entry.grid(row=6, column=4, padx=10, pady=5)

        self.pppoe_password_entry = ctk.CTkEntry(self.table_frame)
        self.pppoe_password_entry.insert(0, pppoe_password)
        self.pppoe_password_entry.grid(row=6, column=5, padx=10, pady=5)

        # Dados Header 3
        self.wifi_channel_2_4 = ctk.CTkOptionMenu(self.table_frame, values=["Auto", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"], width=100, height=20)
        self.wifi_channel_2_4.grid(row=12, column=0, padx=10, pady=5)

        self.bandwidth_2_4 = ctk.CTkOptionMenu(self.table_frame, values=["Auto", "20MHz", "40MHz"], width=100, height=20)
        self.bandwidth_2_4.grid(row=12, column=1, padx=10, pady=5)

        self.operation_mode_2_4 = ctk.CTkOptionMenu(self.table_frame, values=["BGN", "G"], width=100, height=20)
        self.operation_mode_2_4.grid(row=12, column=2, padx=10, pady=5)

        self.ssid_entry_2_4 = ctk.CTkEntry(self.table_frame)
        self.ssid_entry_2_4.grid(row=12, column=3, padx=10, pady=5)

        self.password_entry_2_4 = ctk.CTkEntry(self.table_frame)
        self.password_entry_2_4.grid(row=12, column=4, padx=10, pady=5)

        self.signal_strength_2_4 = ctk.CTkOptionMenu(self.table_frame, values=["100%", "75%", "50%", "25%"], width=100, height=20)
        self.signal_strength_2_4.grid(row=12, column=5, padx=10, pady=5)

        # Dados Header 4
        self.wifi_channel_5 = ctk.CTkOptionMenu(self.table_frame, values=["Auto", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"], width=100, height=20)
        self.wifi_channel_5.grid(row=15, column=0, padx=10, pady=5)

        self.bandwidth_5 = ctk.CTkOptionMenu(self.table_frame, values=["Auto", "20MHz", "40MHz"], width=100, height=20)
        self.bandwidth_5.grid(row=15, column=1, padx=10, pady=5)

        self.operation_mode_5 = ctk.CTkOptionMenu(self.table_frame, values=["BGN", "G"], width=100, height=20)
        self.operation_mode_5.grid(row=15, column=2, padx=10, pady=5)

        self.ssid_entry_5 = ctk.CTkEntry(self.table_frame)
        self.ssid_entry_5.grid(row=15, column=3, padx=10, pady=5)

        self.password_entry_5 = ctk.CTkEntry(self.table_frame)
        self.password_entry_5.grid(row=15, column=4, padx=10, pady=5)

        self.signal_strength_5 = ctk.CTkOptionMenu(self.table_frame, values=["100%", "75%", "50%", "25%"], width=100, height=20)
        self.signal_strength_5.grid(row=15, column=5, padx=10, pady=5)

        # Titulo Wi-Fi 5 GHz
        ctk.CTkLabel(self.table_frame, text="Wi-Fi 5 GHz", font=("Arial", 15, "bold")).grid(row=13, column=0, columnspan=6, padx=10, pady=10, sticky="ew")

        # Logica Header 2
        # Muda a opção do Menu referente ao tipo de conexão
        if operation_type == False:
            self.operation_type_menu.set("Modo Roteador")
        elif operation_type == True:
            self.operation_type_menu.set("Modo Bridge / AP")
            self.pppoe_user_entry.configure(state="disabled")
            self.pppoe_password_entry.configure(state="disabled")
            self.connection_type_menu.configure(state="disabled")

        # Muda a opção do Menu referente ao tipo de conexão
        if conection_type == "dhcp":
            self.connection_type_menu.set("DHCP")
        elif conection_type == "pppoe":
            self.connection_type_menu.set("PPPoE")

        # Muda a opção do Menu referente ao tipo de mesh
        if mesh_mode == 0:
            self.mesh_mode_menu.set("Desabilitado")
        elif mesh_mode == 1:
            self.mesh_mode_menu.set("Cabo")
        elif mesh_mode == 2:
            self.mesh_mode_menu.set("Cabo e Wi-Fi 2.4 GHz")
        elif mesh_mode == 3:
            self.mesh_mode_menu.set("Cabo e Wi-Fi 5 GHz")
        elif mesh_mode == 4:
            self.mesh_mode_menu.set("Cabo e ambos Wi-Fi")

        # Desativar o optionmenu se useTr069 for True
        if useTr069 == "TR-069":
            self.firmware_menu.configure(state="disabled")

        # Reativar o botão de atualização
        self.update_button.configure(state="normal")

    def update_entry_state(self, selected_value=None):
        operation_type = self.operation_type_menu.get()
        if operation_type == "Modo Roteador":
            self.pppoe_user_entry.configure(state="normal")
            self.pppoe_password_entry.configure(state="normal")
            self.connection_type_menu.configure(state="normal")
        else:  # "Modo Bridge / AP"
            self.pppoe_user_entry.configure(state="disabled")
            self.pppoe_password_entry.configure(state="disabled")
            self.connection_type_menu.configure(state="disabled")

    def firmware_update(self, selected_option):
        if selected_option == self.previous_option:
            return

        askFirmwareUpdate = messagebox.askyesno("Atualizar Firmware", f"Você deseja atualizar a versão do firmware para '{selected_option}?'")
        if askFirmwareUpdate:    
            print(f"Opção selecionada: {selected_option}")

            response = requests.put(f'https://flashman.gigalink.net.br/api/v2/device/command/{mac}/upstatus', auth=(config.credentials["username"], config.credentials["password"])) # Faz uma requisição para verificar se o CPE está online antes de atualizar.
            status = response.json().get("success")
            if status == True:
                payloadFirmware = { 'do_update': 'true' }
                responseFirmware = requests.put(f'https://flashman.gigalink.net.br/api/v2/device/update/{mac}/{selected_option}', auth=(config.credentials["username"], config.credentials["password"]), json=payloadFirmware)
                if responseFirmware.json().get("success") == False:
                    messagebox.showerror("Erro", f"Não foi possível atualizar o firmware do CPE: {mac}\n{response.json().get("message")}")
                else:
                    messagebox.showinfo("OK", f"O firmware do CPE: {mac} está sendo atualizado para: {selected_option}\nNão desligue ou desconecte o CPE da rede antes do mesmo reiniciar.")  
            else:
                messagebox.showerror("Erro", "O CPE não está online!")

            self.previous_option = selected_option
        else:
            self.firmware_menu.set(self.previous_option)

# Supondo que você crie uma instância desta classe no arquivo principal
if __name__ == "__main__":
    root = ctk.CTk()
    mac = "0C:80:63:2B:48:96"  # Exemplo de MAC
    app = ConfigCPE(root, mac)
    app.mainloop()
