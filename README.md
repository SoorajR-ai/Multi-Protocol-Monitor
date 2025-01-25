# Multi-Protocol Monitor

A versatile tool for monitoring **Serial**, **UDP**, and **TCP** communication in real-time with an intuitive GUI built using **customtkinter**.

## Features

- **Real-time monitoring** for Serial, UDP, and TCP protocols.
- **Hex view** support for easier analysis of raw data.
- **Log to file** and terminal-like output display for review and record-keeping.
- **Command input** support for sending data over communication channels.
- **Cross-platform support** (works on Windows, macOS, and Linux).
  
## Installation

To get started with this project, follow these installation steps:

1. Clone the repository:
    ```bash
    https://github.com/SoorajR-ai/Multi-Protocol-Monitor.git
    ```
2. Navigate into the project directory:
    ```bash
    cd Multi-Protocol-Monitor
    ```
3. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the application:
    ```bash
    python main.py
    ```

## Usage

1. **Select a communication mode** (Serial/UDP/TCP) from the dropdown menu.
2. Configure the communication settings:
   - For **Serial** mode, select a serial port and baud rate.
   - For **UDP** or **TCP** modes, enter the IP address and port number.
3. Use the **Start** button to begin monitoring and the **Stop** button to end the session.
4. The **Terminal** section displays incoming data and allows sending commands.
5. **Hex view** can be toggled for raw data visualization.

## Contributing

Contributions are welcome! If you'd like to help improve this project, please fork the repository, create a new branch, and submit a pull request. For bug reports or suggestions, open an issue on GitHub.
