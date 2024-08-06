import customtkinter as ctk
import requests
import threading
from PIL import Image, ImageTk
from tkinter import messagebox
from CTkToolTip import *
from config import config
from configcpe import ConfigCPE

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
        self.geometry("800x600")  # Aumentar o tamanho da janela
        #self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", close)

        # Centralizar a janela na tela
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Frame principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        self.after(250, lambda: self.iconbitmap('icon.ico')) # Corrige bug do icon atrasando

        # Rótulo de título
        self.title_label = ctk.CTkLabel(self.main_frame, text="Gerenciar CPE's", font=("Arial", 20))
        self.title_label.pack(pady=20)

        # Frame para a tabela
        self.table_frame = ctk.CTkScrollableFrame(self.main_frame, width=550, height=250)
        self.table_frame.pack(pady=10, fill="both", expand=True)

        # Cabeçalho da tabela
        self.headers = ["", "Tipo de CPE", "Conexão", "Online/Offline", "MAC", "IPv6", "Versão Firmware", "License", ""]
        self.header_labels = []
        for col, header in enumerate(self.headers):
            header_label = ctk.CTkLabel(self.table_frame, text=header, font=("Arial", 12, "bold"))
            header_label.grid(row=0, column=col, padx=10, pady=5, sticky="ew")
            self.header_labels.append(header_label)

        # Frame para os botões
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(side="bottom", fill="x", pady=10)

        # Configurar o grid da button_frame
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)

        # Radio buttons
        self.radio_value = ctk.StringVar(value="none")  # Para controlar o estado dos radio buttons
        self.previous_value = "none"

        # Carregar as imagens para os botões de rádio
        self.block_icon = ImageTk.PhotoImage(Image.open("assets/img/lock-solid.png").resize((15, 15), Image.LANCZOS))
        self.unblock_icon = ImageTk.PhotoImage(Image.open("assets/img/lock-open-solid.png").resize((14, 15), Image.LANCZOS))
        self.delete_icon = ImageTk.PhotoImage(Image.open("assets/img/trash-solid-red.png").resize((14, 15), Image.LANCZOS))

        self.block_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.block_frame.grid(row=0, column=0, padx=5, pady=5)
        self.block_icon_label = ctk.CTkLabel(self.block_frame, image=self.block_icon, text="", width=30)
        self.block_icon_label.pack(side="left")
        self.block_license_rb = ctk.CTkRadioButton(self.block_frame, text="Bloquear Licenças", variable=self.radio_value, value="block", command=self.toggle_radio)
        self.block_license_rb.pack(side="left")

        self.unblock_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent",)
        self.unblock_frame.grid(row=0, column=1, padx=5, pady=5)
        self.unblock_icon_label = ctk.CTkLabel(self.unblock_frame, image=self.unblock_icon, text="", width=30)
        self.unblock_icon_label.pack(side="left")
        self.unblock_license_rb = ctk.CTkRadioButton(self.unblock_frame, text="Desbloquear Licenças", variable=self.radio_value, value="unblock", command=self.toggle_radio)
        self.unblock_license_rb.pack(side="left")

        self.delete_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent",)
        self.delete_frame.grid(row=0, column=2, padx=5, pady=5)
        self.delete_rb = ctk.CTkButton(self.delete_frame, text="Excluir CPE", fg_color="#c0392b", hover_color="#e74c3c", command=self.delete_selected_cpes)
        self.delete_rb.pack(side="left")

        # Botão de Atualizar
        self.update_button = ctk.CTkButton(self.button_frame, text="Atualizar", command=self.update_data)
        self.update_button.grid(row=1, column=0, padx=5, pady=5)

        # Botão de fechar
        close_button = ctk.CTkButton(self.button_frame, text="Fechar", command=self.on_close)
        close_button.grid(row=1, column=1, padx=5, pady=5)

        # Botão de salvar configurações
        self.save_button = ctk.CTkButton(self.button_frame, text="Salvar configurações", command=self.save_settings, state="disabled")
        self.save_button.grid(row=1, column=2, padx=5, pady=5)
        self.toolSaveButton = CTkToolTip(self.save_button, message="Selecione uma opção para salvar as configuração.")

        # Carregar dados
        self.update_data()

    def toggle_radio(self):
        current_value = self.radio_value.get()
        if current_value == self.previous_value:
            # Desmarca o botão se for igual ao valor anterior e define a variável como vazia
            self.radio_value.set("")
            self.previous_value = ""
            self.save_button.configure(state="disabled")  # Desativa o botão "Salvar configurações"
        else:
            # Atualiza o valor anterior para o valor atual
            self.previous_value = current_value
            self.save_button.configure(state="normal")  # Desativa o botão "Salvar configurações"

        # Atualiza a visibilidade do tooltip com base no estado do botão
        if self.save_button.cget("state") == "disabled":
            self.toolSaveButton.show()  # Mostrar o tooltip
        else:
            self.toolSaveButton.hide()  # Esconder o tooltip

        
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
        disableCheckbox = False

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
                    disableCheckbox = True
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
                    disableCheckbox = True
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
                    elif ipv6Status == 0:
                        ipv6Status = "IPv4"
                    else:
                        ipv6Status = "N/A"

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
        self.update_button.configure(state="normal")
        self.after(0, self.display_data)


    def display_data(self):
        
        self.checkbox_vars = []

        # Ocultar o texto de carregamento e exibir a tabela
        self.loading_frame.destroy()
        self.table_frame.pack(pady=10, fill="both", expand=True)
        self.select_all_var = ctk.IntVar()
        select_all_checkbox = ctk.CTkCheckBox(self.table_frame, text="", variable=self.select_all_var, command=self.toggle_select_all, width = 3)
        select_all_checkbox.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Atualizar a tabela com os dados armazenados
        for row_data in self.data_to_display:
            row, mac, cpe_type, conection_type, statusPath, wStatus, hStatus, ipv6Status, firmware_version, licensePath, wLicense, hLicense = row_data

            checkbox_var = ctk.IntVar()
            self.checkbox_vars.append(checkbox_var)
            checkbox = ctk.CTkCheckBox(self.table_frame, text="", variable=checkbox_var,  width = 3)
            checkbox.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            
            if cpe_type:
                cpe_type_label = ctk.CTkLabel(self.table_frame, text=cpe_type, font=("Arial", 12, "bold"), fg_color="#4db6ac", corner_radius=5, text_color="white", width=70, height=20)
                cpe_type_label.grid(row=row, column=1, padx=10, pady=5)
            else:
                cpe_type_label = ctk.CTkLabel(self.table_frame, text="Não encontrado", font=("Arial", 12, "bold"), fg_color="#e67e22", corner_radius=5, text_color="white", width=70, height=20)
                cpe_type_label.grid(row=row, column=1, padx=10, pady=5)
            
            if conection_type:
                conection_type_label = ctk.CTkLabel(self.table_frame, text=conection_type, font=("Arial", 11, "bold"), fg_color="#4db6ac", corner_radius=5, text_color="white", width=50, height=20)
                conection_type_label.grid(row=row, column=2, padx=10, pady=5)
            else:
                conection_type_label = ctk.CTkLabel(self.table_frame, text="?", font=("Arial", 11, "bold"), fg_color="#e67e22", corner_radius=5, text_color="white", width=50, height=20)
                conection_type_label.grid(row=row, column=2, padx=10, pady=5)

            online_label = ctk.CTkLabel(self.table_frame, image=self.showIcon(statusPath, wStatus, hStatus), text="")
            online_label.grid(row=row, column=3, padx=10, pady=5, sticky="ew")

            mac_label = ctk.CTkLabel(self.table_frame, text=mac, font=("Arial", 12))
            mac_label.grid(row=row, column=4, padx=10, pady=5, sticky="ew")

            ipv6_label = ctk.CTkLabel(self.table_frame, text=ipv6Status, font=("Arial", 12))
            ipv6_label.grid(row=row, column=5, padx=10, pady=5, sticky="ew")

            firmware_label = ctk.CTkLabel(self.table_frame, text=firmware_version, font=("Arial", 12))
            firmware_label.grid(row=row, column=6, padx=10, pady=5, sticky="ew")

            license_label = ctk.CTkLabel(self.table_frame, image=self.showIcon(licensePath, wLicense, hLicense), text="")
            license_label.grid(row=row, column=7, padx=10, pady=5, sticky="ew")

            self.config_image = ctk.CTkImage(light_image=Image.open("assets/img/gear-solid-dark.png"), dark_image=Image.open("assets/img/gear-solid-dark.png"), size=(15, 15)) # Carregar a imagem para o botão
            config_button = ctk.CTkButton(self.table_frame, image=self.config_image, text="", font=("Arial", 12), width= 30, fg_color="transparent", command=lambda mac=mac: self.open_config_cpe(mac))
            config_button.grid(row=row, column=8, padx=10, pady=5, sticky="ew")
            CTkToolTip(config_button, message="Ir para as configurações do CPE.")

            self.reset_image = ctk.CTkImage(light_image=Image.open("assets/img/rotate-right-solid-dark.png"), dark_image=Image.open("assets/img/rotate-right-solid-dark.png"), size=(15, 15)) # Carregar a imagem para o botão
            reset_button = ctk.CTkButton(self.table_frame, image=self.reset_image, text="", font=("Arial", 12), width= 30, fg_color="transparent", command=lambda mac=mac: self.firmware_reset(mac))
            reset_button.grid(row=row, column=9, padx=10, pady=5, sticky="ew")
            CTkToolTip(reset_button, message="Resetar para o firmware original")

    def firmware_reset(self, mac):
     
        print(mac)

        askFirmwareUpdate = messagebox.askyesno("Atualizar Firmware", f"Você deseja resetar para o firmware original do fabricante?'")
        if askFirmwareUpdate:    

            response = requests.put(f'https://flashman.gigalink.net.br/api/v2/device/command/{mac}/upstatus', auth=(config.credentials["username"], config.credentials["password"])) # Faz uma requisição para verificar se o CPE está online antes de atualizar.
            status = response.json().get("success")
            if status == True:
                payloadFirmware = { 'do_update': 'true' }
                responseFirmware = requests.put(f'https://flashman.gigalink.net.br/api/v2/device/update/{mac}/9999-aix', auth=(config.credentials["username"], config.credentials["password"]), json=payloadFirmware)
                if responseFirmware.json().get("success") == False:
                    messagebox.showerror("Erro", f"Não foi possível atualizar o firmware do CPE: {mac}\n{response.json().get("message")}")
                else:
                    messagebox.showinfo("OK", f"O firmware do CPE: {mac} está sendo resetado.\nNão desligue ou desconecte o CPE da rede antes do mesmo reiniciar.")  
            else:
                messagebox.showerror("Erro", "O CPE não está online!")

    def open_config_cpe(self, mac):
        ConfigCPE(master=self, mac=mac)

        # Reabilitar o botão de atualização
        self.enable_update_button()

    def toggle_select_all(self):
        for checkbox_var in self.checkbox_vars:
            checkbox_var.set(self.select_all_var.get())

    def showIcon(self, iconPath, width, height):
        license_image = Image.open(iconPath)
        license_image = license_image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(license_image)

    def enable_update_button(self):
        self.update_button.configure(state="normal")

    def delete_selected_cpes(self):
        selected_macs = [mac for i, mac in enumerate(self.mac_array) if self.checkbox_vars[i].get() == 1]
    
        if not selected_macs:
            messagebox.showinfo("Informação", "Nenhum CPE selecionado para exclusão.")
            return
        askDelete = messagebox.askyesno("Deletar CPE's", f"Deseja deletar os CPE's selecionados? {selected_macs}", default=messagebox.NO)
        if askDelete:
            def delete_cpe(mac):
                url = f"https://flashman.gigalink.net.br/api/v2/device/delete/{mac}"
                try:
                    response = requests.delete(url, auth=(config.credentials["username"], config.credentials["password"]))
                    response.raise_for_status()
                    print(mac)
                    messagebox.showinfo("Sucesso", f"CPE {mac} excluído com sucesso.")
                except requests.RequestException as e:
                    messagebox.showerror("Erro", f"Erro ao excluir CPE {mac}: {e}")

        for mac in selected_macs:
            threading.Thread(target=delete_cpe, args=(mac,)).start()


    def save_settings(self):
        selected_action = self.radio_value.get()
        selected_macs = [self.mac_array[idx] for idx, var in enumerate(self.checkbox_vars) if var.get() == 1]
        payload = {
            'ids': selected_macs,
            'block': True if selected_action == "block" else False
        }
        response = requests.put("https://flashman.gigalink.net.br/api/v2/device/license/set", auth=(config.credentials["username"], config.credentials["password"]), json=payload)
        if response.status_code == 200:
            self.update_data()
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        else:
            messagebox.showinfo("Erro", "Falha ao salvar configurações.")

    def on_close(self):
        self.destroy()
        self.master.deiconify()  # Restaurar o frame principal

# Teste da aplicação
if __name__ == "__main__":
    root = ctk.CTk()
    root.iconbitmap("icon.ico")  # Certifique-se de que o caminho está correto e o formato do ícone está correto
    mac_list = ["0C:80:63:09:5A:8A", "MAC2", "MAC3"]  # Substitua com a lista real de MACs
    app = GerenciarCPE(master=root, mac_array=mac_list)
    app.mainloop()
