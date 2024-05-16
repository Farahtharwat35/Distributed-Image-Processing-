import shutil
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QFileDialog, QPushButton, \
    QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QDragEnterEvent, QDropEvent, QDragMoveEvent, QPixmap, \
    QDesktopServices
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from PyQt5.QtCore import QUrl
import requests
import base64
import json

class ClientGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Distributed Image Processor")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1200, 800)
        self.tableData = []
        # Set the font for the title and other text
        self.title_font = QFont("consolas", 24, QFont.Bold)
        self.text_font = QFont("roboto", 14)
        self.smaller_font = QFont("roboto", 10)

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
        vbox_layout.setContentsMargins(150, 150, 150, 150)  # Set the top margin of the layout

        # Add a title label to the layout
        title_label = QLabel("Distributed Image Processor", self)
        title_label.setAlignment(Qt.AlignCenter)  # Align the label horizontally center
        title_label.setFont(self.title_font)  # Set the font for the label
        vbox_layout.addWidget(title_label)

        vbox_layout.addSpacing(50)

        self.file_path_label = QLabel("No file selected", self)
        self.file_path_label.setAlignment(Qt.AlignCenter)
        self.file_path_label.setFont(self.smaller_font)
        self.file_path_label.setStyleSheet("QLabel { color : #00cf81; }")
        self.file_path_label.setFixedSize(200, 50)
        self.file_path_label.setContentsMargins(20, 10, 10, 10)

        self.upload_button = QPushButton("Browse images", self)
        self.upload_button.clicked.connect(self.openFileDialog)
        self.upload_button.setFont(self.text_font)
        self.upload_button.setStyleSheet("QPushButton { border-radius: 10px; background-color: #00cf81;"
                                         " color: black; font-size: 20px; cursor: pointer; padding: 5px 10px; }")
        self.upload_button.setFixedSize(200, 50)
        self.upload_button.setContentsMargins(20, 10, 10, 10)

        #Family ComboBox
        self.processing_options = QComboBox(self)
        self.processing_options.addItems(["Processing family", "Color Manipulation", "Edge Detection",
                                          "Fourier Domain Transform", "Thresholding", "Noise Removal",
                                          "General Filters"])
        self.processing_options.setCurrentIndex(0)
        self.processing_options.setFont(self.smaller_font)
        self.processing_options.setStyleSheet("QComboBox { border-radius: 10px; border: 2px solid #00cf81; "
                                              "background-color: #1c1e1c; color: #7d7d7d;}")
        self.processing_options.setFixedSize(200, 50)
        self.processing_options.setContentsMargins(20, 10, 10, 10)
        

        #Add operation ComboBox
        self.additional_options = QComboBox(self)
        self.additional_options.setFont(self.smaller_font)
        self.additional_options.setStyleSheet("QComboBox { border-radius: 10px; border: 2px solid #00cf81; "
                                              "background-color: #1c1e1c; color: #7d7d7d;}")
        self.additional_options.setFixedSize(200, 50)
        self.additional_options.setContentsMargins(20, 10, 10, 10)
    
        self.processing_options.currentIndexChanged.connect(self.update_second_combobox)
        
        

        self.tableCols=4
        self.table=QTableWidget(1,self.tableCols,self)
        self.table.setHorizontalHeaderLabels(["Image","Path","Family","Operation"])
        self.table.setFixedWidth(900)
        self.table.setCellWidget(0,0,self.upload_button)
        self.table.setCellWidget(0,1,self.file_path_label)
        self.table.setCellWidget(0,2,self.processing_options)
        self.table.setCellWidget(0,3,self.additional_options)
        self.tableData.append([self.file_path_label,self.additional_options])
        self.table.setStyleSheet("""
                QTableWidget {
                    background-color:#1c1e1c;
                    border: 0px;
                    border-color: #1c1e1c;
                                 
                }
                QHeaderView::section {
                    background-color: #1c1e1c;
                    color: white;
                    border: 0px;
                    border-color: #1c1e1c;
                    text-style: bold;
                }
                QTableWidget::item:selected {
                    background-color:#1c1e1c;
                }
                 QTableWidget::item {
                    border: 0px;  # Remove the border from the cells
                    border-color: #1c1e1c;
                    }
            """)
        self.table.setRowHeight(0, 60)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.table.verticalHeader().hide()
        vbox_layout.addWidget(self.table)

        vbox_layout.addSpacing(30)

        # Add a button to start the processing
        self.submit_button = QPushButton("Submit", self)
        # self.submit_button.clicked.connect(process_image)
        # Connect the submit button to the 'on_submit_clicked' method
        self.submit_button.clicked.connect(self.on_submit_clicked)
        self.submit_button.setFont(self.text_font)
        self.submit_button.setStyleSheet("QPushButton { border-radius: 10px; background-color: #00cf81;"
                                         " color: black; font-size: 20px; cursor: pointer; padding: 10px 20px; }")
        self.submit_button.setFixedSize(200, 50)
       
       #Add button add row for table
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_row)
        self.add_button.setFont(self.text_font)
        self.add_button.setStyleSheet("QPushButton { border-radius: 10px; background-color: #00cf81;"
                                            " color: black; font-size: 20px; cursor: pointer; padding: 10px 20px; }")
        self.add_button.setFixedSize(200, 50)


        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.submit_button)
        hbox_layout.addWidget(self.add_button)

        # Align the submit_button to the left and the add_button to the right
        hbox_layout.setAlignment(self.submit_button, Qt.AlignLeft)
        hbox_layout.setAlignment(self.add_button, Qt.AlignRight)

        vbox_layout.addLayout(hbox_layout)

    def copy_element(self, element,name,connected=None):
        if element == "upload_button":
            name = QPushButton("Browse images", self)
            name.clicked.connect(lambda: self.openFileDialog(connected))
            name.setFont(self.text_font)
            name.setStyleSheet("QPushButton { border-radius: 10px; background-color: #00cf81;"
                                            " color: black; font-size: 20px; cursor: pointer; padding: 5px 10px; }")
            name.setFixedSize(200, 50)
        elif element == "processing_options":
            name = QComboBox(self)
            name.addItems(["Processing family", "Color Manipulation", "Edge Detection",
                                          "Fourier Domain Transform", "Thresholding", "Noise Removal",
                                          "General Filters"])
            name.setCurrentIndex(0)
            name.setFont(self.smaller_font)
            name.setStyleSheet("QComboBox { border-radius: 10px; border: 2px solid #00cf81; "
                                              "background-color: #1c1e1c; color: #7d7d7d;}")
            name.setFixedSize(200, 50)
            name.currentIndexChanged.connect(lambda: self.update_second_combobox(name,connected))
        elif element == "additional_options":
            name = QComboBox(self)
            name.setFont(self.smaller_font)
            name.setStyleSheet("QComboBox { border-radius: 10px; border: 2px solid #00cf81; "
                                              "background-color: #1c1e1c; color: #7d7d7d;}")
            name.setFixedSize(200, 50)
        elif element == "file_path_label":
            name = QLabel("No file selected", self)
            name.setAlignment(Qt.AlignCenter)
            name.setFont(self.smaller_font)
            name.setStyleSheet("QLabel { color : #00cf81; }")
            name.setFixedSize(200, 50)
        name.setContentsMargins(20, 10, 10, 10)
        return name
        

        
    def add_row(self):
        rowPosition = self.table.rowCount()
        self.table.insertRow(rowPosition)
        tableRow=[]
        tableRow.append(self.copy_element("file_path_label",f"file_path_label_{rowPosition}"))
        tableRow.append(self.copy_element("additional_options",f"additional_options_{rowPosition}"))
        self.table.setCellWidget(rowPosition,0,self.copy_element("upload_button",f"upload_button_{rowPosition}",tableRow[0]) )
        self.table.setCellWidget(rowPosition,1,tableRow[0])
        self.table.setCellWidget(rowPosition,2,self.copy_element("processing_options",f"processing_options_{rowPosition}",tableRow[1]))
        self.table.setCellWidget(rowPosition,3,tableRow[1])
        self.tableData.append(tableRow)
        self.table.setFixedWidth(900)
        self.table.setHorizontalHeaderLabels(["Image","Path","Family","Operation"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table.setRowHeight(rowPosition, 60)
        self.table.show()
        if(self.table.rowCount()>=10):
            self.add_button.setEnabled(False)

    def openFileDialog(main_window,label=None):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(main_window, "Select an image", "",
                                                   "Images (*.jpg *.png *.jpeg)", options=options)
        files=','.join(file_name)
        print(f"labels: {label}")
        if file_name:
            if hasattr(label, 'setText'):
                label.setText(file_name)
            else:
                main_window.file_path_label.setText(file_name)

    def update_second_combobox(main_window,first = None,second = None):
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
        if hasattr(first, 'currentText'):
            processing_family = first.currentText()
            second.clear()
            second.addItems(options_dict.get(processing_family, []))
        else:
            processing_family = main_window.processing_options.currentText()
            main_window.additional_options.clear()
            main_window.additional_options.addItems(options_dict.get(processing_family, []))
    
    def on_submit_clicked(self):
        print(f'preparing to send request to server....')
        processing_options = {
            "Inversion": 1,
            "Saturation": 2,
            "RGB to Gray": 3,
            "Gray to RGB": 4,
            "Binary thresholding": 18,
            "Otsu thresholding":19,
            "Gaussian thresholding":24,
            "Mean-adaptive thresholding":23,
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
        for row in self.tableData:
            image_path = row[0].text()
            option = row[1].currentText()
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            service_num=processing_options[option]
            request = {'image': image_base64, 'service_num': service_num}
            response = requests.post('http://localhost:8000/', data=json.dumps(request),
                                    headers={'Content-Type': 'application/json'})
            print(f'server response: {response.text}')
            self.show_result_window(response.text)
    
    def show_result_window(self, respone_text):
        # This method creates a new window to display the processed image
        self.result_window = ResultWindow(respone_text)
        self.result_window.show()


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