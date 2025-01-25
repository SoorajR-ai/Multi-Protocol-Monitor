import threading
import socket
import serial
import customtkinter as ctk
import datetime

class MultiProtocolMonitor:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = root
        self.root.title("Multi-Protocol Monitor")
        self.root.geometry("800x600")

        # Frame for settings
        self.settings_frame = ctk.CTkFrame(root)
        self.settings_frame.pack(pady=10, padx=10, fill="x")

        # Communication mode selection
        self.mode = ctk.StringVar(value="Serial")
        ctk.CTkLabel(self.settings_frame, text="Mode:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.mode_menu = ctk.CTkOptionMenu(self.settings_frame, variable=self.mode, values=["Serial", "UDP", "TCP"], command=self.update_options)
        self.mode_menu.grid(row=0, column=1, padx=5, pady=5)

        # Serial settings
        self.serial_port = ctk.StringVar()
        self.baud_rate = ctk.IntVar(value=9600)
        self.serial_ports = self.get_serial_ports()

        self.serial_port_menu = ctk.CTkOptionMenu(self.settings_frame, variable=self.serial_port, values=self.serial_ports)
        self.baud_rate_entry = ctk.CTkEntry(self.settings_frame, textvariable=self.baud_rate)

        # UDP/TCP settings
        self.ip_address = ctk.StringVar(value="127.0.0.1")
        self.port = ctk.IntVar(value=12345)

        self.ip_entry = ctk.CTkEntry(self.settings_frame, textvariable=self.ip_address)
        self.port_entry = ctk.CTkEntry(self.settings_frame, textvariable=self.port)

        # Control buttons
        self.start_button = ctk.CTkButton(root, text="Start", command=self.start_monitor)
        self.start_button.pack(pady=5)
        self.stop_button = ctk.CTkButton(root, text="Stop", command=self.stop_monitor, state="disabled")
        self.stop_button.pack(pady=5)

        # Terminal-like output
        self.output_frame = ctk.CTkFrame(root)
        self.output_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.output = ctk.CTkTextbox(self.output_frame, wrap="word", font=("Consolas", 12), fg_color="black", text_color="green")
        self.output.pack(fill="both", expand=True, padx=5, pady=5)

        # Additional controls for terminal
        self.clear_button = ctk.CTkButton(self.output_frame, text="Clear", command=self.clear_output)
        self.clear_button.pack(side="left", padx=5, pady=5)
        self.log_button = ctk.CTkButton(self.output_frame, text="Log to File", command=self.log_to_file)
        self.log_button.pack(side="right", padx=5, pady=5)

        # Hex View Toggle
        self.hex_view = ctk.BooleanVar(value=False)
        self.hex_toggle = ctk.CTkCheckBox(self.output_frame, text="Hex View", variable=self.hex_view)
        self.hex_toggle.pack(side="left", padx=5, pady=5)

        # Command input
        self.command_frame = ctk.CTkFrame(root)
        self.command_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.command_frame, text="Command:").pack(side="left", padx=5)
        self.command_entry = ctk.CTkEntry(self.command_frame, width=400)
        self.command_entry.pack(side="left", padx=5)
        self.send_button = ctk.CTkButton(self.command_frame, text="Send", command=self.send_command)
        self.send_button.pack(side="left", padx=5)

        # Internal variables
        self.running = False
        self.listener_thread = None
        self.connection = None

        self.update_options()

    def get_serial_ports(self):
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except ImportError:
            return []

    def update_options(self, *args):
        mode = self.mode.get()
        for widget in self.settings_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.grid_forget()

        if mode == "Serial":
            self.serial_ports = self.get_serial_ports()
            self.serial_port_menu.configure(values=self.serial_ports)
            ctk.CTkLabel(self.settings_frame, text="Serial Port:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            self.serial_port_menu.grid(row=1, column=1, padx=5, pady=5)
            ctk.CTkLabel(self.settings_frame, text="Baud Rate:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            self.baud_rate_entry.grid(row=2, column=1, padx=5, pady=5)
        elif mode in ["UDP", "TCP"]:
            ctk.CTkLabel(self.settings_frame, text="IP Address:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            self.ip_entry.grid(row=1, column=1, padx=5, pady=5)
            ctk.CTkLabel(self.settings_frame, text="Port:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            self.port_entry.grid(row=2, column=1, padx=5, pady=5)

    def start_monitor(self):
        self.running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        mode = self.mode.get()
        if mode == "Serial":
            self.listener_thread = threading.Thread(target=self.serial_monitor, daemon=True)
        elif mode == "UDP":
            self.listener_thread = threading.Thread(target=self.udp_monitor, daemon=True)
        elif mode == "TCP":
            self.listener_thread = threading.Thread(target=self.tcp_monitor, daemon=True)

        self.listener_thread.start()

    def stop_monitor(self):
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        if self.connection:
            self.connection.close()
        self.connection = None

    def append_output(self, message):
        if self.hex_view.get():
            message = " ".join(f"{ord(char):02X}" for char in message)
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
        self.output.insert("end", timestamp + message + "\n")
        self.output.see("end")

    def clear_output(self):
        self.output.delete("1.0", "end")

    def log_to_file(self):
        with open("monitor_log.txt", "a") as log_file:
            log_file.write(self.output.get("1.0", "end"))
        self.append_output("Log saved to monitor_log.txt")

    def send_command(self):
        command = self.command_entry.get()
        if self.connection and command:
            try:
                if isinstance(self.connection, serial.Serial):
                    self.connection.write(command.encode())
                else:
                    self.connection.sendall(command.encode())
                self.append_output(f"Sent: {command}")
            except Exception as e:
                self.append_output(f"Error sending command: {e}")

    def serial_monitor(self):
        try:
            self.connection = serial.Serial(self.serial_port.get(), self.baud_rate.get(), timeout=1)
            self.append_output("Serial connection established.")
            while self.running:
                if self.connection.in_waiting > 0:
                    data = self.connection.read(self.connection.in_waiting).decode(errors="ignore")
                    self.append_output(data)
        except Exception as e:
            self.append_output(f"Error: {e}")

    def udp_monitor(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.connection.bind((self.ip_address.get(), self.port.get()))
            self.append_output("UDP listener started.")
            while self.running:
                data, addr = self.connection.recvfrom(1024)
                self.append_output(f"[{addr}] {data.decode(errors='ignore')}")
        except Exception as e:
            self.append_output(f"Error: {e}")

    def tcp_monitor(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.ip_address.get(), self.port.get()))
            server.listen(1)
            self.append_output("TCP server started. Waiting for connection...")

            self.connection, addr = server.accept()
            self.append_output(f"Connected to {addr}")

            while self.running:
                data = self.connection.recv(1024)
                if not data:
                    break
                self.append_output(data.decode(errors="ignore"))
        except Exception as e:
            self.append_output(f"Error: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = MultiProtocolMonitor(root)
    root.mainloop()
