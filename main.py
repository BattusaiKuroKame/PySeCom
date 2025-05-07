
import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QComboBox, QMessageBox
)
from PyQt6.QtCore import QTimer


class SerialMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Terminal - PyQt6 QMainWindow")
        self.resize(600, 400)

        self.serial_port = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Serial port selection
        port_layout = QHBoxLayout()
        self.port_selector = QComboBox()
        self.refresh_ports()
        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_selector)

        self.baud_input = QLineEdit("9600")
        port_layout.addWidget(QLabel("Baud:"))
        port_layout.addWidget(self.baud_input)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        port_layout.addWidget(self.connect_button)

        layout.addLayout(port_layout)

        # Serial monitor
        self.monitor = QTextEdit()
        self.monitor.setReadOnly(True)
        layout.addWidget(self.monitor)

        # Input field
        send_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_data)
        send_layout.addWidget(self.input_line)
        send_layout.addWidget(self.send_button)

        layout.addLayout(send_layout)

        self.central_widget.setLayout(layout)

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_selector.clear()
        for port in ports:
            self.port_selector.addItem(port.device)

    def toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.timer.stop()
            self.connect_button.setText("Connect")
            self.monitor.append("Disconnected.")
        else:
            try:
                port = self.port_selector.currentText()
                baud = int(self.baud_input.text())
                self.serial_port = serial.Serial(port, baud, timeout=0.1)
                self.timer.start(100)
                self.connect_button.setText("Disconnect")
                self.monitor.append(f"Connected to {port} at {baud} baud.")
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", str(e))

    def send_data(self):
        if self.serial_port and self.serial_port.is_open:
            data = self.input_line.text()
            self.serial_port.write(data.encode())
            self.monitor.append(f"> {data}")
            self.input_line.clear()
        else:
            QMessageBox.warning(self, "Warning", "Serial port not connected.")

    def read_serial(self):
        if self.serial_port and self.serial_port.in_waiting:
            try:
                data = self.serial_port.readline().decode(errors="ignore").strip()
                if data:
                    self.monitor.append(f"< {data}")
            except Exception as e:
                self.monitor.append(f"Read error: {e}")

    def closeEvent(self, event):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialMainWindow()
    window.show()
    sys.exit(app.exec())
