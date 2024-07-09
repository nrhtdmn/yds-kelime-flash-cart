import sys
import sqlite3
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QTabWidget, QMessageBox, QAction, QInputDialog, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt

class FlashKartSekmesi(QWidget):
    def __init__(self, db_conn, konu_id, parent=None):
        super(FlashKartSekmesi, self).__init__(parent)
        
        self.db_conn = db_conn
        self.konu_id = konu_id
        self.arayuzuOlustur()
        self.kartlariYukle()
    
    def arayuzuOlustur(self):
        layout = QVBoxLayout()
        
        self.kart_listesi = QListWidget(self)
        self.kart_listesi.itemDoubleClicked.connect(self.kartiDuzenle)
        layout.addWidget(self.kart_listesi)
        
        buton_layout = QHBoxLayout()
        
        self.ekle_butonu = QPushButton("Ekle", self)
        self.ekle_butonu.setFixedSize(100, 40)
        self.ekle_butonu.setStyleSheet("font-size: 18px;")
        self.ekle_butonu.clicked.connect(self.kartEkle)
        buton_layout.addWidget(self.ekle_butonu, alignment=Qt.AlignCenter)
        
        self.sil_butonu = QPushButton("Sil", self)
        self.sil_butonu.setFixedSize(100, 40)
        self.sil_butonu.setStyleSheet("font-size: 18px;")
        self.sil_butonu.clicked.connect(self.kartiSil)
        buton_layout.addWidget(self.sil_butonu, alignment=Qt.AlignCenter)

        self.calistir_butonu = QPushButton("Çalış", self)
        self.calistir_butonu.setFixedSize(100, 40)
        self.calistir_butonu.setStyleSheet("font-size: 18px;")
        self.calistir_butonu.clicked.connect(self.kartlariCalistir)
        buton_layout.addWidget(self.calistir_butonu, alignment=Qt.AlignCenter)
        
        self.kaydet_butonu = QPushButton("Kaydet", self)
        self.kaydet_butonu.setFixedSize(100, 40)
        self.kaydet_butonu.setStyleSheet("font-size: 18px;")
        self.kaydet_butonu.clicked.connect(self.tumKartlariKaydet)
        buton_layout.addWidget(self.kaydet_butonu, alignment=Qt.AlignCenter)
        
        layout.addLayout(buton_layout)
        
        self.setLayout(layout)
        
    def kartEkle(self):
        on_yuz, ok1 = QInputDialog.getText(self, "Yeni Kart", "Ön Yüz:")
        if ok1 and on_yuz:
            arka_yuz, ok2 = QInputDialog.getText(self, "Yeni Kart", "Arka Yüz:")
            if ok2 and arka_yuz:
                kart = f"Ön: {on_yuz}\nArka: {arka_yuz}"
                liste_ogesi = QListWidgetItem(kart)
                self.kart_listesi.addItem(liste_ogesi)
                self.kartiVeritabaninaKaydet(on_yuz, arka_yuz)
    
    def kartiDuzenle(self, item):
        kart = item.text().split('\n')
        on_yuz = kart[0].split(': ')[1]
        arka_yuz = kart[1].split(': ')[1]
        
        yeni_on_yuz, ok1 = QInputDialog.getText(self, "Kartı Düzenle", "Ön Yüz:", text=on_yuz)
        if ok1 and yeni_on_yuz:
            yeni_arka_yuz, ok2 = QInputDialog.getText(self, "Kartı Düzenle", "Arka Yüz:", text=arka_yuz)
            if ok2 and yeni_arka_yuz:
                yeni_kart = f"Ön: {yeni_on_yuz}\nArka: {yeni_arka_yuz}"
                item.setText(yeni_kart)
                self.kartiVeritabanindaGuncelle(on_yuz, arka_yuz, yeni_on_yuz, yeni_arka_yuz)
    
    def kartiSil(self):
        secili_ogeyi = self.kart_listesi.currentItem()
        if secili_ogeyi:
            cevap = QMessageBox.question(self, 'Silme Onayı', 'Bu kartı silmek istediğinize emin misiniz?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if cevap == QMessageBox.Yes:
                kart = secili_ogeyi.text().split('\n')
                on_yuz = kart[0].split(': ')[1]
                arka_yuz = kart[1].split(': ')[1]
                self.kartiVeritabanindanSil(on_yuz, arka_yuz)
                self.kart_listesi.takeItem(self.kart_listesi.currentRow())

    def kartlariYukle(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT front, back FROM cards WHERE topic_id=?", (self.konu_id,))
        rows = cursor.fetchall()
        for row in rows:
            on_yuz, arka_yuz = row
            kart = f"Ön: {on_yuz}\nArka: {arka_yuz}"
            liste_ogesi = QListWidgetItem(kart)
            self.kart_listesi.addItem(liste_ogesi)
    
    def kartiVeritabaninaKaydet(self, on_yuz, arka_yuz):
        cursor = self.db_conn.cursor()
        cursor.execute("INSERT INTO cards (front, back, topic_id) VALUES (?, ?, ?)", (on_yuz, arka_yuz, self.konu_id))
        self.db_conn.commit()
    
    def kartiVeritabanindaGuncelle(self, eski_on_yuz, eski_arka_yuz, yeni_on_yuz, yeni_arka_yuz):
        cursor = self.db_conn.cursor()
        cursor.execute("UPDATE cards SET front = ?, back = ? WHERE front = ? AND back = ? AND topic_id = ?", (yeni_on_yuz, yeni_arka_yuz, eski_on_yuz, eski_arka_yuz, self.konu_id))
        self.db_conn.commit()
    
    def kartiVeritabanindanSil(self, on_yuz, arka_yuz):
        cursor = self.db_conn.cursor()
        cursor.execute("DELETE FROM cards WHERE front = ? AND back = ? AND topic_id = ?", (on_yuz, arka_yuz, self.konu_id))
        self.db_conn.commit()

    def kartlariCalistir(self):
        self.calisma_penceresi = CalismaPenceresi(self.db_conn, self.konu_id)
        self.calisma_penceresi.show()

    def tumKartlariKaydet(self):
        self.db_conn.commit()
        QMessageBox.information(self, "Başarılı", "Tüm kartlar kaydedildi.")

class CalismaPenceresi(QWidget):
    def __init__(self, db_conn, konu_id, parent=None):
        super(CalismaPenceresi, self).__init__(parent)
        
        self.db_conn = db_conn
        self.konu_id = konu_id
        self.arayuzuOlustur()
        self.kartlariYukle()
    
    def arayuzuOlustur(self):
        self.setWindowTitle('Flash Kart Çalışma')
        self.setGeometry(150, 150, 400, 300)
        
        layout = QVBoxLayout()
        
        self.kart_etiketi = QLabel("", self)
        self.kart_etiketi.setAlignment(Qt.AlignCenter)
        self.kart_etiketi.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.kart_etiketi)
        
        buton_layout = QHBoxLayout()
        
        self.on_yuz_goster_butonu = QPushButton("Ön Yüzü Göster", self)
        self.on_yuz_goster_butonu.setFixedSize(150, 40)
        self.on_yuz_goster_butonu.setStyleSheet("font-size: 18px;")
        self.on_yuz_goster_butonu.clicked.connect(self.onYuzuGoster)
        buton_layout.addWidget(self.on_yuz_goster_butonu, alignment=Qt.AlignCenter)

        self.arka_yuz_goster_butonu = QPushButton("Arka Yüzü Göster", self)
        self.arka_yuz_goster_butonu.setFixedSize(150, 40)
        self.arka_yuz_goster_butonu.setStyleSheet("font-size: 18px;")
        self.arka_yuz_goster_butonu.clicked.connect(self.arkaYuzuGoster)
        buton_layout.addWidget(self.arka_yuz_goster_butonu, alignment=Qt.AlignCenter)
        
        self.sonraki_buton = QPushButton("Sonraki", self)
        self.sonraki_buton.setFixedSize(100, 40)
        self.sonraki_buton.setStyleSheet("font-size: 18px;")
        self.sonraki_buton.clicked.connect(self.sonrakiKart)
        buton_layout.addWidget(self.sonraki_buton, alignment=Qt.AlignCenter)
        
        layout.addLayout(buton_layout)
        
        self.setLayout(layout)
        
        self.kartlar = []
        self.guncel_kart_indeksi = -1
    
    def kartlariYukle(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT front, back FROM cards WHERE topic_id=?", (self.konu_id,))
        self.kartlar = cursor.fetchall()
        random.shuffle(self.kartlar)
        self.sonrakiKart()
    
    def onYuzuGoster(self):
        if self.guncel_kart_indeksi >= 0:
            self.kart_etiketi.setText(self.kartlar[self.guncel_kart_indeksi][0])

    def arkaYuzuGoster(self):
        if self.guncel_kart_indeksi >= 0:
            self.kart_etiketi.setText(self.kartlar[self.guncel_kart_indeksi][1])
    
    def sonrakiKart(self):
        if len(self.kartlar) == 0:
            QMessageBox.warning(self, "Uyarı", "Bu konuda hiç kart yok.")
            return
        self.guncel_kart_indeksi += 1
        if self.guncel_kart_indeksi >= len(self.kartlar):
            cevap = QMessageBox.question(self, 'Bitti', 'Tüm kartlar gösterildi. Yeniden başlatmak ister misiniz?', QMessageBox.Yes | QMessageBox.No)
            if cevap == QMessageBox.Yes:
                self.guncel_kart_indeksi = 0
            else:
                self.close()
                return
        self.kart_etiketi.setText(self.kartlar[self.guncel_kart_indeksi][0])

class KonuSecmeDialog(QDialog):
    def __init__(self, db_conn, parent=None):
        super(KonuSecmeDialog, self).__init__(parent)
        self.setWindowTitle("Konuyu Seç")
        self.setGeometry(200, 200, 300, 300)
        
        self.db_conn = db_conn
        
        layout = QVBoxLayout()
        
        self.konu_listesi = QListWidget(self)
        self.konu_listesi.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.konu_listesi)
        
        self.konulariYukle()
        
        buton_layout = QHBoxLayout()
        
        self.sil_butonu = QPushButton("Sil", self)
        self.sil_butonu.setFixedSize(100, 40)
        self.sil_butonu.setStyleSheet("font-size: 18px;")
        self.sil_butonu.clicked.connect(self.konuSil)
        buton_layout.addWidget(self.sil_butonu, alignment=Qt.AlignCenter)
        
        self.ac_butonu = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.ac_butonu.accepted.connect(self.accept)
        self.ac_butonu.rejected.connect(self.reject)
        buton_layout.addWidget(self.ac_butonu)
        
        layout.addLayout(buton_layout)
        
        self.setLayout(layout)
    
    def konulariYukle(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT name FROM topics")
        konular = [row[0] for row in cursor.fetchall()]
        self.konu_listesi.clear()
        for konu in konular:
            self.konu_listesi.addItem(konu)
    
    def konuSil(self):
        secili_ogeyi = self.konu_listesi.currentItem()
        if secili_ogeyi:
            cevap = QMessageBox.question(self, 'Silme Onayı', 'Bu konuyu silmek istediğinize emin misiniz?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if cevap == QMessageBox.Yes:
                konu_adi = secili_ogeyi.text()
                cursor = self.db_conn.cursor()
                cursor.execute("SELECT id FROM topics WHERE name=?", (konu_adi,))
                konu_id = cursor.fetchone()[0]
                cursor.execute("DELETE FROM topics WHERE id=?", (konu_id,))
                cursor.execute("DELETE FROM cards WHERE topic_id=?", (konu_id,))
                self.db_conn.commit()
                self.konulariYukle()
    
    def seciliKonuyuAl(self):
        secili_ogeyi = self.konu_listesi.currentItem()
        if secili_ogeyi:
            return secili_ogeyi.text()
        return None

class FlashKartUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.db_conn = sqlite3.connect("flash_kart.db")
        self.veritabaniOlustur()
        self.arayuzuOlustur()
    
    def veritabaniOlustur(self):
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
    
    def arayuzuOlustur(self):
        self.setWindowTitle('Flash Kart Uygulaması')
        self.setGeometry(100, 100, 600, 400)
        
        self.sekme_widgeti = QTabWidget(self)
        self.sekme_widgeti.setTabsClosable(True)
        self.sekme_widgeti.tabBarDoubleClicked.connect(self.sekmeIsminiDuzenle)
        self.sekme_widgeti.tabCloseRequested.connect(self.sekmeKapat)
        self.setCentralWidget(self.sekme_widgeti)
        
        self.konulariYukle()
        
        menubar = self.menuBar()
        kart_menu = menubar.addMenu('Kartlar')
        
        yeni_action = QAction("Yeni Konu Ekle", self)
        yeni_action.setShortcut("Ctrl+N")
        yeni_action.triggered.connect(self.yeniKonuEkle)
        kart_menu.addAction(yeni_action)
        
        sekme_duzenle_action = QAction("Sekme İsmini Düzenle", self)
        sekme_duzenle_action.setShortcut("Ctrl+E")
        sekme_duzenle_action.triggered.connect(self.sekmeIsminiDuzenle)
        kart_menu.addAction(sekme_duzenle_action)

        konu_ac_action = QAction("Konuyu Aç", self)
        konu_ac_action.setShortcut("Ctrl+O")
        konu_ac_action.triggered.connect(self.konuAc)
        kart_menu.addAction(konu_ac_action)
        
        # QSS stili uygula
        self.setStyleSheet(self.qssStili())
        
        self.show()
    
    def konulariYukle(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT id, name FROM topics")
        rows = cursor.fetchall()
        for row in rows:
            konu_id, ad = row
            self.yeniSekmeEkle(konu_id, ad)
    
    def yeniKonuEkle(self):
        ad, ok = QInputDialog.getText(self, "Yeni Konu", "Konu İsmi:")
        if ok and ad:
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO topics (name) VALUES (?)", (ad,))
            self.db_conn.commit()
            konu_id = cursor.lastrowid
            self.yeniSekmeEkle(konu_id, ad)

    def konuAc(self):
        dialog = KonuSecmeDialog(self.db_conn, self)
        if dialog.exec_() == QDialog.Accepted:
            konu = dialog.seciliKonuyuAl()
            if konu:
                cursor = self.db_conn.cursor()
                cursor.execute("SELECT id FROM topics WHERE name=?", (konu,))
                konu_id = cursor.fetchone()[0]
                self.yeniSekmeEkle(konu_id, konu)
    
    def yeniSekmeEkle(self, konu_id=None, ad=None):
        if konu_id is None or ad is None:
            return
        
        for i in range(self.sekme_widgeti.count()):
            if self.sekme_widgeti.tabText(i) == ad:
                self.sekme_widgeti.setCurrentIndex(i)
                return
        
        yeni_sekme = FlashKartSekmesi(self.db_conn, konu_id)
        self.sekme_widgeti.addTab(yeni_sekme, ad)
        self.sekme_widgeti.setCurrentWidget(yeni_sekme)
    
    def sekmeIsminiDuzenle(self, index=None):
        if index is None:
            index = self.sekme_widgeti.currentIndex()
        
        if index >= 0:
            mevcut_isim = self.sekme_widgeti.tabText(index)
            yeni_isim, ok = QInputDialog.getText(self, "Sekme İsmini Düzenle", "Yeni isim girin:", text=mevcut_isim)
            if ok and yeni_isim:
                self.sekme_widgeti.setTabText(index, yeni_isim)
                konu_id = self.sekme_widgeti.widget(index).konu_id
                cursor = self.db_conn.cursor()
                cursor.execute("UPDATE topics SET name = ? WHERE id = ?", (yeni_isim, konu_id))
                self.db_conn.commit()
    
    def sekmeKapat(self, index):
        konu_id = self.sekme_widgeti.widget(index).konu_id
        self.db_conn.commit()
        self.sekme_widgeti.removeTab(index)
    
    def qssStili(self):
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
