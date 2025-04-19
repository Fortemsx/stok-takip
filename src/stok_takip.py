import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sqlite3
import os
import locale
from tkcalendar import DateEntry
import shutil
import pandas as pd


# Solar tema renkleri (modernleştirilmiş)
BG_COLOR = "#002b36"       # Koyu arka plan
PRIMARY_COLOR = "#268bd2"   # Mavi (daha canlı)
SECONDARY_COLOR = "#859900" # Yeşil
DANGER_COLOR = "#dc322f"    # Kırmızı
WARNING_COLOR = "#b58900"   # Sarı
TEXT_COLOR = "#eee8d5"      # Açık bej
ENTRY_BG = "#073642"        # Giriş alanları arkaplan
BUTTON_HOVER = "#1e6ea7"    # Buton hover
CARD_COLOR = "#073642"      # Kart arkaplan
SELECTION_COLOR = "#586e75" # Seçim rengi
BUTTON_TEXT = "#fdf6e3"     # Buton yazı rengi
BORDER_COLOR = "#0a5460"    # Kenarlık rengi
ACCENT_COLOR = "#d33682"    # Pembe (vurgu)
SIDEBAR_COLOR = "#1a2a34"   # Sidebar rengi
SIDEBAR_TEXT = "#eee8d5"    # Sidebar yazı reğni

# Font ayarları
FONT_PRIMARY = ("Segoe UI", 10)
FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SIDEBAR = ("Segoe UI", 11)

class StopTakipPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Temelli Stok Takip")
        self.root.geometry("1366x768")
        self.root.state('zoomed')
        
        # Stil ayarları
        self.style = ttk.Style()
        self._configure_styles()
        
        # Veritabanı bağlantısı
        self.db_path = os.path.join(os.path.dirname(__file__), "stop_takip.db")
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        self._create_database()
        
        # Arayüz bileşenleri
        self._setup_ui()
        self._load_data()
        
    def _load_data(self):
        """Verileri yüklemek için genel metod"""
        self._load_hareket_raporu()
        self._load_categories()
        self._update_dashboard()
        self._update_malzeme_listesi()
        self._load_mevcut_stok()  # Mevcut stok verilerini yükle

    def _configure_styles(self):
        """Tema ve stil ayarlarını yapar"""
        self.style.theme_use("clam")  # Solar tema için en uygun tema
        
        # Genel ayarlar
        self.style.configure(".", 
                          background=BG_COLOR, 
                          foreground=TEXT_COLOR, 
                          font=FONT_PRIMARY,
                          insertcolor=TEXT_COLOR,
                          borderwidth=1)
        
        # Frame stilleri
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("Card.TFrame", 
                           background=CARD_COLOR,
                           relief=tk.RAISED,
                           borderwidth=1,
                           bordercolor=BORDER_COLOR,
                           padding=10)
        
        # Sidebar frame
        self.style.configure("Sidebar.TFrame",
                           background=SIDEBAR_COLOR)
        
        # Label stilleri
        self.style.configure("TLabel", 
                           background=BG_COLOR, 
                           foreground=TEXT_COLOR,
                           font=FONT_PRIMARY)
        self.style.configure("Header.TLabel",
                           font=FONT_HEADER,
                           foreground=PRIMARY_COLOR)
        self.style.configure("Accent.TLabel",
                           foreground=ACCENT_COLOR)
        self.style.configure("Sidebar.TLabel",
                           background=SIDEBAR_COLOR,
                           foreground=SIDEBAR_TEXT,
                           font=FONT_SIDEBAR)
        self.style.configure("Title.TLabel",
                           font=FONT_TITLE,
                           foreground=TEXT_COLOR)
        
        # Entry stilleri
        self.style.configure("TEntry", 
                           fieldbackground=ENTRY_BG, 
                           foreground=TEXT_COLOR,
                           insertcolor=TEXT_COLOR,
                           font=FONT_PRIMARY,
                           bordercolor=BORDER_COLOR,
                           lightcolor=ENTRY_BG,
                           darkcolor=ENTRY_BG,
                           padding=8,
                           relief=tk.SOLID)
        
        # Combobox stilleri
        self.style.configure("TCombobox", 
                           fieldbackground=ENTRY_BG,
                           foreground=TEXT_COLOR,
                           background=BG_COLOR,
                           selectbackground=SELECTION_COLOR,
                           selectforeground=TEXT_COLOR,
                           arrowcolor=PRIMARY_COLOR,
                           bordercolor=BORDER_COLOR,
                           padding=6,
                           relief=tk.SOLID)
        
        # Buton stilleri
        self.style.configure("TButton",
                           font=FONT_BUTTON,
                           borderwidth=1,
                           foreground=BUTTON_TEXT,
                           background=PRIMARY_COLOR,
                           focuscolor=BG_COLOR,
                           padding=10,
                           relief=tk.RAISED)
        
        # Sidebar butonları
        self.style.configure("Sidebar.TButton",
                          font=FONT_SIDEBAR,
                          background=SIDEBAR_COLOR,
                          foreground=SIDEBAR_TEXT,
                          borderwidth=1,
                          padding=(10, 15),
                          anchor="w")
        
        # Buton efektleri
        self.style.map("Primary.TButton",
            foreground=[('active', BUTTON_TEXT), ('!active', BUTTON_TEXT)],
            background=[('active', BUTTON_HOVER), ('!active', PRIMARY_COLOR)],
            bordercolor=[('active', PRIMARY_COLOR), ('!active', PRIMARY_COLOR)])
        
        self.style.map("Success.TButton",
            foreground=[('active', BUTTON_TEXT), ('!active', BUTTON_TEXT)],
            background=[('active', '#738a05'), ('!active', SECONDARY_COLOR)],
            bordercolor=[('active', SECONDARY_COLOR), ('!active', SECONDARY_COLOR)])
        
        self.style.map("Danger.TButton",
            foreground=[('active', BUTTON_TEXT), ('!active', BUTTON_TEXT)],
            background=[('active', '#a32724'), ('!active', DANGER_COLOR)],
            bordercolor=[('active', DANGER_COLOR), ('!active', DANGER_COLOR)])
        
        self.style.map("Warning.TButton",
            foreground=[('active', TEXT_COLOR), ('!active', TEXT_COLOR)],
            background=[('active', '#9d7503'), ('!active', WARNING_COLOR)],
            bordercolor=[('active', WARNING_COLOR), ('!active', WARNING_COLOR)])
        
        self.style.map("Sidebar.TButton",
            background=[('active', PRIMARY_COLOR), ('!active', SIDEBAR_COLOR)],
            foreground=[('active', BUTTON_TEXT), ('!active', SIDEBAR_TEXT)],
            bordercolor=[('active', PRIMARY_COLOR), ('!active', SIDEBAR_COLOR)])
        
        # Treeview stil
        self.style.configure("Treeview",
            background=ENTRY_BG,
            foreground=TEXT_COLOR,
            rowheight=32,
            fieldbackground=ENTRY_BG,
            font=FONT_PRIMARY,
            bordercolor=BORDER_COLOR,
            lightcolor=BG_COLOR,
            darkcolor=BG_COLOR,
            padding=5,
            relief=tk.SOLID)
        
        self.style.configure("Treeview.Heading",
            font=FONT_BUTTON,
            background=PRIMARY_COLOR,
            foreground=BUTTON_TEXT,
            relief=tk.RAISED,
            padding=8)
        
        self.style.map("Treeview",
            background=[('selected', SELECTION_COLOR)],
            foreground=[('selected', TEXT_COLOR)])
        
        # DateEntry stili
        self.style.configure("DateEntry", 
                           fieldbackground=ENTRY_BG, 
                           foreground=TEXT_COLOR, 
                           background=BG_COLOR, 
                           arrowcolor=PRIMARY_COLOR,
                           selectbackground=SELECTION_COLOR,
                           bordercolor=BORDER_COLOR)
        
        # Scrollbar stili
        self.style.configure("Vertical.TScrollbar",
                           background=PRIMARY_COLOR,
                           troughcolor=CARD_COLOR,
                           arrowcolor=BUTTON_TEXT,
                           bordercolor=BORDER_COLOR)
        
        # Listbox stili
        self.style.configure("Listbox",
                           background=ENTRY_BG,
                           foreground=TEXT_COLOR,
                           selectbackground=SELECTION_COLOR,
                           selectforeground=TEXT_COLOR,
                           font=FONT_PRIMARY,
                           bordercolor=BORDER_COLOR,
                           relief=tk.SOLID)
        
        # Notebook (tab) stili
        self.style.configure("TNotebook",
                           background=BG_COLOR,
                           bordercolor=BORDER_COLOR)
        self.style.configure("TNotebook.Tab",
                           background=BG_COLOR,
                           foreground=TEXT_COLOR,
                           padding=[12, 4],
                           font=FONT_BUTTON)
        self.style.map("TNotebook.Tab",
                     background=[("selected", CARD_COLOR)],
                     foreground=[("selected", PRIMARY_COLOR)],
                     bordercolor=[("selected", PRIMARY_COLOR)])

    def _setup_ui(self):
        """Arayüz bileşenlerini oluşturur"""
        # Ana container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, ipadx=10)
        
        # Logo alanı
        logo_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        logo_frame.pack(pady=(20, 30), fill=tk.X)
        
        # Logo (metin olarak)
        self.logo = ttk.Label(logo_frame, text="Stok Takip", 
                            style="Sidebar.TLabel", font=("Segoe UI", 14, "bold"))
        self.logo.pack()
        
        # Sidebar menü butonları
        menu_items = [
            ("📊 Dashboard", self._show_dashboard),
            ("📦 Malzeme Ekle", lambda: self.notebook.select(0)),
            ("➖ Malzeme Çıktı", lambda: self.notebook.select(1)),
            ("🏭 Depo Takip", lambda: self.notebook.select(2)),
            ("📈 Aylık Rapor", lambda: self.notebook.select(3)),
            ("⚙️ Ayarlar", lambda: self.notebook.select(4))
        ]
        
        for text, command in menu_items:
            btn = ttk.Button(self.sidebar, text=text, 
                           style="Sidebar.TButton", command=command)
            btn.pack(fill=tk.X, pady=(0, 5))
        
        # Çıkış butonu
        exit_btn = ttk.Button(self.sidebar, text="🚪 Çıkış", 
                            style="Sidebar.TButton", command=self.root.quit)
        exit_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 20))
        
        # Ana içerik alanı
        self.content = ttk.Frame(self.main_container)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Ana notebook (sekmeler)
        self.notebook = ttk.Notebook(self.content)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Malzeme Ekleme Sekmesi
        self._setup_malzeme_ekleme()
        
        # Malzeme Çıktı Sekmesi
        self._setup_malzeme_cikti()
        
        # Depo Takip Sekmesi (Yeniden düzenlenmiş)
        self._setup_depo_takip()
        
        # Aylık Rapor Sekmesi
        self._setup_aylik_rapor()
        
        # Ayarlar Sekmesi
        self._setup_ayarlar()
        
        # Dashboard (başlangıçta gizli)
        self._setup_dashboard()

    def _show_dashboard(self):
        """Dashboard'ı gösterir"""
        self.notebook.pack_forget()
        self.dashboard.pack(fill=tk.BOTH, expand=True)
        self._update_dashboard()
        
    def _setup_dashboard(self):
        """Dashboard panelini oluşturur"""
        self.dashboard = ttk.Frame(self.content, style="Card.TFrame")
        
        # Başlık
        ttk.Label(self.dashboard, text="DASHBOARD", style="Title.TLabel").pack(pady=20)
        
        # İstatistik kartları
        stats_frame = ttk.Frame(self.dashboard)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        stats = [
            {"title": "Toplam Malzeme", "value": "0", "color": PRIMARY_COLOR, "icon": "📦"},
            {"title": "Düşük Stok", "value": "0", "color": WARNING_COLOR, "icon": "⚠️"},
            {"title": "Toplam Maliyet", "value": "0 ₺", "color": SECONDARY_COLOR, "icon": "💰"},
            {"title": "Kategori Sayısı", "value": "0", "color": ACCENT_COLOR, "icon": "🏷️"}
        ]
        
        for stat in stats:
            card = ttk.Frame(stats_frame, style="Card.TFrame", padding=15)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            icon = ttk.Label(card, text=stat["icon"], font=("Segoe UI", 24))
            icon.pack()
            
            value = ttk.Label(card, text=stat["value"], style="Header.TLabel", 
                            foreground=stat["color"], font=("Segoe UI", 18, "bold"))
            value.pack()
            
            title = ttk.Label(card, text=stat["title"], style="TLabel")
            title.pack()
            
            setattr(self, f"dashboard_{stat['title'].lower().replace(' ', '_')}", value)
        
        # Grafik alanı (simüle edilmiş)
        chart_frame = ttk.Frame(self.dashboard, style="Card.TFrame", height=300)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(chart_frame, text="Stok Hareketleri Grafiği", 
                 style="Header.TLabel").pack(pady=50)
        
    def _update_dashboard(self):
        """Dashboard verilerini günceller"""
        # Toplam malzeme
        self.c.execute("SELECT SUM(adet) FROM malzeme_girisleri")
        total = self.c.fetchone()[0] or 0
        self.dashboard_toplam_malzeme.config(text=str(total))
        
        # Düşük stok (varsayılan olarak 10'dan az)
        self.c.execute("SELECT COUNT(*) FROM malzeme_girisleri WHERE adet < 10")
        low_stock = self.c.fetchone()[0] or 0
        self.dashboard_düşük_stok.config(text=str(low_stock))
        
        # Toplam maliyet
        self.c.execute("SELECT SUM(toplam) FROM malzeme_girisleri")
        total_cost = self.c.fetchone()[0] or 0
        self.dashboard_toplam_maliyet.config(text=f"{total_cost:.2f} ₺")
        
        # Kategori sayısı
        self.c.execute("SELECT COUNT(DISTINCT kategori) FROM malzeme_girisleri WHERE kategori IS NOT NULL")
        categories = self.c.fetchone()[0] or 0
        self.dashboard_kategori_sayısı.config(text=str(categories))

    def _create_database(self):
        """Veritabanı tablosunu oluşturur"""
        # Eski tabloları sil
        self.c.execute("DROP TABLE IF EXISTS malzeme_girisleri")
        self.c.execute("DROP TABLE IF EXISTS malzeme_cikislari")
        self.c.execute("DROP TABLE IF EXISTS mevcut_stok")
    
        # Yeni tabloları oluştur
        self.c.execute('''CREATE TABLE IF NOT EXISTS malzeme_girisleri
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           ad TEXT NOT NULL,
                           fiyat REAL NOT NULL,
                           adet INTEGER NOT NULL,
                           kdv REAL NOT NULL,
                           toplam REAL NOT NULL,
                           tarih TEXT NOT NULL,
                           kategori TEXT,
                           tedarikci TEXT)''')
    
        self.c.execute('''CREATE TABLE IF NOT EXISTS malzeme_cikislari
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           giris_id INTEGER NOT NULL,
                           malzeme_adi TEXT NOT NULL,
                           cikis_adedi INTEGER NOT NULL,
                           personel TEXT NOT NULL,
                           tarih TEXT NOT NULL,
                           FOREIGN KEY(giris_id) REFERENCES malzeme_girisleri(id))''')
    
        self.c.execute('''CREATE TABLE IF NOT EXISTS mevcut_stok
                          (malzeme_adi TEXT PRIMARY KEY,
                           toplam_adet INTEGER NOT NULL)''')
        self.conn.commit()

    def _setup_malzeme_ekleme(self):
        """Malzeme ekleme sekmesini oluşturur"""
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(frame, text="➕ Malzeme Ekle")
        
        # Başlık
        ttk.Label(frame, text="YENİ MALZEME EKLE", style="Title.TLabel").pack(pady=(20, 10))
        
        # Form alanları
        form_frame = ttk.Frame(frame, style="Card.TFrame", padding=30)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        fields = [
            ("Malzeme Adı:", "entry_ad"),
            ("Birim Fiyat (₺):", "entry_fiyat"),
            ("Adet:", "entry_adet"),
            ("KDV Oranı (%):", "entry_kdv"),
            ("Tarih:", "entry_tarih"),
            ("Kategori:", "entry_kategori"),
            ("Tedarikçi:", "entry_tedarikci")
        ]
        
        for i, (label, var_name) in enumerate(fields):
            row_frame = ttk.Frame(form_frame)
            row_frame.grid(row=i, column=0, sticky="ew", pady=10)
            
            ttk.Label(row_frame, text=label, width=15, anchor="e", 
                     style="TLabel").pack(side=tk.LEFT, padx=10)
            
            if label == "Tarih:":
                entry = DateEntry(row_frame, width=24, background='darkblue',
                                foreground='white', borderwidth=2, date_pattern='dd.MM.yyyy',
                                font=FONT_PRIMARY)
                entry.set_date(datetime.now())
            elif label == "Kategori:":
                entry = ttk.Combobox(row_frame, width=27, font=FONT_PRIMARY)
                # Kategorileri yükle
                self.c.execute("SELECT DISTINCT kategori FROM malzeme_girisleri WHERE kategori IS NOT NULL")
                categories = [cat[0] for cat in self.c.fetchall()]
                entry['values'] = categories
            elif label == "Malzeme Adı:":
                entry = ttk.Combobox(row_frame, width=30, font=FONT_PRIMARY)
                # Malzeme adlarını yükle
                self.c.execute("SELECT DISTINCT ad FROM malzeme_girisleri WHERE ad IS NOT NULL")
                malzemeler = [malzeme[0] for malzeme in self.c.fetchall()]
                entry['values'] = malzemeler
                # Otomatik tamamlama
                entry.bind('<KeyRelease>', lambda event: self._autocomplete(event, 'ad'))
            elif label == "Tedarikçi:":
                entry = ttk.Combobox(row_frame, width=30, font=FONT_PRIMARY)
                # Tedarikçileri yükle
                self.c.execute("SELECT DISTINCT tedarikci FROM malzeme_girisleri WHERE tedarikci IS NOT NULL")
                tedarikciler = [tedarikci[0] for tedarikci in self.c.fetchall()]
                entry['values'] = tedarikciler
                # Otomatik tamamlama
                entry.bind('<KeyRelease>', lambda event: self._autocomplete(event, 'tedarikci'))
            else:
                entry = ttk.Entry(row_frame, width=30, font=FONT_PRIMARY)
            
            setattr(self, var_name, entry)
            entry.pack(side=tk.LEFT, padx=10)
            
            if label == "KDV Oranı (%):":
                entry.insert(0, "20")  # Varsayılan KDV
        
        # Butonlar
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields)+1, column=0, pady=(30, 10))
        
        ttk.Button(btn_frame, text="Temizle", style="Warning.TButton",
                  command=self._temizle_form).pack(side=tk.LEFT, padx=20, ipadx=20, ipady=8)
        ttk.Button(btn_frame, text="Kaydet", style="Success.TButton",
                  command=self.malzeme_ekle).pack(side=tk.LEFT, padx=20, ipadx=25, ipady=8)

    def _setup_malzeme_cikti(self):
        """Malzeme çıktı sekmesini oluşturur"""
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(frame, text="➖ Malzeme Çıktı")
        
        # Başlık
        ttk.Label(frame, text="MALZEME ÇIKIŞI", style="Title.TLabel").pack(pady=(20, 10))
        
        # Form alanları
        form_frame = ttk.Frame(frame, style="Card.TFrame", padding=30)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Malzeme seçimi
        row_frame = ttk.Frame(form_frame)
        row_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(row_frame, text="Malzeme Seçin:", width=15, anchor="e", 
                 style="TLabel").pack(side=tk.LEFT, padx=10)
        
        self.cikti_malzeme = ttk.Combobox(row_frame, width=30, font=FONT_PRIMARY)
        self.cikti_malzeme.pack(side=tk.LEFT, padx=10)
        
        # Mevcut stok bilgisi
        self.stok_bilgisi = ttk.Label(row_frame, text="Mevcut Stok: -", style="Accent.TLabel")
        self.stok_bilgisi.pack(side=tk.LEFT, padx=20)
        
        # Malzeme seçildiğinde stok bilgisini güncelle
        self.cikti_malzeme.bind('<<ComboboxSelected>>', self._update_stok_bilgisi)
        
        # Personel bilgisi
        row_frame = ttk.Frame(form_frame)
        row_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(row_frame, text="Personel Ad-Soyad:", width=15, anchor="e", 
                 style="TLabel").pack(side=tk.LEFT, padx=10)
        
        self.cikti_personel = ttk.Entry(row_frame, width=30, font=FONT_PRIMARY)
        self.cikti_personel.pack(side=tk.LEFT, padx=10)
        
        # Çıkış miktarı
        row_frame = ttk.Frame(form_frame)
        row_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(row_frame, text="Çıkış Miktarı:", width=15, anchor="e", 
                 style="TLabel").pack(side=tk.LEFT, padx=10)
        
        self.cikti_miktar = ttk.Entry(row_frame, width=30, font=FONT_PRIMARY)
        self.cikti_miktar.pack(side=tk.LEFT, padx=10)
        
        # Tarih
        row_frame = ttk.Frame(form_frame)
        row_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(row_frame, text="Tarih:", width=15, anchor="e", 
                 style="TLabel").pack(side=tk.LEFT, padx=10)
        
        self.cikti_tarih = DateEntry(row_frame, width=24, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='dd.MM.yyyy',
                                   font=FONT_PRIMARY)
        self.cikti_tarih.set_date(datetime.now())
        self.cikti_tarih.pack(side=tk.LEFT, padx=10)
        
        # Butonlar
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=(30, 10))
        
        ttk.Button(btn_frame, text="Temizle", style="Warning.TButton",
                  command=self._temizle_cikti_form).pack(side=tk.LEFT, padx=20, ipadx=20, ipady=8)
        ttk.Button(btn_frame, text="Çıkış Yap", style="Danger.TButton",
                  command=self.malzeme_cikisi_yap).pack(side=tk.LEFT, padx=20, ipadx=25, ipady=8)
        
        # Malzeme listesini güncelle
        self._update_malzeme_listesi()

    def _update_malzeme_listesi(self):
        """Malzeme çıktı sekmesindeki malzeme listesini günceller"""
        self.c.execute("SELECT malzeme_adi, toplam_adet FROM mevcut_stok WHERE toplam_adet > 0 ORDER BY malzeme_adi")
        malzemeler = [f"{row[0]} (Stok: {row[1]})" for row in self.c.fetchall()]
        self.cikti_malzeme['values'] = malzemeler

    def _update_stok_bilgisi(self, event=None):
        """Seçili malzemenin stok bilgisini gösterir"""
        selected = self.cikti_malzeme.get()
        if not selected:
            return
            
        # Malzeme adını al (parantezden önceki kısım)
        malzeme_adi = selected.split(' (Stok:')[0].strip()
        
        # Veritabanından stok bilgisini al
        self.c.execute("SELECT toplam_adet FROM mevcut_stok WHERE malzeme_adi=?", (malzeme_adi,))
        result = self.c.fetchone()
        
        if result:
            self.stok_bilgisi.config(text=f"Mevcut Stok: {result[0]}")
        else:
            self.stok_bilgisi.config(text="Mevcut Stok: -")

    def _temizle_cikti_form(self):
        """Çıktı formunu temizler"""
        self.cikti_malzeme.set('')
        self.cikti_personel.delete(0, tk.END)
        self.cikti_miktar.delete(0, tk.END)
        self.cikti_tarih.set_date(datetime.now())
        self.stok_bilgisi.config(text="Mevcut Stok: -")

    def malzeme_cikisi_yap(self):
        """Malzeme çıkış işlemini gerçekleştirir"""
        try:
            # Form verilerini al
            selected = self.cikti_malzeme.get()
            personel = self.cikti_personel.get().strip()
            miktar = int(self.cikti_miktar.get())
            tarih = self.cikti_tarih.get()
        
            if not selected:
                messagebox.showerror("Hata", "Malzeme seçiniz!")
                return
            
            if not personel:
                messagebox.showerror("Hata", "Personel bilgisi giriniz!")
                return
            
            if miktar <= 0:
                messagebox.showerror("Hata", "Geçerli bir miktar giriniz!")
                return
        
            # Malzeme adını al (parantezden önceki kısım)
            malzeme_adi = selected.split(' (Stok:')[0].strip()
        
            # Mevcut stok kontrolü
            self.c.execute("SELECT toplam_adet FROM mevcut_stok WHERE malzeme_adi=?", (malzeme_adi,))
            result = self.c.fetchone()
        
            if not result or result[0] < miktar:
                messagebox.showerror("Hata", f"Yetersiz stok! Mevcut stok: {result[0] if result else 0}")
                return
        
            # En eski giriş kaydını bul (FIFO yöntemi)
            self.c.execute(
               "SELECT id, adet FROM malzeme_girisleri "
                "WHERE ad=? AND adet > 0 ORDER BY tarih ASC LIMIT 1",
                (malzeme_adi,)
            )
            giris_kaydi = self.c.fetchone()
        
            if not giris_kaydi:
                messagebox.showerror("Hata", "Stok kaydı bulunamadı!")
                return
            
            giris_id, giris_adet = giris_kaydi
        
            # Çıkış kaydı oluştur
            self.c.execute(
                "INSERT INTO malzeme_cikislari (giris_id, malzeme_adi, cikis_adedi, personel, tarih) VALUES (?, ?, ?, ?, ?)",
                (giris_id, malzeme_adi, miktar, personel, tarih)
            )
        
            # Mevcut stok güncelleme
            self.c.execute(
                "UPDATE mevcut_stok SET toplam_adet = toplam_adet - ? WHERE malzeme_adi=?",
                (miktar, malzeme_adi)
            )
        
            self.conn.commit()
        
            messagebox.showinfo("Başarılı", f"{malzeme_adi} malzemesinden {miktar} adet çıkış yapıldı.")
        
            # Formu temizle ve verileri yenile
            self._temizle_cikti_form()
            self._update_malzeme_listesi()
            self._load_data()
    
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz miktar! Sayı giriniz.")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu:\n{str(e)}")   

    def _temizle_form(self):
        """Formu temizler"""
        self.entry_ad.delete(0, tk.END)
        self.entry_fiyat.delete(0, tk.END)
        self.entry_adet.delete(0, tk.END)
        self.entry_kdv.delete(0, tk.END)
        self.entry_kdv.insert(0, "20")  # Varsayılan KDV
        self.entry_tarih.set_date(datetime.now())
        self.entry_kategori.set('')
        self.entry_tedarikci.delete(0, tk.END)
        self.entry_ad.focus_set()

    def _autocomplete(self, event, field_type):
        """Otomatik tamamlama işlemini gerçekleştirir"""
        widget = event.widget
        text = widget.get()
    
        if field_type == 'ad':
            self.c.execute("SELECT DISTINCT ad FROM malzeme_girisleri WHERE ad LIKE ?", (f'%{text}%',))
            values = [row[0] for row in self.c.fetchall()]
        elif field_type == 'tedarikci':
            self.c.execute("SELECT DISTINCT tedarikci FROM malzeme_girisleri WHERE tedarikci LIKE ?", (f'%{text}%',))
            values = [row[0] for row in self.c.fetchall()]
    
        widget['values'] = values
    
    def malzeme_ekle(self):
        """Yeni malzeme ekler"""
        try:
            ad = self.entry_ad.get().strip()
            fiyat = float(self.entry_fiyat.get())
            adet = int(self.entry_adet.get())
            kdv_orani = float(self.entry_kdv.get()) / 100
            tarih = self.entry_tarih.get()
            kategori = self.entry_kategori.get().strip()
            tedarikci = self.entry_tedarikci.get().strip()
        
            if not ad:
                messagebox.showerror("Hata", "Malzeme adı boş olamaz!")
                return
        
            # KDV dahil toplam
            toplam = (fiyat * adet) * (1 + kdv_orani)
        
            # Veritabanına ekle
            self.c.execute(
                "INSERT INTO malzeme_girisleri (ad, fiyat, adet, kdv, toplam, tarih, kategori, tedarikci) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ad, fiyat, adet, kdv_orani, toplam, tarih, kategori if kategori else None, tedarikci if tedarikci else None)
            )
        
            # Mevcut stok güncelleme
            self.c.execute(
                "INSERT OR REPLACE INTO mevcut_stok (malzeme_adi, toplam_adet) "
                "VALUES (?, COALESCE((SELECT toplam_adet FROM mevcut_stok WHERE malzeme_adi=?), 0) + ?)",
                (ad, ad, adet)
            )
        
            self.conn.commit()
        
            messagebox.showinfo("Başarılı", f"{ad} malzemesi başarıyla eklendi!\nToplam: {toplam:.2f} ₺")
        
            # Formu temizle ve verileri yenile
            self._temizle_form()
            self._load_data()
        
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri girişi!\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu!\n{str(e)}")

    def _setup_depo_takip(self):
        """Depo takip sekmesini yeniden düzenler (basitleştirilmiş versiyon)"""
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(frame, text="📦 Depo Takip")
        
        # Notebook oluştur (alt sekmeler için)
        self.depo_notebook = ttk.Notebook(frame)
        self.depo_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Hareket Raporu Sekmesi
        self._setup_hareket_raporu_tab()
        
        # Mevcut Stok Sekmesi
        self._setup_mevcut_stok_tab()

    def _setup_hareket_raporu_tab(self):
        """Hareket raporu alt sekmesini oluşturur"""
        tab = ttk.Frame(self.depo_notebook, style="Card.TFrame")
        self.depo_notebook.add(tab, text="Hareket Raporu")
        
        # Başlık
        ttk.Label(tab, text="DEPO HAREKET RAPORU", style="Title.TLabel").pack(pady=(10, 15))
        
        # Filtreleme paneli
        filter_frame = ttk.LabelFrame(tab, text="Filtreleme Seçenekleri", 
                                    style="Card.TFrame", padding=(15, 10))
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Tarih filtreleri
        ttk.Label(filter_frame, text="Başlangıç Tarihi:", style="TLabel").grid(row=0, column=0, padx=5, pady=5)
        self.hareket_baslangic_tarih = DateEntry(filter_frame, width=15, background='darkblue',
                                               foreground='white', borderwidth=2, date_pattern='dd.MM.yyyy',
                                               font=FONT_PRIMARY)
        self.hareket_baslangic_tarih.grid(row=0, column=1, padx=5, pady=5)
        self.hareket_baslangic_tarih.set_date(datetime.now().replace(day=1))  # Ayın ilk günü
        
        ttk.Label(filter_frame, text="Bitiş Tarihi:", style="TLabel").grid(row=0, column=2, padx=5, pady=5)
        self.hareket_bitis_tarih = DateEntry(filter_frame, width=15, background='darkblue',
                                            foreground='white', borderwidth=2, date_pattern='dd.MM.yyyy',
                                            font=FONT_PRIMARY)
        self.hareket_bitis_tarih.grid(row=0, column=3, padx=5, pady=5)
        
        # Kategori filtre
        ttk.Label(filter_frame, text="Kategori:", style="TLabel").grid(row=0, column=4, padx=5, pady=5)
        self.kategori_filtre = ttk.Combobox(filter_frame, width=20, font=FONT_PRIMARY)
        self.kategori_filtre.grid(row=0, column=5, padx=5, pady=5)
        
        # Malzeme adı filtre
        ttk.Label(filter_frame, text="Malzeme Adı:", style="TLabel").grid(row=1, column=0, padx=5, pady=5)
        self.malzeme_filtre = ttk.Combobox(filter_frame, width=20, font=FONT_PRIMARY)
        self.malzeme_filtre.grid(row=1, column=1, padx=5, pady=5)
        self.malzeme_filtre.bind('<KeyRelease>', lambda event: self._autocomplete(event, 'ad'))
        
        # Hareket türü filtre
        ttk.Label(filter_frame, text="Hareket Türü:", style="TLabel").grid(row=1, column=2, padx=5, pady=5)
        self.hareket_turu_filtre = ttk.Combobox(filter_frame, width=20, font=FONT_PRIMARY)
        self.hareket_turu_filtre['values'] = ['Tümü', 'Giriş', 'Çıkış']
        self.hareket_turu_filtre.current(0)
        self.hareket_turu_filtre.grid(row=1, column=3, padx=5, pady=5)
        
        # Filtrele butonu
        ttk.Button(filter_frame, text="Filtrele", style="Primary.TButton",
                  command=self._filter_hareket_raporu).grid(row=1, column=4, padx=10, ipadx=10, ipady=3)
        ttk.Button(filter_frame, text="Filtreyi Temizle", style="Warning.TButton",
                  command=self._clear_hareket_filter).grid(row=1, column=5, padx=5, ipadx=10, ipady=3)
        
        # Tablo
        self.hareket_tree_frame = ttk.Frame(tab, style="Card.TFrame", padding=10)
        self.hareket_tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview sütunları
        columns = [
            ("Tarih", 120),
            ("Malzeme Adı", 200),
            ("Hareket Türü", 100),
            ("Miktar", 100),
            ("Birim Fiyat", 100),
            ("Toplam Maliyet", 120),
            ("Personel/Tedarikçi", 200),
            ("Kategori", 150)
        ]
        
        self.hareket_tree = ttk.Treeview(
            self.hareket_tree_frame, 
            columns=[col[0] for col in columns],
            show="headings",
            selectmode="extended"
        )
        
        # Sütun başlıkları ve genişlikleri
        for col, width in columns:
            self.hareket_tree.heading(col, text=col)
            self.hareket_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.hareket_tree_frame, orient=tk.VERTICAL, command=self.hareket_tree.yview)
        self.hareket_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hareket_tree.pack(fill=tk.BOTH, expand=True)
        
        # Toplam paneli
        self.hareket_total_frame = ttk.Frame(tab, style="Card.TFrame", padding=(15, 10))
        self.hareket_total_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(self.hareket_total_frame, text="Toplam Giriş:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.label_toplam_giris = ttk.Label(self.hareket_total_frame, text="0", style="Header.TLabel", foreground=SECONDARY_COLOR)
        self.label_toplam_giris.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.hareket_total_frame, text="Toplam Çıkış:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.label_toplam_cikis = ttk.Label(self.hareket_total_frame, text="0", style="Header.TLabel", foreground=DANGER_COLOR)
        self.label_toplam_cikis.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.hareket_total_frame, text="Toplam Maliyet:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.label_toplam_maliyet = ttk.Label(self.hareket_total_frame, text="0.00 ₺", style="Header.TLabel", foreground=ACCENT_COLOR)
        self.label_toplam_maliyet.pack(side=tk.LEFT, padx=5)
        
        # Butonlar
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Excel'e Aktar", style="Success.TButton",
                  command=lambda: self._export_excel(self.hareket_tree)).pack(side=tk.LEFT, padx=10, ipadx=15, ipady=5)
        ttk.Button(btn_frame, text="Güncelle", style="Primary.TButton",
                  command=self._load_hareket_raporu).pack(side=tk.RIGHT, padx=10, ipadx=15, ipady=5)
        
        # İlk yükleme
        self._load_hareket_raporu()
        self._load_categories()

    def _load_hareket_raporu(self):
        """Hareket raporu verilerini yükler"""
        # Treeview'ı temizle
        for row in self.hareket_tree.get_children():
            self.hareket_tree.delete(row)
        
        # Filtreleri al
        baslangic_tarih = self.hareket_baslangic_tarih.get()
        bitis_tarih = self.hareket_bitis_tarih.get()
        kategori = self.kategori_filtre.get()
        malzeme = self.malzeme_filtre.get()
        hareket_turu = self.hareket_turu_filtre.get()
        
        # Giriş hareketlerini sorgula
        giris_query = """
        SELECT 
            mg.tarih AS tarih,
            mg.ad AS malzeme_adi,
            'Giriş' AS hareket_turu,
            mg.adet AS miktar,
            mg.fiyat AS birim_fiyat,
            mg.toplam AS toplam_maliyet,
            COALESCE(mg.tedarikci, 'Belirtilmemiş') AS tedarikci,
            COALESCE(mg.kategori, 'Kategorisiz') AS kategori
        FROM malzeme_girisleri mg
        WHERE mg.tarih BETWEEN ? AND ?
        """
        
        giris_params = [baslangic_tarih, bitis_tarih]
        
        if kategori:
            giris_query += " AND mg.kategori = ?"
            giris_params.append(kategori)
        
        if malzeme:
            giris_query += " AND mg.ad LIKE ?"
            giris_params.append(f'%{malzeme}%')
        
        # Çıkış hareketlerini sorgula
        cikis_query = """
        SELECT 
            mc.tarih AS tarih,
            mc.malzeme_adi AS malzeme_adi,
            'Çıkış' AS hareket_turu,
            mc.cikis_adedi AS miktar,
            (SELECT mg.fiyat FROM malzeme_girisleri mg WHERE mg.id = mc.giris_id) AS birim_fiyat,
            (mc.cikis_adedi * (SELECT mg.fiyat FROM malzeme_girisleri mg WHERE mg.id = mc.giris_id)) AS toplam_maliyet,
            mc.personel AS personel,
            (SELECT COALESCE(mg.kategori, 'Kategorisiz') FROM malzeme_girisleri mg WHERE mg.id = mc.giris_id) AS kategori
        FROM malzeme_cikislari mc
        WHERE mc.tarih BETWEEN ? AND ?
        """
        
        cikis_params = [baslangic_tarih, bitis_tarih]
        
        if kategori:
            cikis_query += " AND EXISTS (SELECT 1 FROM malzeme_girisleri mg WHERE mg.id = mc.giris_id AND mg.kategori = ?)"
            cikis_params.append(kategori)
        
        if malzeme:
            cikis_query += " AND mc.malzeme_adi LIKE ?"
            cikis_params.append(f'%{malzeme}%')
        
        # Hareket türüne göre sorguyu belirle
        if hareket_turu == 'Giriş':
            query = giris_query
            params = giris_params
        elif hareket_turu == 'Çıkış':
            query = cikis_query
            params = cikis_params
        else:  # Tümü
            query = giris_query + " UNION ALL " + cikis_query
            params = giris_params + cikis_params
        
        query += " ORDER BY tarih DESC"
        
        self.c.execute(query, params)
        rows = self.c.fetchall()
        
        toplam_giris = 0
        toplam_cikis = 0
        toplam_maliyet = 0.0
        
        for row in rows:
            self.hareket_tree.insert("", tk.END, values=row)
            
            if row[2] == 'Giriş':
                toplam_giris += row[3]
                toplam_maliyet += row[5] if row[5] else 0
            else:
                toplam_cikis += row[3]
        
        # Toplamları güncelle
        self.label_toplam_giris.config(text=str(toplam_giris))
        self.label_toplam_cikis.config(text=str(toplam_cikis))
        self.label_toplam_maliyet.config(text=f"{toplam_maliyet:.2f} ₺")

    def _setup_mevcut_stok_tab(self):
        """Mevcut stok alt sekmesini oluşturur"""
        tab = ttk.Frame(self.depo_notebook, style="Card.TFrame")
        self.depo_notebook.add(tab, text="Mevcut Stok")
        
        # Başlık
        ttk.Label(tab, text="MEVCUT STOK DURUMU", style="Title.TLabel").pack(pady=(10, 15))
        
        # Filtreleme paneli
        filter_frame = ttk.LabelFrame(tab, text="Filtreleme Seçenekleri", 
                                    style="Card.TFrame", padding=(15, 10))
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Kategori filtre
        ttk.Label(filter_frame, text="Kategori:", style="TLabel").grid(row=0, column=0, padx=5, pady=5)
        self.stok_kategori_filtre = ttk.Combobox(filter_frame, width=20, font=FONT_PRIMARY)
        self.stok_kategori_filtre.grid(row=0, column=1, padx=5, pady=5)
        
        # Malzeme adı filtre
        ttk.Label(filter_frame, text="Malzeme Adı:", style="TLabel").grid(row=0, column=2, padx=5, pady=5)
        self.stok_malzeme_filtre = ttk.Combobox(filter_frame, width=20, font=FONT_PRIMARY)
        self.stok_malzeme_filtre.grid(row=0, column=3, padx=5, pady=5)
        
        # Stok durumu filtre
        ttk.Label(filter_frame, text="Stok Durumu:", style="TLabel").grid(row=0, column=4, padx=5, pady=5)
        self.stok_durumu_filtre = ttk.Combobox(filter_frame, width=20, font=FONT_PRIMARY)
        self.stok_durumu_filtre['values'] = ['Tümü', 'Düşük Stok (<10)', 'Normal Stok']
        self.stok_durumu_filtre.current(0)
        self.stok_durumu_filtre.grid(row=0, column=5, padx=5, pady=5)
        
        # Filtrele butonu
        ttk.Button(filter_frame, text="Filtrele", style="Primary.TButton",
                  command=self._filter_mevcut_stok).grid(row=0, column=6, padx=10, ipadx=10, ipady=3)
        ttk.Button(filter_frame, text="Filtreyi Temizle", style="Warning.TButton",
                  command=self._clear_stok_filter).grid(row=0, column=7, padx=5, ipadx=10, ipady=3)
        
        # Tablo
        self.stok_tree_frame = ttk.Frame(tab, style="Card.TFrame", padding=10)
        self.stok_tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview sütunları
        columns = [
            ("Malzeme Adı", 250),
            ("Kategori", 150),
            ("Mevcut Stok", 100),
            ("Birim Fiyat (₺)", 120),
            ("Toplam Maliyet (₺)", 150),
            ("Tedarikçi", 200),
            ("Son Giriş Tarihi", 120)
        ]
        
        self.stok_tree = ttk.Treeview(
            self.stok_tree_frame, 
            columns=[col[0] for col in columns],
            show="headings",
            selectmode="extended"
        )
        
        # Sütun başlıkları ve genişlikleri
        for col, width in columns:
            self.stok_tree.heading(col, text=col)
            self.stok_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.stok_tree_frame, orient=tk.VERTICAL, command=self.stok_tree.yview)
        self.stok_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stok_tree.pack(fill=tk.BOTH, expand=True)
        
        # Toplam paneli
        self.stok_total_frame = ttk.Frame(tab, style="Card.TFrame", padding=(15, 10))
        self.stok_total_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(self.stok_total_frame, text="Toplam Malzeme:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.stok_label_toplam_malzeme = ttk.Label(self.stok_total_frame, text="0", style="Header.TLabel", foreground=PRIMARY_COLOR)
        self.stok_label_toplam_malzeme.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.stok_total_frame, text="Toplam Maliyet:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.stok_label_toplam_maliyet = ttk.Label(self.stok_total_frame, text="0.00 ₺", style="Header.TLabel", foreground=SECONDARY_COLOR)
        self.stok_label_toplam_maliyet.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.stok_total_frame, text="Düşük Stok:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.stok_label_dusuk_stok = ttk.Label(self.stok_total_frame, text="0", style="Header.TLabel", foreground=DANGER_COLOR)
        self.stok_label_dusuk_stok.pack(side=tk.LEFT, padx=5)
        
        # Butonlar
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Excel'e Aktar", style="Success.TButton",
                  command=lambda: self._export_excel(self.stok_tree)).pack(side=tk.LEFT, padx=10, ipadx=15, ipady=5)
        ttk.Button(btn_frame, text="Güncelle", style="Primary.TButton",
                  command=self._load_mevcut_stok).pack(side=tk.RIGHT, padx=10, ipadx=15, ipady=5)
        
        # İlk yükleme
        self._load_mevcut_stok()
        self._load_categories()

    def _load_mevcut_stok(self):
        """Mevcut stok verilerini yükler"""
        # Treeview'ı temizle
        for row in self.stok_tree.get_children():
            self.stok_tree.delete(row)
    
        # Filtreleri al
        kategori = self.stok_kategori_filtre.get()
        malzeme = self.stok_malzeme_filtre.get()
        stok_durumu = self.stok_durumu_filtre.get()
    
        # Sorguyu oluştur
        query = """
        SELECT 
            ms.malzeme_adi AS malzeme_adi,
            COALESCE((SELECT kategori FROM malzeme_girisleri WHERE ad=ms.malzeme_adi LIMIT 1), 'Kategorisiz') AS kategori,
            ms.toplam_adet AS mevcut_stok,
            (SELECT fiyat FROM malzeme_girisleri WHERE ad=ms.malzeme_adi ORDER BY tarih DESC LIMIT 1) AS birim_fiyat,
            (ms.toplam_adet * (SELECT fiyat FROM malzeme_girisleri WHERE ad=ms.malzeme_adi ORDER BY tarih DESC LIMIT 1)) AS toplam_maliyet,
            COALESCE((SELECT tedarikci FROM malzeme_girisleri WHERE ad=ms.malzeme_adi ORDER BY tarih DESC LIMIT 1), 'Belirtilmemiş') AS tedarikci,
            (SELECT MAX(tarih) FROM malzeme_girisleri WHERE ad=ms.malzeme_adi) AS son_giris_tarihi
        FROM mevcut_stok ms
        WHERE ms.toplam_adet > 0
        """
    
        params = []
    
        if kategori:
            query += " AND EXISTS (SELECT 1 FROM malzeme_girisleri mg WHERE mg.ad=ms.malzeme_adi AND mg.kategori = ?)"
            params.append(kategori)
    
        if malzeme:
            query += " AND ms.malzeme_adi LIKE ?"
            params.append(f'%{malzeme}%')
    
        if stok_durumu == 'Düşük Stok (<10)':
            query += " AND ms.toplam_adet < 10"
        elif stok_durumu == 'Normal Stok':
            query += " AND ms.toplam_adet >= 10"
    
        query += " ORDER BY ms.malzeme_adi"
    
        self.c.execute(query, params)
        rows = self.c.fetchall()
    
        total_malzeme = 0
        total_maliyet = 0.0
        dusuk_stok = 0
    
        for row in rows:
            self.stok_tree.insert("", tk.END, values=row)
            total_malzeme += row[2]
            total_maliyet += row[4] if row[4] else 0
            if row[2] < 10:
                dusuk_stok += 1
    
        # Toplamları güncelle
        self.stok_label_toplam_malzeme.config(text=str(total_malzeme))
        self.stok_label_toplam_maliyet.config(text=f"{total_maliyet:.2f} ₺")
        self.stok_label_dusuk_stok.config(text=str(dusuk_stok))   

    def _filter_hareket_raporu(self):
        """Hareket raporu verilerini filtreler"""
        self._load_hareket_raporu()

    def _filter_mevcut_stok(self):
        """Mevcut stok verilerini filtreler"""
        self._load_mevcut_stok()

    def _clear_hareket_filter(self):
        """Hareket raporu filtrelerini temizler"""
        self.hareket_baslangic_tarih.set_date(datetime.now().replace(day=1))
        self.hareket_bitis_tarih.set_date(datetime.now())
        self.kategori_filtre.set('')
        self.malzeme_filtre.set('')
        self.hareket_turu_filtre.current(0)
        self._load_hareket_raporu()

    def _clear_stok_filter(self):
        """Stok filtrelerini temizler"""
        self.stok_kategori_filtre.set('')
        self.stok_malzeme_filtre.set('')
        self.stok_durumu_filtre.current(0)
        self._load_mevcut_stok()

    def _setup_aylik_rapor(self):
        """Aylık rapor sekmesini oluşturur"""
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(frame, text="📈 Aylık Rapor")
        
        # Başlık
        ttk.Label(frame, text="AYLIK MALZEME HAREKET RAPORU", style="Title.TLabel").pack(pady=(10, 15))
        
        # Filtreleme paneli
        filter_frame = ttk.LabelFrame(frame, text="Filtreleme Seçenekleri", 
                                    style="Card.TFrame", padding=(15, 10))
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Yıl seçimi
        ttk.Label(filter_frame, text="Yıl:", style="TLabel").grid(row=0, column=0, padx=5, pady=5)
        self.aylik_yil_filtre = ttk.Combobox(filter_frame, width=10, font=FONT_PRIMARY)
        self.aylik_yil_filtre['values'] = [str(year) for year in range(2020, datetime.now().year + 3)]
        self.aylik_yil_filtre.set(str(datetime.now().year))
        self.aylik_yil_filtre.grid(row=0, column=1, padx=5, pady=5)
        
        # Kategori filtre
        ttk.Label(filter_frame, text="Kategori:", style="TLabel").grid(row=0, column=2, padx=5, pady=5)
        self.aylik_kategori_filtre = ttk.Combobox(filter_frame, width=20, font=FONT_PRIMARY)
        self.aylik_kategori_filtre.grid(row=0, column=3, padx=5, pady=5)
        
        # Malzeme adı filtre
        ttk.Label(filter_frame, text="Malzeme Adı:", style="TLabel").grid(row=0, column=4, padx=5, pady=5)
        self.aylik_malzeme_filtre = ttk.Combobox(filter_frame, width=20, font=FONT_PRIMARY)
        self.aylik_malzeme_filtre.grid(row=0, column=5, padx=5, pady=5)
        
        # Filtrele butonu
        ttk.Button(filter_frame, text="Filtrele", style="Primary.TButton",
                  command=self._filter_aylik_rapor).grid(row=0, column=6, padx=10, ipadx=10, ipady=3)
        ttk.Button(filter_frame, text="Filtreyi Temizle", style="Warning.TButton",
                  command=self._clear_aylik_filter).grid(row=0, column=7, padx=5, ipadx=10, ipady=3)
        
        # Tablo
        self.aylik_tree_frame = ttk.Frame(frame, style="Card.TFrame", padding=10)
        self.aylik_tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview sütunları
        columns = [
            ("Ay", 150),
            ("Giriş Miktarı", 120),
            ("Çıkış Miktarı", 120),
            ("Net Değişim", 120),
            ("Toplam Maliyet (₺)", 150)
        ]
        
        self.aylik_tree = ttk.Treeview(
            self.aylik_tree_frame, 
            columns=[col[0] for col in columns],
            show="headings",
            selectmode="extended"
        )
        
        # Sütun başlıkları ve genişlikleri
        for col, width in columns:
            self.aylik_tree.heading(col, text=col)
            self.aylik_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.aylik_tree_frame, orient=tk.VERTICAL, command=self.aylik_tree.yview)
        self.aylik_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.aylik_tree.pack(fill=tk.BOTH, expand=True)
        
        # Toplam paneli
        self.aylik_total_frame = ttk.Frame(frame, style="Card.TFrame", padding=(15, 10))
        self.aylik_total_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(self.aylik_total_frame, text="Yıllık Toplam Giriş:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.aylik_label_toplam_giris = ttk.Label(self.aylik_total_frame, text="0", style="Header.TLabel", foreground=SECONDARY_COLOR)
        self.aylik_label_toplam_giris.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.aylik_total_frame, text="Yıllık Toplam Çıkış:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.aylik_label_toplam_cikis = ttk.Label(self.aylik_total_frame, text="0", style="Header.TLabel", foreground=DANGER_COLOR)
        self.aylik_label_toplam_cikis.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.aylik_total_frame, text="Yıllık Net Değişim:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.aylik_label_net_degisim = ttk.Label(self.aylik_total_frame, text="0", style="Header.TLabel", foreground=PRIMARY_COLOR)
        self.aylik_label_net_degisim.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.aylik_total_frame, text="Yıllık Toplam Maliyet:", style="Header.TLabel").pack(side=tk.LEFT, padx=20)
        self.aylik_label_toplam_maliyet = ttk.Label(self.aylik_total_frame, text="0.00 ₺", style="Header.TLabel", foreground=ACCENT_COLOR)
        self.aylik_label_toplam_maliyet.pack(side=tk.LEFT, padx=5)
        
        # Butonlar
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Excel'e Aktar", style="Success.TButton",
                  command=lambda: self._export_excel(self.aylik_tree)).pack(side=tk.LEFT, padx=10, ipadx=15, ipady=5)
        ttk.Button(btn_frame, text="Güncelle", style="Primary.TButton",
                  command=self._load_aylik_rapor).pack(side=tk.RIGHT, padx=10, ipadx=15, ipady=5)
        
        # İlk yükleme
        self._load_aylik_rapor()
        self._load_categories()

    def _load_aylik_rapor(self):
        """Aylık rapor verilerini yükler"""
        # Treeview'ı temizle
        for row in self.aylik_tree.get_children():
            self.aylik_tree.delete(row)
        
        # Yıl ve filtreleri al
        yil = self.aylik_yil_filtre.get()
        kategori = self.aylik_kategori_filtre.get()
        malzeme = self.aylik_malzeme_filtre.get()
        
        try:
            yil = int(yil)
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz yıl değeri!")
            return
        
        # Ayları tanımla
        aylar = [
            ("Ocak", 1), ("Şubat", 2), ("Mart", 3), ("Nisan", 4), 
            ("Mayıs", 5), ("Haziran", 6), ("Temmuz", 7), ("Ağustos", 8), 
            ("Eylül", 9), ("Ekim", 10), ("Kasım", 11), ("Aralık", 12)
        ]
        
        # Her ay için verileri topla
        yillik_toplam_giris = 0
        yillik_toplam_cikis = 0
        yillik_toplam_maliyet = 0.0
        
        for ay_adi, ay_no in aylar:
            # Ayın başlangıç ve bitiş tarihleri
            baslangic_tarih = datetime(yil, ay_no, 1).strftime("%d.%m.%Y")
            
            if ay_no == 12:
                bitis_tarih = datetime(yil, ay_no, 31).strftime("%d.%m.%Y")
            else:
                bitis_tarih = datetime(yil, ay_no+1, 1).strftime("%d.%m.%Y")
            
            # Giriş sorgusu
            giris_query = """
            SELECT 
                SUM(mg.adet) AS toplam_giris,
                SUM(mg.toplam) AS toplam_maliyet
            FROM malzeme_girisleri mg
            WHERE mg.tarih BETWEEN ? AND ?
            """
            
            giris_params = [baslangic_tarih, bitis_tarih]
            
            if kategori:
                giris_query += " AND mg.kategori = ?"
                giris_params.append(kategori)
            
            if malzeme:
                giris_query += " AND mg.ad LIKE ?"
                giris_params.append(f'%{malzeme}%')
            
            self.c.execute(giris_query, giris_params)
            giris_result = self.c.fetchone()
            toplam_giris = giris_result[0] or 0
            toplam_maliyet = giris_result[1] or 0.0
            
            # Çıkış sorgusu
            cikis_query = """
            SELECT 
                SUM(mc.cikis_adedi) AS toplam_cikis
            FROM malzeme_cikislari mc
            WHERE mc.tarih BETWEEN ? AND ?
            """
            
            cikis_params = [baslangic_tarih, bitis_tarih]
            
            if kategori:
                cikis_query += " AND EXISTS (SELECT 1 FROM malzeme_girisleri mg WHERE mg.id = mc.giris_id AND mg.kategori = ?)"
                cikis_params.append(kategori)
            
            if malzeme:
                cikis_query += " AND mc.malzeme_adi LIKE ?"
                cikis_params.append(f'%{malzeme}%')
            
            self.c.execute(cikis_query, cikis_params)
            cikis_result = self.c.fetchone()
            toplam_cikis = cikis_result[0] or 0
            
            # Toplamları hesapla
            net_degisim = toplam_giris - toplam_cikis
            
            # Treeview'a ekle
            self.aylik_tree.insert("", tk.END, values=(
                ay_adi,
                toplam_giris,
                toplam_cikis,
                net_degisim,
                f"{toplam_maliyet:.2f}"
            ))
            
            # Yıllık toplamlara ekle
            yillik_toplam_giris += toplam_giris
            yillik_toplam_cikis += toplam_cikis
            yillik_toplam_maliyet += toplam_maliyet
        
        # Yıllık toplamları güncelle
        self.aylik_label_toplam_giris.config(text=str(yillik_toplam_giris))
        self.aylik_label_toplam_cikis.config(text=str(yillik_toplam_cikis))
        self.aylik_label_net_degisim.config(text=str(yillik_toplam_giris - yillik_toplam_cikis))
        self.aylik_label_toplam_maliyet.config(text=f"{yillik_toplam_maliyet:.2f} ₺")

    def _filter_aylik_rapor(self):
        """Aylık rapor verilerini filtreler"""
        self._load_aylik_rapor()

    def _clear_aylik_filter(self):
        """Aylık rapor filtrelerini temizler"""
        self.aylik_yil_filtre.set(str(datetime.now().year))
        self.aylik_kategori_filtre.set('')
        self.aylik_malzeme_filtre.set('')
        self._load_aylik_rapor()

    def _setup_ayarlar(self):
        """Ayarlar sekmesini oluşturur"""
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(frame, text="⚙️ Ayarlar")
        
        # Başlık
        ttk.Label(frame, text="AYARLAR PANELİ", style="Title.TLabel").pack(pady=(10, 20))
        
        # KDV oranı ayarı
        kdv_frame = ttk.LabelFrame(frame, text="KDV Ayarları", 
                                 style="Card.TFrame", padding=(15, 10))
        kdv_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(kdv_frame, text="Varsayılan KDV Oranı (%):", style="TLabel").pack(side=tk.LEFT, padx=5, pady=5)
        self.default_kdv = ttk.Entry(kdv_frame, width=5, font=FONT_PRIMARY)
        self.default_kdv.pack(side=tk.LEFT, padx=5, pady=5)
        self.default_kdv.insert(0, "20")
        
        ttk.Button(kdv_frame, text="Kaydet", style="Success.TButton",
                  command=self._save_settings).pack(side=tk.LEFT, padx=20, ipadx=15, ipady=3)
        
        # Veritabanı yönetimi
        db_frame = ttk.LabelFrame(frame, text="Veritabanı Yönetimi", 
                                style="Card.TFrame", padding=(15, 10))
        db_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(db_frame, text="Yedek Al", style="Primary.TButton",
                  command=self._backup_db).pack(side=tk.LEFT, padx=10, ipadx=15, ipady=5)
        ttk.Button(db_frame, text="Yedekten Geri Yükle", style="Warning.TButton",
                  command=self._restore_db).pack(side=tk.LEFT, padx=10, ipadx=15, ipady=5)
        ttk.Button(db_frame, text="Verileri Temizle", style="Danger.TButton",
                  command=self._clear_db).pack(side=tk.LEFT, padx=10, ipadx=15, ipady=5)
        
        # Kategoriler
        cat_frame = ttk.LabelFrame(frame, text="Kategori Yönetimi", 
                                 style="Card.TFrame", padding=(15, 10))
        cat_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        
        # Yeni kategori ekleme
        add_frame = ttk.Frame(cat_frame)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_frame, text="Yeni Kategori:", style="TLabel").pack(side=tk.LEFT, padx=5)
        self.new_category = ttk.Entry(add_frame, width=25, font=FONT_PRIMARY)
        self.new_category.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_frame, text="Ekle", style="Success.TButton",
                  command=self._add_category).pack(side=tk.LEFT, padx=10, ipadx=15, ipady=3)
        
        # Kategori listesi
        list_frame = ttk.Frame(cat_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.category_list = tk.Listbox(list_frame, height=12, font=FONT_PRIMARY, 
                                      bg=ENTRY_BG, fg=TEXT_COLOR,
                                      selectbackground=SELECTION_COLOR, 
                                      selectforeground=TEXT_COLOR,
                                      relief=tk.SOLID, borderwidth=1)
        self.category_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Liste butonları
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(btn_frame, text="Yenile", style="Primary.TButton",
                  command=self._load_categories).pack(pady=5, ipadx=10, ipady=3)
        ttk.Button(btn_frame, text="Sil", style="Danger.TButton",
                  command=self._remove_category).pack(pady=5, ipadx=10, ipady=3)

    def _save_settings(self):
        """Ayarları kaydeder"""
        try:
            new_kdv = float(self.default_kdv.get())
            if not (0 <= new_kdv <= 100):
                raise ValueError("KDV oranı 0-100 arasında olmalıdır.")
            
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
        
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz KDV oranı!\n{str(e)}")

    def _backup_db(self):
        """Veritabanı yedeği alır"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            backup_filename = f"stop_takip_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join(script_dir, backup_filename)
            
            # Veritabanını kopyala
            shutil.copy2(self.db_path, backup_path)
            messagebox.showinfo("Başarılı", f"Veritabanı yedeği alındı:\n{backup_filename}")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Yedek alınamadı:\n{str(e)}")

    def _restore_db(self):
        """Yedekten geri yükler"""
        try:
            backup_file = filedialog.askopenfilename(
                title="Yedek Dosyasını Seçin",
                filetypes=[("Veritabanı Dosyaları", "*.db"), ("Tüm Dosyalar", "*.*")]
            )
            
            if backup_file:
                confirm = messagebox.askyesno(
                    "Onay", 
                    "Yedekten geri yükleme yapılacak. Bu işlem mevcut verilerin üzerine yazacak.\n"
                    "Devam etmek istiyor musunuz?"
                )
                
                if confirm:
                    # Veritabanı bağlantılarını kapat
                    self.conn.close()
                    
                    # Yedek dosyayı kopyala
                    shutil.copy2(backup_file, self.db_path)
                    
                    # Yeni bağlantı aç
                    self.conn = sqlite3.connect(self.db_path)
                    self.c = self.conn.cursor()
                    
                    # Verileri yenile
                    self._load_hareket_raporu()
                    self._load_categories()
                    self._update_dashboard()
                    self._update_malzeme_listesi()
                    messagebox.showinfo("Başarılı", "Veritabanı başarıyla geri yüklendi!")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Geri yükleme başarısız:\n{str(e)}")
            
            # Bağlantıyı yeniden açmaya çalış
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.c = self.conn.cursor()
            except:
                pass

    def _clear_db(self):
        """Veritabanını temizler"""
        confirm = messagebox.askyesno(
            "Onay", 
            "TÜM verileri silmek istediğinize emin misiniz?\nBu işlem geri alınamaz!"
        )
        
        if confirm:
            self.c.execute("DELETE FROM malzeme_girisleri")
            self.c.execute("DELETE FROM malzeme_cikislari")
            self.c.execute("DELETE FROM mevcut_stok")
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Tüm veriler silindi!")
            self._load_hareket_raporu()
            self._load_categories()
            self._update_dashboard()
            self._update_malzeme_listesi()

    def _add_category(self):
        """Yeni kategori ekler"""
        new_cat = self.new_category.get().strip()
        if not new_cat:
            messagebox.showwarning("Uyarı", "Kategori adı boş olamaz!")
            return
        
        # Kategorileri güncelle
        self._load_categories()  # Önce mevcut kategorileri yükle
        
        # Kategoriyi veritabanına eklemek için bir malzeme ekliyoruz (geçici çözüm)
        # Aslında ayrı bir kategori tablosu olmalı
        self.c.execute(
            "INSERT INTO malzeme_girisleri (ad, fiyat, adet, kdv, toplam, tarih, kategori) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("KATEGORI_OLUSTURMA", 0, 0, 0, 0, datetime.now().strftime("%d.%m.%Y"), new_cat)
        )
        self.conn.commit()
        
        messagebox.showinfo("Başarılı", f"'{new_cat}' kategorisi eklendi!")
        self.new_category.delete(0, tk.END)
        self._load_categories()  # Kategorileri yeniden yükle

    def _remove_category(self):
        """Kategori siler"""
        selected = self.category_list.curselection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silinecek bir kategori seçin!")
            return
        
        cat = self.category_list.get(selected[0])
        confirm = messagebox.askyesno("Onay", f"'{cat}' kategorisini silmek istediğinize emin misiniz?\n\nBu kategorideki tüm malzemeler 'Kategorisiz' olarak işaretlenecek.")
        
        if confirm:
            # Kategorideki malzemeleri güncelle
            self.c.execute("UPDATE malzeme_girisleri SET kategori=NULL WHERE kategori=?", (cat,))
            self.conn.commit()
            
            # Kategoriyi silmek için geçici kaydı sil
            self.c.execute("DELETE FROM malzeme_girisleri WHERE ad='KATEGORI_OLUSTURMA' AND kategori=?", (cat,))
            self.conn.commit()
            
            messagebox.showinfo("Başarılı", f"'{cat}' kategorisi silindi!")
            self._load_categories()  # Kategorileri yeniden yükle

    def _load_categories(self):
        """Kategorileri yükler ve combobox'ları günceller"""
        self.c.execute("SELECT DISTINCT kategori FROM malzeme_girisleri WHERE kategori IS NOT NULL AND kategori != ''")
        categories = sorted([cat[0] for cat in self.c.fetchall()])
    
        # Kategori filtreleme combobox'larını güncelle
        if hasattr(self, 'kategori_filtre'):
            self.kategori_filtre['values'] = categories
        if hasattr(self, 'aylik_kategori_filtre'):
            self.aylik_kategori_filtre['values'] = categories
        if hasattr(self, 'stok_kategori_filtre'):
            self.stok_kategori_filtre['values'] = categories
    
        # Malzeme ekleme sekmesindeki kategori combobox'ını güncelle
        if hasattr(self, 'entry_kategori'):
            self.entry_kategori['values'] = categories
    
        # Ayarlar sekmesindeki kategori listesini güncelle
        if hasattr(self, 'category_list'):
            self.category_list.delete(0, tk.END)
            for cat in categories:
                self.category_list.insert(tk.END, cat)

    def _export_excel(self, tree):
        """Treeview verilerini Excel'e aktarır"""
        try:
            items = []
            for item in tree.get_children():
                items.append(tree.item(item)['values'])
            
            if not items:
                messagebox.showwarning("Uyarı", "Aktarılacak veri yok!")
                return
            
            # Sütun başlıklarını al
            columns = [tree.heading(col)['text'] for col in tree['columns']]
            
            # DataFrame oluştur
            df = pd.DataFrame(items, columns=columns)
            
            # Dosya yolu (scriptin olduğu dizin)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filename = f"stok_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(script_dir, filename)
            
            # Excel'e yaz
            df.to_excel(filepath, index=False)
            messagebox.showinfo("Başarılı", f"Excel raporu oluşturuldu:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Excel oluşturulamadı:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Windows'ta daha iyi görünüm için
    if os.name == 'nt':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    
    app = StopTakipPro(root)
    root.mainloop()
