import sys
import json
import time
import base64
from cryptography.fernet import Fernet
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
                             QProgressBar, QLineEdit, QComboBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Save the key securely
with open('cipher_key.key', 'wb') as key_file:
    key_file.write(key)

class Worker(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    
    def __init__(self, genres, creds):
        super().__init__()
        self.genres = genres
        self.creds = creds
    
    def run(self):
        results = []
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
                results.append({
                    'name': detailed_playlist['name'],
                    'followers': detailed_playlist['followers']['total'],
                    'owner': detailed_playlist['owner']['display_name'],
                    'link': detailed_playlist['external_urls']['spotify']
                })
                time.sleep(0.1)  # Simulate processing time
                self.progress.emit(1)
        
        # Convert results to DataFrame and sort by followers
        df = pd.DataFrame(results)
        df = df.sort_values(by='followers', ascending=False)
        self.result.emit(df.to_string(index=False))

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Music Streaming Search')
        self.setGeometry(100, 100, 800, 600)
        
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
        self.genre_combo.addItems(["drum and bass", "idm", "electro"])
        layout.addWidget(self.genre_combo)
        
        self.api_label = QLabel('Enter your API Key:', self)
        layout.addWidget(self.api_label)
        
        self.api_input = QLineEdit(self)
        layout.addWidget(self.api_input)
        
        self.secret_label = QLabel('Enter your API Secret:', self)
        layout.addWidget(self.secret_label)
        
        self.secret_input = QLineEdit(self)
        layout.addWidget(self.secret_input)
        
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
        
        self.resultText = QTextEdit(self)
        self.resultText.setReadOnly(True)
        layout.addWidget(self.resultText)
        
        self.setLayout(layout)
    
    def startSearch(self):
        self.search_button.setEnabled(False)
        self.resultText.clear()
        
        platform = self.platform_combo.currentText()
        genre = self.genre_combo.currentText()
        api_key = self.api_input.text()
        api_secret = self.secret_input.text()
        
        creds = {
            "client_id": api_key,
            "client_secret": api_secret,
            "redirect_uri": "http://localhost:8888/callback"
        }
        encoded_creds = cipher_suite.encrypt(json.dumps(creds).encode()).decode()
        
        self.worker = Worker([genre], encoded_creds)
        self.worker.progress.connect(self.updateProgress)
        self.worker.result.connect(self.displayResult)
        
        total_tasks = 50  # Assuming 50 playlists for the selected genre
        self.progressBar.setMaximum(total_tasks)
        
        self.worker.start()
    
    def updateProgress(self, value):
        self.progressBar.setValue(self.progressBar.value() + value)
    
    def displayResult(self, result):
        self.resultText.setText(result)
        self.search_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
