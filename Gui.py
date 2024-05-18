import shutil
import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QFileDialog, QPushButton, \
    QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QDragEnterEvent, QDropEvent, QDragMoveEvent, QPixmap, \
    QDesktopServices
from PyQt5.QtCore import QUrl
import requests
import base64
import json


class ClientGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Distributed Image Processor")
        self.setWindowIcon(QIcon("icon.png"))

        # Set the font for the title and other text
        title_font = QFont("consolas", 24, QFont.Bold)
        text_font = QFont("roboto", 16)
        smaller_text_font = QFont("roboto", 12)

        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Set the background color and text color
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1c1e1c"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)

        # Create a vertical box layout
        vbox_layout = QVBoxLayout(central_widget)
        vbox_layout.setAlignment(Qt.AlignTop)  # Align the layout vertically top
        vbox_layout.setContentsMargins(300, 150, 300, 150)  # Set the top margin of the layout

        # Add a title label to the layout
        title_label = QLabel("Distributed Image Processor", self)
        title_label.setAlignment(Qt.AlignCenter)  # Align the label horizontally center
        title_label.setFont(title_font)  # Set the font for the label
        vbox_layout.addWidget(title_label)

        vbox_layout.addSpacing(100)

        # Label to indicate drag and drop functionality
        drag_drop_label = QLabel("Drag and drop an image here\n upload .jpg, .png, .jpeg", self)
        drag_drop_label.setAlignment(Qt.AlignCenter)
        drag_drop_label.setFont(text_font)
        drag_drop_label.setStyleSheet("QLabel "
                                      "{ border: 2px dashed #00cf81; border-radius: 15px; "
                                      "padding: 10px; color: #fafafa; }")
        vbox_layout.addWidget(drag_drop_label)

        # Enable dragging and dropping onto the window
        self.setAcceptDrops(True)

        vbox_layout.addSpacing(20)

        # Create a horizontal box layout for the upload button and file path label
        hbox1_layout = QHBoxLayout()
        hbox1_layout.setAlignment(Qt.AlignLeft)  # Align the layout left

        # Add the upload button to the horizontal layout
        self.upload_button = QPushButton("Browse images", self)
        self.upload_button.clicked.connect(self.openFileDialog)
        self.upload_button.setFont(text_font)
        self.upload_button.setStyleSheet("QPushButton { border-radius: 10px; background-color: #00cf81;"
                                         " color: black; font-size: 20px; cursor: pointer; padding: 10px 20px; }")
        self.upload_button.setFixedSize(200, 50)
        hbox1_layout.addWidget(self.upload_button)

        # Add a spacer to separate the button and label
        hbox1_layout.addSpacing(10)

        # Add the file path label to the horizontal layout
        self.file_path_label = QLabel("No file selected", self)
        self.file_path_label.setAlignment(Qt.AlignCenter)
        self.file_path_label.setFont(smaller_text_font)
        self.file_path_label.setStyleSheet("QLabel { color : #00cf81; }")
        hbox1_layout.addWidget(self.file_path_label)

        # Add the horizontal layout to the vertical layout
        vbox_layout.addLayout(hbox1_layout)
        vbox_layout.addSpacing(20)

        hbox2_layout = QHBoxLayout()
        hbox2_layout.setAlignment(Qt.AlignLeft)

        self.processing_family_label = QLabel("Choose Processing Family", self)
        self.processing_family_label.setFont(text_font)
        self.processing_family_label.setStyleSheet("QLabel { color : #fafafa; }")
        self.processing_family_label.hide()
        hbox2_layout.addWidget(self.processing_family_label)

        hbox2_layout.addSpacing(20)

        # Dropdown menu for processing options
        self.processing_options = QComboBox(self)
        self.processing_options.addItems(["Processing family", "Color Manipulation", "Edge Detection",
                                          "Fourier Domain Transform", "Thresholding", "Noise Removal",
                                          "General Filters"])
        self.processing_options.setCurrentIndex(0)
        self.processing_options.setFont(smaller_text_font)
        self.processing_options.setStyleSheet("QComboBox { border-radius: 10px; border: 2px solid #00cf81; "
                                              "background-color: #1c1e1c; color: #7d7d7d;}")
        self.processing_options.setFixedSize(800, 50)
        self.processing_options.hide()
        hbox2_layout.addWidget(self.processing_options)

        vbox_layout.addLayout(hbox2_layout)
        vbox_layout.addSpacing(20)

        hbox3_layout = QHBoxLayout()
        hbox3_layout.setAlignment(Qt.AlignLeft)

        self.additional_options_label = QLabel("Choose operation", self)
        self.additional_options_label.setFont(text_font)
        self.additional_options_label.setStyleSheet("QLabel { color : #fafafa; }")
        self.additional_options_label.hide()
        hbox3_layout.addWidget(self.additional_options_label)

        hbox3_layout.addSpacing(125)

        # Second combobox for additional options, hidden by default
        self.additional_options = QComboBox(self)
        self.additional_options.setFont(smaller_text_font)
        self.additional_options.setStyleSheet("QComboBox { border-radius: 10px; border: 2px solid #00cf81; "
                                              "background-color: #1c1e1c; color: #7d7d7d;}")
        self.additional_options.setFixedSize(800, 50)
        self.additional_options.hide()
        hbox3_layout.addWidget(self.additional_options)

        vbox_layout.addLayout(hbox3_layout)
        vbox_layout.addSpacing(40)

        # Connect the first combobox to update the second combobox based on selection
        self.processing_options.currentIndexChanged.connect(self.update_second_combobox)

        # Add the submit button to the horizontal layout
        self.submit_button = QPushButton("Submit", self)
        # self.submit_button.clicked.connect(process_image)
        # Connect the submit button to the 'on_submit_clicked' method
        self.submit_button.clicked.connect(self.on_submit_clicked)
        self.submit_button.setFont(text_font)
        self.submit_button.setStyleSheet("QPushButton { border-radius: 10px; background-color: #00cf81;"
                                         " color: black; font-size: 20px; cursor: pointer; padding: 10px 20px; }")
        self.submit_button.setFixedSize(200, 50)
        self.submit_button.hide()
        vbox_layout.addWidget(self.submit_button)

    def openFileDialog(main_window):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(main_window, "Select an image", "",
                                                   "Images (*.jpg *.png *.jpeg)", options=options)
        if file_name:
            main_window.file_path_label.setText(file_name)
            main_window.processing_options.show()
            main_window.processing_family_label.show()

    def update_second_combobox(main_window):
        # Dictionary mapping the first combobox options to the second combobox options
        options_dict = {
            "Color Manipulation": ["Inversion", "Saturation", "RGB to Gray", "Gray to RGB"],

            "Thresholding": ["Binary thresholding", "Otsu thresholding", "Gaussian thresholding",
                             "Mean-adaptive thresholding", "Gaussian-adaptive thresholding"],

            "Edge Detection": ["Sobel edge detection", "Prewitt edge detection", "Roberts edge detection",
                               "Canny edge detection", "Hough transform", "Harris corner detection"],

            "General Filters": ["Blurring", "Sharpening"],

            "Noise Removal": ["Remove Gaussian noise", "Remove salt & pepper noise"],

            "Fourier Domain Transform": ["Butterworth low pass filter", "Butterworth high pass filter",
                                         "Low pass filter", "High pass filter"]
        }

        # Get the selected processing family
        processing_family = main_window.processing_options.currentText()

        # Update and show the second combobox with the relevant options
        main_window.additional_options.clear()
        main_window.additional_options.addItems(options_dict.get(processing_family, []))
        main_window.additional_options_label.show()
        main_window.additional_options.show()
        main_window.submit_button.show()

    def dragEnterEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():  # Check if the dropped item has URLs
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                file_path = urls[0].toLocalFile()
                self.file_path_label.setText(file_path)
                self.processing_options.show()
                self.processing_family_label.show()
                event.accept()  # Accept the drop event
            else:
                event.ignore()  # Ignore the drop event if it's not a file
        else:
            event.ignore()  # Ignore the drop event if there are no URLs

    def on_submit_clicked(self):
        # send request to server
        print(f'preparing to send request to server....')
        image_path = self.file_path_label.text()
        option = self.additional_options.currentText()
        processing_options = {
            "Inversion": 1,
            "Saturation": 2,
            "RGB to Gray": 3,
            "Gray to RGB": 4,
            "Binary thresholding": 18,
            "Otsu thresholding": 19,
            "Gaussian thresholding": 24,
            "Mean-adaptive thresholding": 23,
            "Gaussian-adaptive thresholding": 20,
            "Sobel edge detection": 12,
            "Prewitt edge detection": 13,
            "Roberts edge detection": 14,
            "Canny edge detection": 15,
            "Hough transform": 16,
            "Harris corner detection": 17,
            "Blurring": 8,
            "Sharpening": 9,
            "Remove Gaussian noise": 10,
            "Remove salt & pepper noise": 11,
            "Butterworth low pass filter": 6,
            "Butterworth high pass filter": 7,
            "Low pass filter": 21,
            "High pass filter": 22,
        }
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        service_num = processing_options[option]
        request = {'image': image_base64, 'service_num': service_num}
        response = requests.post('http://localhost:8000', data=json.dumps(request),
                                 headers={'Content-Type': 'application/json'})
        print(f'server response: {response.text}')
        # Creating a thread for task_status
        task_status_thread = threading.Thread(target=self.task_status, args=(response.text,))
        task_status_thread.start()
        print("Task status thread started")

    def task_status(self, task_id):
        try:
            from Notification_System import NotificationSystem
            notification_system = NotificationSystem(task_id)
            poll_thread = threading.Thread(target=notification_system.poll_task, args=(self,))
            poll_thread.start()
            print("Polling thread started")
        except Exception as e:
            print(f"Failed to start polling thread: {e}")

    def show_result_window(self, image_status=None, processed_image=None):
        # This method creates a new window to display the processed image
        if (image_status == None):
            # self.result_window = ResultWindow("NOT PROCESSED YET")
            print("NOT PROCESSED YET")
        elif (image_status == "processed"):
            # self.result_window = ResultWindow("PROCESSED", processed_image)
            print("PROCESSED", processed_image)
        else:
            # self.result_window = ResultWindow(image_status)
            print(image_status)
        # self.result_window.show()


