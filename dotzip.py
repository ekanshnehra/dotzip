import sys
import math
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QComboBox,
    QStyleFactory,
    QMessageBox,
    QProgressBar,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
import os
import zipfile

class FileZipperApp(QWidget):
    def __init__(self):
        super().__init__()

        self.file_list = []
        self.password_visible = False
        self.dark_mode = False

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 600, 500)
        self.setWindowTitle('.zip')
        self.setWindowIcon(QIcon('icon.svg'))

        self.main_layout = QVBoxLayout()

        self.create_title_label()
        self.create_file_label()
        self.create_browse_button()
        self.create_zip_info_layout()
        self.create_extract_button_layout()

        self.setLayout(self.main_layout)

        self.create_dark_mode_button()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, 490, 580, 10)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.main_layout.addWidget(self.progress_bar)

    def create_dark_mode_button(self):
        dark_mode_button = QPushButton('🌙 Dark Mode', self)
        dark_mode_button.clicked.connect(self.toggle_dark_mode)
        dark_mode_button.setStyleSheet(
            'padding: 12px; background-color: #2c3e50; color: white; border: none; border-radius: 5px; margin: 5px;'
        )
        self.main_layout.addWidget(dark_mode_button)

    def create_title_label(self):
        self.title_label = QLabel('.zip')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet('color: #3498db; font-size: 130px;')
        self.main_layout.addWidget(self.title_label)

    def create_file_label(self):
        self.file_label = QLabel('No files selected.')
        self.file_label.setStyleSheet(
            'font-size: 18px; color: #7f8c8d; margin-top: 10px; margin-bottom: 10px; text-decoration: underline;'
        )
        self.main_layout.addWidget(self.file_label)
        self.setAcceptDrops(True)

    def create_browse_button(self):
        browse_button = QPushButton('Browse', self)
        browse_button.clicked.connect(self.browse_files)
        browse_button.setStyleSheet(
            'padding: 12px; background-color: #3498db; color: white; border: none; border-radius: 5px; margin: 5px;'
        )
        self.main_layout.addWidget(browse_button)

    def create_zip_info_layout(self):
        zip_info_layout = QVBoxLayout()

        zip_name_label = QLabel('Zip File Name:')
        zip_name_label.setStyleSheet('font-size: 18px; color: #2c3e50; margin-top: 15px;')
        zip_info_layout.addWidget(zip_name_label)

        self.zip_name_entry = QLineEdit(self)
        self.zip_name_entry.setStyleSheet('padding: 12px; border: 1px solid #ccc; border-radius: 5px; background-color: white;')
        zip_info_layout.addWidget(self.zip_name_entry)

        password_label = QLabel('Password (optional):')
        password_label.setStyleSheet('font-size: 18px; color: #2c3e50; margin-top: 15px;')
        zip_info_layout.addWidget(password_label)

        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet(
            'padding: 12px; border: 1px solid #ccc; border-radius: 5px; background-color: white; color: #2c3e50;'
        )
        zip_info_layout.addWidget(self.password_entry)

        show_password_button = QPushButton('Show/Hide Password', self)
        show_password_button.clicked.connect(self.toggle_password_visibility)
        show_password_button.setStyleSheet(
            'padding: 12px; background-color: #ecf0f1; color: #2c3e50; border: none; '
            'border-radius: 5px; margin-top: 5px; cursor: pointer;'
        )
        show_password_button.setCursor(Qt.PointingHandCursor)
        show_password_button.setFocusPolicy(Qt.NoFocus)
        show_password_button.setToolTip('Click to show/hide password')
        zip_info_layout.addWidget(show_password_button)

        compression_label = QLabel('Compression Format:')
        compression_label.setStyleSheet('font-size: 18px; color: #2c3e50; margin-top: 15px;')
        zip_info_layout.addWidget(compression_label)

        self.compression_combobox = QComboBox(self)
        self.compression_combobox.addItems(['.zip', '.rar', '.tar', '.tar.gz', '.tar.bz2', '.7z'])
        self.compression_combobox.setStyleSheet(
            'padding: 12px; border: 1px solid #ccc; border-radius: 5px; background-color: white; color: #2c3e50;'
        )
        zip_info_layout.addWidget(self.compression_combobox)

        self.compression_combobox.currentIndexChanged.connect(self.update_estimation)

        estimated_size_label = QLabel('Estimated Compressed Size:')
        estimated_size_label.setStyleSheet('font-size: 18px; color: #2c3e50; margin-top: 15px;')
        zip_info_layout.addWidget(estimated_size_label)

        self.estimated_size_value = QLabel(self)
        self.estimated_size_value.setStyleSheet('font-size: 18px; color: #2c3e50; margin-top: 5px;')
        zip_info_layout.addWidget(self.estimated_size_value)

        zip_button = QPushButton('Zip Files', self)
        zip_button.clicked.connect(self.zip_files)
        zip_button.setStyleSheet(
            'padding: 12px; background-color: #2ecc71; color: white; border: none; '
            'border-radius: 5px; margin-top: 15px;'
        )
        zip_info_layout.addWidget(zip_button)

        self.main_layout.addLayout(zip_info_layout)

    def create_extract_button_layout(self):
        extract_button_layout = QHBoxLayout()

        extract_button = QPushButton('Extract Files', self)
        extract_button.clicked.connect(self.extract_files)
        extract_button.setStyleSheet(
            'padding: 12px; background-color: #e74c3c; color: white; border: none; '
            'border-radius: 5px; margin-top: 15px;'
        )
        extract_button_layout.addWidget(extract_button)

        self.main_layout.addLayout(extract_button_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_font_size

    def adjust_font_size(self):
        font_size = min(self.width() // 20, 32)
        font = QFont('Arial', font_size, QFont.Bold)
        self.title_label.setFont(font)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.file_list.extend(file_paths)
        self.update_file_label()

    def browse_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, 'Select Files', '', 'All Files (*.*);;')
        self.file_list = file_paths
        self.update_file_label()

    def estimate_compressed_size(self):
        if not self.file_list:
            return 0  # No files to estimate

        compression_format = self.compression_combobox.currentText()
        compression_level = 5

        total_original_size = sum(os.path.getsize(file_path) for file_path in self.file_list)

        compression_ratio = 0.7  # Default compression ratio if not found in COMPRESSION_RATIOS

        estimated_compressed_size = math.ceil(total_original_size * compression_ratio)
        return estimated_compressed_size

    def update_file_label(self):
        if self.file_list:
            self.file_label.setText('Selected Files:')
            file_display_text = ''
            for file_path in self.file_list:
                file_display_text += f'{os.path.basename(file_path)}<br>'
            self.file_label.setText(file_display_text)
            self.file_label.setOpenExternalLinks(True)
            self.file_label.setStyleSheet(
                'font-size: 18px; color: #3498db; margin-top: 10px; margin-bottom: 10px; text-decoration: underline;'
            )
        else:
            self.file_label.setText('No files selected.')
            self.file_label.setStyleSheet(
                'font-size: 18px; color: #7f8c8d; margin-top: 10px; margin-bottom: 10px;'
            )

        estimated_size = self.estimate_compressed_size()
        self.estimated_size_value.setText(f'Approx. {estimated_size / (1024 * 1024):.2f} MB')

    def zip_files(self):
        if not self.file_list:
            QMessageBox.critical(self, 'Error', 'Please select at least one file.')
            return

        self.zip_file_name = self.zip_name_entry.text()

        if not self.zip_file_name:
            QMessageBox.critical(self, 'Error', 'Please enter a zip file name.')
            return

        compression_format = self.compression_combobox.currentText()

        password = self.password_entry.text() if self.password_entry.text() else None

        directory = os.path.dirname(self.file_list[0])
        zip_file_path = os.path.join(directory, f'{self.zip_file_name}{compression_format}')

        try:
            self.progress_bar.show()

            with zipfile.ZipFile(zip_file_path, 'w') as archive:
                total_files = len(self.file_list)
                for i, file_path in enumerate(self.file_list):
                    archive.write(file_path, os.path.basename(file_path))
                    progress = int((i + 1) / total_files * 100)
                    self.progress_bar.setValue(progress)

            QMessageBox.information(None, 'Success', f'Files compressed successfully to {zip_file_path}')
        except Exception as e:
            QMessageBox.critical(None, 'Error', f'Error compressing files: {str(e)}')
        finally:
            self.progress_bar.hide()

    def extract_files(self):
        if not self.file_list:
            QMessageBox.critical(self, 'Error', 'Please select a compressed file to extract.')
            return

        compressed_file_path = self.file_list[0]

        password = self.password_entry.text() if self.password_entry.text() else None

        destination_folder = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')

        try:
            self.progress_bar.show()

            with zipfile.ZipFile(compressed_file_path, 'r') as archive:
                total_files = len(archive.filelist)
                for i, file_info in enumerate(archive.filelist):
                    archive.extract(file_info, destination_folder)
                    progress = int((i + 1) / total_files * 100)
                    self.progress_bar.setValue(progress)

            QMessageBox.information(None, 'Success', f'Files extracted successfully to {destination_folder}')
        except Exception as e:
            QMessageBox.critical(None, 'Error', f'Error extracting files: {str(e)}')
        finally:
            self.progress_bar.hide()

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_entry.setEchoMode(QLineEdit.Normal)
        else:
            self.password_entry.setEchoMode(QLineEdit.Password)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

        background_color = '#2c3e50' if self.dark_mode else 'white'
        text_color = 'white' if self.dark_mode else '#2c3e50'

        self.setStyleSheet(f'background-color: {background_color}; color: {text_color};')
        self.title_label.setStyleSheet(f'color: #3498db;')

        self.update_file_label()

    def update_estimation(self):
        estimated_size = self.estimate_compressed_size()
        self.estimated_size_value.setText(f'Approx. {estimated_size / (1024 * 1024):.2f} MB')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))

    ex = FileZipperApp()
    ex.show()
    sys.exit(app.exec_())
