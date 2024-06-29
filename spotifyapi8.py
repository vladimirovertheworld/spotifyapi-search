import sys
import json
import time
from cryptography.fernet import Fernet
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QComboBox, QHBoxLayout, QProgressBar, QTableWidget, QTableWidgetItem, 
                             QMenuBar, QMenu, QAction, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Save the key securely
with open('cipher_key.key', 'wb') as key_file:
    key_file.write(key)

class Worker(QThread):
    progress = pyqtSignal(int)
    new_result = pyqtSignal(dict)
    
    def __init__(self, genres, creds):
        super().__init__()
        self.genres = genres
        self.creds = creds
    
    def run(self):
        creds = json.loads(cipher_suite.decrypt(self.creds.encode()).decode())
        
        # Authenticate with Spotify
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=creds['client_id'],
                                                       client_secret=creds['client_secret'],
                                                       redirect_uri=creds['redirect_uri'],
                                                       scope="playlist-read-private"))
        
        for genre in self.genres:
            playlists = sp.search(q=f'genre:{genre}', type='playlist', limit=50)
            for playlist in playlists['playlists']['items']:
                playlist_id = playlist['id']
                detailed_playlist = sp.playlist(playlist_id)
                owner_profile = sp.user(detailed_playlist['owner']['id'])
                result = {
                    'name': detailed_playlist['name'],
                    'likes': detailed_playlist['followers']['total'],
                    'owner': detailed_playlist['owner']['display_name'],
                    'link': detailed_playlist['external_urls']['spotify'],
                    'owner_email': owner_profile.get('email', 'N/A'),
                    'additional_info': detailed_playlist.get('description', 'N/A')
                }
                self.new_result.emit(result)
                time.sleep(0.1)  # Simulate processing time
                self.progress.emit(1)

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About')
        self.setFixedSize(400, 400)

        layout = QVBoxLayout()
        
        logo = QLabel(self)
        pixmap = QPixmap('logo.png')
        scaled_pixmap = pixmap.scaled(self.width(), self.height()//2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(scaled_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        text = QLabel('VOVKES SOFTWARE "HYPERSOFT" (c) 2025', self)
        text.setAlignment(Qt.AlignCenter)
        layout.addWidget(text)
        
        email = QLabel('Author: Volodymyr Ovcharov - volodymyr.ovcharov@example.com', self)
        email.setAlignment(Qt.AlignCenter)
        layout.addWidget(email)

        ok_button = QPushButton('Okay', self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Music Streaming Search')
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout()
        
        self.platform_label = QLabel('Choose Streaming Platform:', self)
        layout.addWidget(self.platform_label)
        
        self.platform_combo = QComboBox(self)
        self.platform_combo.addItems(["Spotify", "Apple Music", "Amazon Music", "Tidal", "Deezer", 
                                      "YouTube Music", "SoundCloud", "Pandora", "iHeartRadio", "Qobuz"])
        layout.addWidget(self.platform_combo)
        
        self.genre_label = QLabel('Choose Music Genre:', self)
        layout.addWidget(self.genre_label)
        
        self.genre_combo = QComboBox(self)
        self.genre_combo.addItems(["House", "Techno", "Drum and Bass", "Trance", "Dubstep", 
                                   "EDM", "Electro", "Synthwave", "Trap", "Future Bass"])
        layout.addWidget(self.genre_combo)
        
        self.button_layout = QHBoxLayout()
        
        self.search_button = QPushButton('Search', self)
        self.search_button.clicked.connect(self.startSearch)
        self.button_layout.addWidget(self.search_button)
        
        self.stop_button = QPushButton('Stop', self)
        self.button_layout.addWidget(self.stop_button)
        
        self.exit_button = QPushButton('Exit', self)
        self.exit_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.exit_button)
        
        layout.addLayout(self.button_layout)
        
        self.progressBar = QProgressBar(self)
        layout.addWidget(self.progressBar)
        
        self.resultTable = QTableWidget(self)
        self.resultTable.setColumnCount(6)
        self.resultTable.setHorizontalHeaderLabels(["Name", "Likes", "Owner", "Link", "Owner Email", "Additional Info"])
        self.resultTable.setSortingEnabled(True)
        layout.addWidget(self.resultTable)
        
        self.central_widget.setLayout(layout)
        
        self.createMenu()
    
    def createMenu(self):
        menubar = self.menuBar()
        
        fileMenu = menubar.addMenu('File')
        
        viewCredentials = QAction('View Saved Credentials', self)
        viewCredentials.triggered.connect(self.viewSavedCredentials)
        fileMenu.addAction(viewCredentials)
        
        aboutMenu = menubar.addMenu('About')
        
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.showAboutDialog)
        aboutMenu.addAction(aboutAction)
    
    def viewSavedCredentials(self):
        try:
            with open('credentials.json', 'r') as file:
                creds = json.load(file)
                QMessageBox.information(self, 'Saved Credentials', json.dumps(creds, indent=4))
        except FileNotFoundError:
            QMessageBox.warning(self, 'Error', 'No saved credentials found.')
    
    def showAboutDialog(self):
        about_dialog = AboutDialog()
        about_dialog.exec_()
    
    def startSearch(self):
        self.search_button.setEnabled(False)
        self.resultTable.setRowCount(0)
        
        try:
            with open('credentials.json', 'r') as file:
                creds = json.load(file)
        except FileNotFoundError:
            QMessageBox.warning(self, 'Error', 'No credentials file found.')
            self.search_button.setEnabled(True)
            return
        
        encoded_creds = cipher_suite.encrypt(json.dumps(creds).encode()).decode()
        
        genre = self.genre_combo.currentText()
        
        self.worker = Worker([genre], encoded_creds)
        self.worker.progress.connect(self.updateProgress)
        self.worker.new_result.connect(self.addResult)
        
        total_tasks = 50  # Assuming 50 playlists for the selected genre
        self.progressBar.setMaximum(total_tasks)
        
        self.worker.start()
    
    def updateProgress(self, value):
        self.progressBar.setValue(self.progressBar.value() + value)
    
    def addResult(self, result):
        row_position = self.resultTable.rowCount()
        self.resultTable.insertRow(row_position)
        
        self.resultTable.setItem(row_position, 0, QTableWidgetItem(result['name']))
        self.resultTable.setItem(row_position, 1, QTableWidgetItem(str(result['likes'])))
        self.resultTable.setItem(row_position, 2, QTableWidgetItem(result['owner']))
        self.resultTable.setItem(row_position, 3, QTableWidgetItem(result['link']))
        self.resultTable.setItem(row_position, 4, QTableWidgetItem(result['owner_email']))
        self.resultTable.setItem(row_position, 5, QTableWidgetItem(result['additional_info']))
    
    def displayResult(self, results):
        # Select the playlist with the highest number of likes
        if results:
            best_playlist = results[0]
            QMessageBox.information(self, 'Best Playlist', f"Best Playlist:\n"
                                                          f"Name: {best_playlist['name']}\n"
                                                          f"Likes: {best_playlist['likes']}\n"
                                                          f"Owner: {best_playlist['owner']}\n"
                                                          f"Link: {best_playlist['link']}\n"
                                                          f"Owner Email: {best_playlist['owner_email']}\n"
                                                          f"Additional Info: {best_playlist['additional_info']}")
        
        self.search_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