class ResultWindow(QWidget):
    def __init__(self, title, parent=None):
        super(ResultWindow, self).__init__(parent)

        # Set window title and icon
        self.setWindowTitle(f'Processed Image: {title}')
        self.setWindowIcon(QIcon("icon.png"))

        # Set the background color
        self.setStyleSheet("background-color: #1c1e1c;")

        # Set the font for the title and other text
        title_font = QFont("consolas", 24, QFont.Bold)
        text_font = QFont("roboto", 16)

        # Create a vertical box layout for the main window
        vbox_layout = QVBoxLayout(self)
        vbox_layout.setAlignment(Qt.AlignTop)
        vbox_layout.setContentsMargins(300, 150, 300, 150)

        # Add a title label to the layout
        title_label = QLabel("Here's your result...", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #fafafa;")
        title_label.setFont(title_font)
        vbox_layout.addWidget(title_label)

        vbox_layout.addSpacing(100)

        vbox_layout.addSpacing(30)
        # Create a horizontal box layout for the download button
        hbox_layout = QHBoxLayout()
        hbox_layout.setAlignment(Qt.AlignCenter)
        image_url = ''
        # Add the download button to the horizontal layout
        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(lambda: self.download_image(image_url))
        self.download_button.setFont(text_font)
        self.download_button.setStyleSheet("QPushButton { border-radius: 10px; background-color: #00cf81;"
                                           " color: black; font-size: 20px; cursor: pointer; padding: 10px 20px; }")
        self.download_button.setFixedSize(200, 50)
        hbox_layout.addWidget(self.download_button)

        # Add the horizontal layout to the main vertical layout
        vbox_layout.addLayout(hbox_layout)

    def download_image(self, image_path):
        QDesktopServices.openUrl(QUrl(image_path))
        # options = QFileDialog.Options()
        # save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
        #                                            "Images (*.jpg *.png *.jpeg)", options=options)
        # if save_path:
        #     shutil.copyfile(image_path, save_path)


def main():
    app = QApplication(sys.argv)
    main_window = ClientGui()
    main_window.show()
    sys.exit(app.exec_())
    # client = ClientGUI('http://localhost:8000')
    # server = WebSocketServer(('localhost', 8765),client)
    # server_thread = threading.Thread(target=server.start_server)
    # server_thread.start()


if __name__ == "__main__":
    main()