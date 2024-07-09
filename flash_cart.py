import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QTabWidget, QMessageBox, QAction, QInputDialog, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox, QFormLayout, QLineEdit
)
from PyQt5.QtCore import Qt

class FlashKartSekmesi(QWidget):
    def __init__(self, db_conn, topic_id, parent=None):
        super(FlashKartSekmesi, self).__init__(parent)
        
        self.db_conn = db_conn
        self.topic_id = topic_id
        self.initUI()
        self.load_cards()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.card_list = QListWidget(self)
        self.card_list.itemDoubleClicked.connect(self.edit_card)
        layout.addWidget(self.card_list)
        
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Ekle", self)
        self.add_button.setFixedSize(100, 40)
        self.add_button.setStyleSheet("font-size: 18px;")
        self.add_button.clicked.connect(self.add_card)
        button_layout.addWidget(self.add_button, alignment=Qt.AlignCenter)
        
        self.delete_button = QPushButton("Sil", self)
        self.delete_button.setFixedSize(100, 40)
        self.delete_button.setStyleSheet("font-size: 18px;")
        self.delete_button.clicked.connect(self.delete_card)
        button_layout.addWidget(self.delete_button, alignment=Qt.AlignCenter)

        self.study_button = QPushButton("Çalış", self)
        self.study_button.setFixedSize(100, 40)
        self.study_button.setStyleSheet("font-size: 18px;")
        self.study_button.clicked.connect(self.study_cards)
        button_layout.addWidget(self.study_button, alignment=Qt.AlignCenter)
        
        self.save_button = QPushButton("Kaydet", self)
        self.save_button.setFixedSize(100, 40)
        self.save_button.setStyleSheet("font-size: 18px;")
        self.save_button.clicked.connect(self.save_all_cards)
        button_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def add_card(self):
        front, ok1 = QInputDialog.getText(self, "Yeni Kart", "Ön Yüz:")
        if ok1 and front:
            back, ok2 = QInputDialog.getText(self, "Yeni Kart", "Arka Yüz:")
            if ok2 and back:
                card = f"Ön: {front}\nArka: {back}"
                list_item = QListWidgetItem(card)
                self.card_list.addItem(list_item)
                self.save_card_to_db(front, back)
    
    def edit_card(self, item):
        card = item.text().split('\n')
        front = card[0].split(': ')[1]
        back = card[1].split(': ')[1]
        
        new_front, ok1 = QInputDialog.getText(self, "Kartı Düzenle", "Ön Yüz:", text=front)
        if ok1 and new_front:
            new_back, ok2 = QInputDialog.getText(self, "Kartı Düzenle", "Arka Yüz:", text=back)
            if ok2 and new_back:
                new_card = f"Ön: {new_front}\nArka: {new_back}"
                item.setText(new_card)
                self.update_card_in_db(front, back, new_front, new_back)
    
    def delete_card(self):
        selected_item = self.card_list.currentItem()
        if selected_item:
            reply = QMessageBox.question(self, 'Silme Onayı', 'Bu kartı silmek istediğinize emin misiniz?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                card = selected_item.text().split('\n')
                front = card[0].split(': ')[1]
                back = card[1].split(': ')[1]
                self.remove_card_from_db(front, back)
                self.card_list.takeItem(self.card_list.currentRow())

    def load_cards(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT front, back FROM cards WHERE topic_id=?", (self.topic_id,))
        rows = cursor.fetchall()
        for row in rows:
            front, back = row
            card = f"Ön: {front}\nArka: {back}"
            list_item = QListWidgetItem(card)
            self.card_list.addItem(list_item)
    
    def save_card_to_db(self, front, back):
        cursor = self.db_conn.cursor()
        cursor.execute("INSERT INTO cards (front, back, topic_id) VALUES (?, ?, ?)", (front, back, self.topic_id))
        self.db_conn.commit()
    
    def update_card_in_db(self, old_front, old_back, new_front, new_back):
        cursor = self.db_conn.cursor()
        cursor.execute("UPDATE cards SET front = ?, back = ? WHERE front = ? AND back = ? AND topic_id = ?", (new_front, new_back, old_front, old_back, self.topic_id))
        self.db_conn.commit()
    
    def remove_card_from_db(self, front, back):
        cursor = self.db_conn.cursor()
        cursor.execute("DELETE FROM cards WHERE front = ? AND back = ? AND topic_id = ?", (front, back, self.topic_id))
        self.db_conn.commit()

    def study_cards(self):
        self.study_window = StudyWindow(self.db_conn, self.topic_id)
        self.study_window.show()

    def save_all_cards(self):
        # Tüm kartları veritabanına kaydet
        self.db_conn.commit()
        QMessageBox.information(self, "Başarılı", "Tüm kartlar kaydedildi.")

class StudyWindow(QWidget):
    def __init__(self, db_conn, topic_id, parent=None):
        super(StudyWindow, self).__init__(parent)
        
        self.db_conn = db_conn
        self.topic_id = topic_id
        self.initUI()
        self.load_cards()
    
    def initUI(self):
        self.setWindowTitle('Flash Kart Çalışma')
        self.setGeometry(150, 150, 400, 300)
        
        layout = QVBoxLayout()
        
        self.card_label = QLabel("", self)
        self.card_label.setAlignment(Qt.AlignCenter)
        self.card_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.card_label)
        
        button_layout = QHBoxLayout()
        
        self.show_front_button = QPushButton("Ön Yüzü Göster", self)
        self.show_front_button.setFixedSize(150, 40)
        self.show_front_button.setStyleSheet("font-size: 18px;")
        self.show_front_button.clicked.connect(self.show_front)
        button_layout.addWidget(self.show_front_button, alignment=Qt.AlignCenter)

        self.show_back_button = QPushButton("Arka Yüzü Göster", self)
        self.show_back_button.setFixedSize(150, 40)
        self.show_back_button.setStyleSheet("font-size: 18px;")
        self.show_back_button.clicked.connect(self.show_back)
        button_layout.addWidget(self.show_back_button, alignment=Qt.AlignCenter)
        
        self.next_button = QPushButton("Sonraki", self)
        self.next_button.setFixedSize(100, 40)
        self.next_button.setStyleSheet("font-size: 18px;")
        self.next_button.clicked.connect(self.next_card)
        button_layout.addWidget(self.next_button, alignment=Qt.AlignCenter)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.cards = []
        self.current_card_index = -1
    
    def load_cards(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT front, back FROM cards WHERE topic_id=?", (self.topic_id,))
        self.cards = cursor.fetchall()
        self.next_card()
    
    def show_front(self):
        if self.current_card_index >= 0:
            self.card_label.setText(self.cards[self.current_card_index][0])

    def show_back(self):
        if self.current_card_index >= 0:
            self.card_label.setText(self.cards[self.current_card_index][1])
    
    def next_card(self):
        self.current_card_index = (self.current_card_index + 1) % len(self.cards)
        self.card_label.setText(self.cards[self.current_card_index][0])

class KonuSecmeDialog(QDialog):
    def __init__(self, topics, parent=None):
        super(KonuSecmeDialog, self).__init__(parent)
        self.setWindowTitle("Konuyu Seç")
        self.setGeometry(200, 200, 300, 200)
        
        layout = QVBoxLayout()
        self.topic_list = QListWidget(self)
        for topic in topics:
            self.topic_list.addItem(topic)
        layout.addWidget(self.topic_list)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_selected_topic(self):
        selected_item = self.topic_list.currentItem()
        if selected_item:
            return selected_item.text()
        return None

class FlashKartUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.db_conn = sqlite3.connect("flash_kart.db")
        self.init_db()
        self.initUI()
    
    def init_db(self):
        cursor = self.db_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                topic_id INTEGER,
                FOREIGN KEY(topic_id) REFERENCES topics(id)
            )
        """)
        self.db_conn.commit()
    
    def initUI(self):
        self.setWindowTitle('Flash Kart Uygulaması')
        self.setGeometry(100, 100, 600, 400)
        
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabBarDoubleClicked.connect(self.sekme_ismini_duzenle)
        self.tab_widget.tabCloseRequested.connect(self.sekme_kapat)
        self.setCentralWidget(self.tab_widget)
        
        self.load_topics()
        
        menubar = self.menuBar()
        kart_menu = menubar.addMenu('Kartlar')
        
        yeni_action = QAction("Yeni Konu Ekle", self)
        yeni_action.setShortcut("Ctrl+N")
        yeni_action.triggered.connect(self.yeni_konu_ekle)
        kart_menu.addAction(yeni_action)
        
        sekme_duzenle_action = QAction("Sekme İsmini Düzenle", self)
        sekme_duzenle_action.setShortcut("Ctrl+E")
        sekme_duzenle_action.triggered.connect(self.sekme_ismini_duzenle)
        kart_menu.addAction(sekme_duzenle_action)

        konu_ac_action = QAction("Konuyu Aç", self)
        konu_ac_action.setShortcut("Ctrl+O")
        konu_ac_action.triggered.connect(self.konu_ac)
        kart_menu.addAction(konu_ac_action)
        
        # QSS stili uygula
        self.setStyleSheet(self.qss_stili())
        
        self.show()
    
    def load_topics(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT id, name FROM topics")
        rows = cursor.fetchall()
        for row in rows:
            topic_id, name = row
            self.yeni_kart_ekle(topic_id, name)
    
    def yeni_konu_ekle(self):
        name, ok = QInputDialog.getText(self, "Yeni Konu", "Konu İsmi:")
        if ok and name:
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO topics (name) VALUES (?)", (name,))
            self.db_conn.commit()
            topic_id = cursor.lastrowid
            self.yeni_kart_ekle(topic_id, name)

    def konu_ac(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT name FROM topics")
        topics = [row[0] for row in cursor.fetchall()]
        dialog = KonuSecmeDialog(topics, self)
        if dialog.exec_() == QDialog.Accepted:
            konu = dialog.get_selected_topic()
            if konu:
                cursor.execute("SELECT id FROM topics WHERE name=?", (konu,))
                topic_id = cursor.fetchone()[0]
                self.yeni_kart_ekle(topic_id, konu)
    
    def yeni_kart_ekle(self, topic_id=None, name=None):
        if topic_id is None or name is None:
            return
        
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == name:
                self.tab_widget.setCurrentIndex(i)
                return
        
        yeni_sekme = FlashKartSekmesi(self.db_conn, topic_id)
        self.tab_widget.addTab(yeni_sekme, name)
        self.tab_widget.setCurrentWidget(yeni_sekme)
    
    def sekme_ismini_duzenle(self, index=None):
        if index is None:
            index = self.tab_widget.currentIndex()
        
        if index >= 0:
            current_name = self.tab_widget.tabText(index)
            yeni_isim, ok = QInputDialog.getText(self, "Sekme İsmini Düzenle", "Yeni isim girin:", text=current_name)
            if ok and yeni_isim:
                self.tab_widget.setTabText(index, yeni_isim)
                topic_id = self.tab_widget.widget(index).topic_id
                cursor = self.db_conn.cursor()
                cursor.execute("UPDATE topics SET name = ? WHERE id = ?", (yeni_isim, topic_id))
                self.db_conn.commit()
    
    def sekme_kapat(self, index):
        topic_id = self.tab_widget.widget(index).topic_id
        self.db_conn.commit()
        self.tab_widget.removeTab(index)
    
    def qss_stili(self):
        return """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QTabWidget::pane {
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        QTabBar::tab {
            background: #ddd;
            border: 1px solid #ccc;
            border-bottom: none;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            padding: 5px;
            margin-right: 1px;
        }
        QTabBar::tab:selected {
            background: #f0f0f0;
            border-color: #999;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3e8e41;
        }
        QListWidget {
            font-size: 16px;
        }
        QLabel {
            font-size: 24px;
        }
        """
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    flash_kart_uygulamasi = FlashKartUygulamasi()
    sys.exit(app.exec_())
