import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import mysql.connector
import warnings
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import os

# Gereksiz uyarıları gizle
warnings.filterwarnings("ignore", category=DeprecationWarning)

# --- VERİTABANI AYARLARI ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Batu.2003',  # Şifreniz
    'database': 'CinemaDB'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Veritabanı Hatası: {err}") 
        return None

# --- BÖLÜM 1: GİRİŞ EKRANI ---
class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sinema Yönetim Sistemi")
        self.root.geometry("450x350")
        self.center_window(450, 350)
        
        self.main_frame = ttk.Frame(root, padding=30)
        self.main_frame.pack(fill=BOTH, expand=True)

        ttk.Label(self.main_frame, text="SİSTEM GİRİŞİ", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(pady=20)
        
        ttk.Label(self.main_frame, text="Kullanıcı Adı:").pack(fill=X)
        self.entry_user = ttk.Entry(self.main_frame)
        self.entry_user.pack(fill=X, pady=5)
        # self.entry_user.insert(0, "admin") # Otomatik doldurmayı kaldırdım, güvenlik için
        
        ttk.Label(self.main_frame, text="Şifre:").pack(fill=X, pady=(10,0))
        self.entry_pass = ttk.Entry(self.main_frame, show="*")
        self.entry_pass.pack(fill=X, pady=5)
        # self.entry_pass.insert(0, "1234")
        
        ttk.Button(self.main_frame, text="GİRİŞ YAP", command=self.login, bootstyle="success-outline", width=100).pack(pady=30)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users WHERE Username = %s AND Password = %s", (username, password))
                user = cursor.fetchone()
                if user:
                    for widget in self.root.winfo_children(): widget.destroy()
                    # user[3] veritabanındaki Role sütunudur (Admin/User)
                    CinemaMainApp(self.root, user_id=user[0], user_role=user[3])
                else:
                    messagebox.showerror("Hata", "Hatalı Giriş Bilgileri")
            finally:
                conn.close()
        else:
            messagebox.showerror("Hata", "Veritabanına bağlanılamadı!")

# --- BÖLÜM 2: ANA EKRAN (YETKİLENDİRMELİ) ---
class CinemaMainApp:
    def __init__(self, root, user_id, user_role):
        self.root = root
        self.user_id = user_id
        self.user_role = user_role # Rolü kaydet
        
        self.root.title(f"Sinema Paneli | Kullanıcı: {user_role}")
        self.root.geometry("1280x800")
        self.center_window(1280, 800)

        self.notebook = ttk.Notebook(root, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- SEKME 1 & 2: HERKES İÇİN (Admin ve User) ---
        self.tab_search = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_search, text="🎬 Gişe & Bilet")
        self.setup_search_tab()

        self.tab_tickets = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_tickets, text="🎫 Satış Geçmişi")
        self.setup_tickets_tab()

        # --- SEKME 3 & 4: SADECE ADMIN İÇİN ---
        if self.user_role == 'admin':
            self.tab_movies = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(self.tab_movies, text="⚙️ Film & Seans Yönetimi")
            self.setup_movies_tab()

            self.tab_reports = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(self.tab_reports, text="📊 Hasılat Raporları")
            self.setup_reports_tab()
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    # --- SEKME 1: GİŞE ---
    def setup_search_tab(self):
        left_panel = ttk.Frame(self.tab_search)
        left_panel.pack(side=LEFT, fill=BOTH, expand=True)

        right_panel = ttk.Frame(self.tab_search, width=300, padding=10, bootstyle="secondary")
        right_panel.pack(side=RIGHT, fill=Y, padx=(10,0))
        
        ttk.Label(right_panel, text="FİLM AFİŞİ", font=("Helvetica", 12, "bold"), bootstyle="inverse-secondary").pack(pady=10)
        self.lbl_poster = ttk.Label(right_panel, text="[ Seçim Yapınız ]", bootstyle="inverse-secondary")
        self.lbl_poster.pack(pady=20)

        frame_top = ttk.Labelframe(left_panel, text="Hızlı İşlem", padding=15, bootstyle="info")
        frame_top.pack(fill=X, pady=(0, 10))
        
        ttk.Label(frame_top, text="Film Ara:").pack(side=LEFT, padx=(0, 10))
        self.entry_search = ttk.Entry(frame_top, width=30)
        self.entry_search.pack(side=LEFT, padx=5)
        
        ttk.Button(frame_top, text="🔍 Ara", command=self.search_sessions, bootstyle="primary").pack(side=LEFT, padx=5)
        ttk.Button(frame_top, text="💺 Koltuk Seç & Sat", command=self.open_seat_window, bootstyle="warning").pack(side=RIGHT)
        
        columns = ("ID", "FilmAdi", "SalonAdi", "Tarih", "Saat", "Kapasite")
        self.tree = ttk.Treeview(left_panel, columns=columns, show="headings", bootstyle="info", 
                                 displaycolumns=("FilmAdi", "SalonAdi", "Tarih", "Saat", "Kapasite"))
        
        self.tree.heading("FilmAdi", text="Film Adı")
        self.tree.heading("SalonAdi", text="Salon")
        self.tree.heading("Tarih", text="Tarih")
        self.tree.heading("Saat", text="Saat")
        self.tree.heading("Kapasite", text="Doluluk")
        self.tree.column("FilmAdi", width=200)
        self.tree.column("Kapasite", width=80, anchor=CENTER)
        
        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.show_poster_on_select)
        self.search_sessions()

    # --- SEKME 2: GEÇMİŞ ---
    def setup_tickets_tab(self):
        frame_top = ttk.Frame(self.tab_tickets)
        frame_top.pack(fill=X, pady=10)
        ttk.Label(frame_top, text="SATIŞ GEÇMİŞİM", font=("Helvetica", 12, "bold"), bootstyle="secondary").pack(side=LEFT)
        ttk.Button(frame_top, text="🔄 Yenile", command=self.load_my_tickets, bootstyle="success-outline").pack(side=RIGHT, padx=5)
        ttk.Button(frame_top, text="🚫 İptal Et", command=self.cancel_ticket, bootstyle="danger").pack(side=RIGHT, padx=5)

        columns = ("TicketID", "Film", "Salon", "Tarih", "Saat", "Koltuk", "Fiyat")
        self.tree_tickets = ttk.Treeview(self.tab_tickets, columns=columns, show="headings", bootstyle="success",
                                         displaycolumns=("Film", "Salon", "Tarih", "Saat", "Koltuk", "Fiyat"))

        self.tree_tickets.heading("Film", text="Film")
        self.tree_tickets.heading("Salon", text="Salon")
        self.tree_tickets.heading("Tarih", text="Tarih")
        self.tree_tickets.heading("Saat", text="Saat")
        self.tree_tickets.heading("Koltuk", text="Koltuk")
        self.tree_tickets.heading("Fiyat", text="Tutar")
        self.tree_tickets.pack(fill=BOTH, expand=True)

    # --- SEKME 3: FİLM YÖNETİMİ ---
    def setup_movies_tab(self):
        frame_left = ttk.Frame(self.tab_movies, padding=10, width=350)
        frame_left.pack(side=LEFT, fill=Y, padx=(0, 10))
        frame_left.pack_propagate(False)

        frame_add_movie = ttk.Labelframe(frame_left, text=" 1. Yeni Film Ekle ", padding=15, bootstyle="primary")
        frame_add_movie.pack(fill=X, pady=(0, 20))

        ttk.Label(frame_add_movie, text="Film Adı:").pack(anchor=W)
        self.entry_m_title = ttk.Entry(frame_add_movie)
        self.entry_m_title.pack(fill=X, pady=2)
        ttk.Label(frame_add_movie, text="Tür:").pack(anchor=W)
        self.entry_m_genre = ttk.Entry(frame_add_movie)
        self.entry_m_genre.pack(fill=X, pady=2)
        ttk.Label(frame_add_movie, text="Süre (Dk):").pack(anchor=W)
        self.entry_m_duration = ttk.Entry(frame_add_movie)
        self.entry_m_duration.pack(fill=X, pady=2)
        ttk.Label(frame_add_movie, text="Yönetmen:").pack(anchor=W)
        self.entry_m_director = ttk.Entry(frame_add_movie)
        self.entry_m_director.pack(fill=X, pady=2)

        self.selected_poster_path = tk.StringVar()
        ttk.Button(frame_add_movie, text="🖼️ Afiş Seç", command=self.select_poster, bootstyle="info-outline").pack(fill=X, pady=5)
        self.lbl_path = ttk.Label(frame_add_movie, text="", font=("Arial", 8))
        self.lbl_path.pack()
        ttk.Button(frame_add_movie, text="➕ Filmi Kaydet", command=self.add_movie, bootstyle="success").pack(fill=X, pady=10)

        frame_add_session = ttk.Labelframe(frame_left, text=" 2. Filme Seans Ekle ", padding=15, bootstyle="warning")
        frame_add_session.pack(fill=X, pady=(0, 20))
        ttk.Label(frame_add_session, text="Film Seç:").pack(anchor=W)
        self.combo_movies = ttk.Combobox(frame_add_session, state="readonly")
        self.combo_movies.pack(fill=X, pady=2)
        ttk.Label(frame_add_session, text="Salon Seç:").pack(anchor=W)
        self.combo_halls = ttk.Combobox(frame_add_session, state="readonly")
        self.combo_halls.pack(fill=X, pady=2)
        ttk.Label(frame_add_session, text="Tarih (YYYY-MM-DD):").pack(anchor=W)
        self.entry_s_date = ttk.Entry(frame_add_session)
        self.entry_s_date.pack(fill=X, pady=2)
        self.entry_s_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Label(frame_add_session, text="Saat (HH:MM:SS):").pack(anchor=W)
        self.entry_s_time = ttk.Entry(frame_add_session)
        self.entry_s_time.pack(fill=X, pady=2)
        self.entry_s_time.insert(0, "20:00:00")
        ttk.Button(frame_add_session, text="📅 Seansı Oluştur", command=self.add_session, bootstyle="warning").pack(fill=X, pady=10)

        frame_list = ttk.Frame(self.tab_movies)
        frame_list.pack(side=RIGHT, fill=BOTH, expand=True)
        ttk.Label(frame_list, text="FİLM ARŞİVİ", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        columns = ("ID", "Title", "Genre", "Duration", "Director")
        self.tree_movies = ttk.Treeview(frame_list, columns=columns, show="headings", bootstyle="primary",
                                        displaycolumns=("Title", "Genre", "Duration", "Director"))
        self.tree_movies.heading("Title", text="Film Adı")
        self.tree_movies.heading("Genre", text="Tür")
        self.tree_movies.heading("Duration", text="Süre")
        self.tree_movies.heading("Director", text="Yönetmen")
        self.tree_movies.pack(fill=BOTH, expand=True)
        ttk.Button(frame_list, text="🗑️ SEÇİLİ FİLMİ SİL", command=self.delete_movie, bootstyle="danger").pack(pady=10, anchor=E)

        self.load_movies()
        self.load_combobox_data()

    # --- SEKME 4: RAPORLAR ---
    def setup_reports_tab(self):
        frame_cards = ttk.Frame(self.tab_reports, padding=20)
        frame_cards.pack(fill=X)

        card1 = ttk.Labelframe(frame_cards, text="Toplam Hasılat", padding=20, bootstyle="success")
        card1.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        self.lbl_total_revenue = ttk.Label(card1, text="0.00 TL", font=("Arial", 24, "bold"), foreground="#2eb85c")
        self.lbl_total_revenue.pack()

        card2 = ttk.Labelframe(frame_cards, text="Toplam Bilet", padding=20, bootstyle="info")
        card2.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        self.lbl_total_tickets = ttk.Label(card2, text="0 Adet", font=("Arial", 24, "bold"), foreground="#3399ff")
        self.lbl_total_tickets.pack()

        frame_table = ttk.Frame(self.tab_reports, padding=10)
        frame_table.pack(fill=BOTH, expand=True)
        ttk.Label(frame_table, text="FİLM BAZLI HASILAT", font=("Helvetica", 12, "bold")).pack(pady=10)
        ttk.Button(frame_table, text="🔄 Güncelle", command=self.load_reports, bootstyle="dark").pack(pady=5, anchor=E)

        columns = ("Film", "BiletSayisi", "Hasilat")
        self.tree_reports = ttk.Treeview(frame_table, columns=columns, show="headings", bootstyle="dark")
        self.tree_reports.heading("Film", text="Film Adı")
        self.tree_reports.heading("BiletSayisi", text="Satılan Bilet")
        self.tree_reports.heading("Hasilat", text="Kazanç")
        self.tree_reports.column("BiletSayisi", anchor=CENTER)
        self.tree_reports.column("Hasilat", anchor=E)
        self.tree_reports.pack(fill=BOTH, expand=True)
        self.load_reports()

    # --- LOGIC ---
    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        # Eğer tab yoksa (gizliyse) hata vermemesi için try-except
        try:
            tab_text = event.widget.tab(selected_tab, "text")
            if "Satış" in tab_text: self.load_my_tickets()
            elif "Yönetim" in tab_text and self.user_role == 'admin': 
                self.load_movies()
                self.load_combobox_data()
            elif "Rapor" in tab_text and self.user_role == 'admin':
                self.load_reports()
        except:
            pass

    def select_poster(self):
        filename = filedialog.askopenfilename(title="Resim Seç", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if filename:
            self.selected_poster_path.set(filename)
            self.lbl_path.config(text=os.path.basename(filename))

    def show_poster_on_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        session_id = self.tree.item(selected)['values'][0]
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                query = """SELECT M.PosterPath FROM Sessions S JOIN Movies M ON S.MovieID = M.MovieID WHERE S.SessionID = %s"""
                c.execute(query, (session_id,))
                result = c.fetchone()
                if result and result[0] and os.path.exists(result[0]):
                    img = Image.open(result[0])
                    img = img.resize((200, 300), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.lbl_poster.config(image=photo, text="")
                    self.lbl_poster.image = photo
                else:
                    self.lbl_poster.config(image='', text="[ Afiş Yok ]")
            except Exception as e:
                print(e)
            finally: conn.close()

    def add_session(self):
        movie_name = self.combo_movies.get()
        hall_name = self.combo_halls.get()
        s_date = self.entry_s_date.get()
        s_time = self.entry_s_time.get()

        if not movie_name or not hall_name:
            messagebox.showwarning("Eksik", "Lütfen bilgileri doldurun!")
            return

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MovieID, Duration FROM Movies WHERE Title=%s", (movie_name,))
                movie_data = cursor.fetchone()
                if not movie_data:
                    messagebox.showerror("Hata", "Film bulunamadı!")
                    return
                m_id, duration = movie_data[0], movie_data[1]
                
                cursor.execute("SELECT HallID FROM Halls WHERE HallName=%s", (hall_name,))
                h_id = cursor.fetchone()[0]

                new_start = datetime.strptime(f"{s_date} {s_time}", "%Y-%m-%d %H:%M:%S")
                new_end = new_start + timedelta(minutes=duration + 15)

                cursor.execute("""SELECT S.SessionDate, S.SessionTime, M.Duration FROM Sessions S 
                                  JOIN Movies M ON S.MovieID = M.MovieID WHERE S.HallID = %s AND S.SessionDate = %s""", (h_id, s_date))
                existing = cursor.fetchall()
                conflict = False
                for sess in existing:
                    ex_start = datetime.strptime(f"{s_date} {sess[1]}", "%Y-%m-%d %H:%M:%S")
                    ex_end = ex_start + timedelta(minutes=sess[2] + 15)
                    if new_start < ex_end and new_end > ex_start:
                        conflict = True
                        break
                
                if conflict:
                    messagebox.showerror("ÇAKIŞMA!", "Bu saatte salon dolu.")
                    return

                cursor.execute("INSERT INTO Sessions (MovieID, HallID, SessionDate, SessionTime) VALUES (%s, %s, %s, %s)", (m_id, h_id, s_date, s_time))
                conn.commit()
                messagebox.showinfo("Başarılı", "Seans eklendi.")
                self.search_sessions()
            except Exception as e:
                messagebox.showerror("Hata", str(e))
            finally: conn.close()

    def load_combobox_data(self):
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute("SELECT Title FROM Movies"); self.combo_movies['values'] = [r[0] for r in c.fetchall()]
                c.execute("SELECT HallName FROM Halls"); self.combo_halls['values'] = [r[0] for r in c.fetchall()]
            finally: conn.close()

    def search_sessions(self):
        movie_name = self.entry_search.get()
        for row in self.tree.get_children(): self.tree.delete(row)
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.callproc('sp_GetMovieSessions', [movie_name])
                for result in cursor.stored_results():
                    for row in result.fetchall(): self.tree.insert("", "end", values=row)
            finally: conn.close()

    def load_my_tickets(self):
        for row in self.tree_tickets.get_children(): self.tree_tickets.delete(row)
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = """SELECT T.TicketID, M.Title, H.HallName, S.SessionDate, S.SessionTime, T.SeatNumber, T.Price
                           FROM Tickets T JOIN Sessions S ON T.SessionID = S.SessionID
                           JOIN Movies M ON S.MovieID = M.MovieID JOIN Halls H ON S.HallID = H.HallID
                           WHERE T.UserID = %s ORDER BY T.PurchaseDate DESC"""
                cursor.execute(query, (self.user_id,))
                for row in cursor.fetchall(): self.tree_tickets.insert("", "end", values=row)
            finally: conn.close()

    def cancel_ticket(self):
        selected = self.tree_tickets.selection()
        if not selected: return
        data = self.tree_tickets.item(selected)['values']
        if messagebox.askyesno("İptal", "Bilet iptal edilsin mi?"):
            conn = get_db_connection()
            if conn:
                try:
                    c = conn.cursor()
                    c.execute("DELETE FROM Tickets WHERE TicketID=%s", (data[0],))
                    conn.commit()
                    messagebox.showinfo("Başarılı", "İptal edildi.")
                    self.load_my_tickets()
                    self.search_sessions()
                finally: conn.close()

    def load_movies(self):
        for row in self.tree_movies.get_children(): self.tree_movies.delete(row)
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute("SELECT * FROM Movies")
                for r in c.fetchall(): self.tree_movies.insert("", "end", values=r)
            finally: conn.close()

    def add_movie(self):
        title = self.entry_m_title.get()
        duration = self.entry_m_duration.get()
        poster = self.selected_poster_path.get()
        if not title or not duration:
            messagebox.showwarning("Eksik", "Film adı ve süresi şart!")
            return
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                sql = "INSERT INTO Movies (Title, Genre, Duration, Director, PosterPath) VALUES (%s, %s, %s, %s, %s)"
                c.execute(sql, (title, self.entry_m_genre.get(), duration, self.entry_m_director.get(), poster))
                conn.commit()
                messagebox.showinfo("Başarılı", "Film Eklendi")
                self.load_movies()
                self.load_combobox_data()
            finally: conn.close()

    def delete_movie(self):
        selected = self.tree_movies.selection()
        if not selected: return
        movie_id = self.tree_movies.item(selected)['values'][0]
        if messagebox.askyesno("DİKKAT", "Bu filmi ve verilerini silmek istiyor musunuz?"):
            conn = get_db_connection()
            if conn:
                try:
                    c = conn.cursor()
                    c.execute("DELETE FROM Tickets WHERE SessionID IN (SELECT SessionID FROM Sessions WHERE MovieID=%s)", (movie_id,))
                    c.execute("DELETE FROM Sessions WHERE MovieID=%s", (movie_id,))
                    c.execute("DELETE FROM Movies WHERE MovieID=%s", (movie_id,))
                    conn.commit()
                    messagebox.showinfo("Silindi", "Film silindi.")
                    self.load_movies()
                finally: conn.close()

    def open_seat_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seçim Yok", "Listeden bir seans seçin.")
            return

        values = self.tree.item(selected)['values']
        session_id = values[0]
        film_adi = values[1]
        kapasite_text = str(values[5])
        kapasite = int(kapasite_text.split('/')[1].strip()) if '/' in kapasite_text else int(kapasite_text)

        sold_seats = []
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute("SELECT SeatNumber FROM Tickets WHERE SessionID=%s", (session_id,))
                sold_seats = [r[0] for r in c.fetchall()]
            finally: conn.close()

        seat_win = ttk.Toplevel(self.root)
        seat_win.title(f"Koltuk Seçimi: {film_adi}")
        seat_win.geometry("600x600")
        seat_win.grab_set()

        ttk.Label(seat_win, text="[ SAHNE ]", font=("Arial", 14, "bold"), bootstyle="inverse-dark").pack(fill=X, pady=10)
        
        frame_type = ttk.Frame(seat_win, padding=10)
        frame_type.pack()
        ttk.Label(frame_type, text="Bilet Türü: ").pack(side=LEFT)
        self.combo_ticket_type = ttk.Combobox(frame_type, values=["Tam (150 TL)", "Öğrenci (100 TL)"], state="readonly")
        self.combo_ticket_type.current(0)
        self.combo_ticket_type.pack(side=LEFT)

        frame_seats = ttk.Frame(seat_win, padding=20)
        frame_seats.pack()

        cols = 10 
        for i in range(1, kapasite + 1):
            r, c_idx = (i - 1) // cols, (i - 1) % cols
            if i in sold_seats:
                btn = ttk.Button(frame_seats, text=str(i), bootstyle="danger", state="disabled", width=3)
            else:
                btn = ttk.Button(frame_seats, text=str(i), bootstyle="success", width=3,
                                 command=lambda x=i: self.confirm_booking(seat_win, session_id, x))
            btn.grid(row=r, column=c_idx, padx=2, pady=2)

    def confirm_booking(self, win, s_id, seat):
        ticket_type = self.combo_ticket_type.get()
        fiyat = 100.00 if "Öğrenci" in ticket_type else 150.00

        if messagebox.askyesno("Onay", f"{seat} numaralı koltuğu {fiyat} TL'ye sat?"):
            conn = get_db_connection()
            if conn:
                try:
                    c = conn.cursor()
                    c.execute("SELECT COUNT(*) FROM Tickets WHERE SessionID=%s AND SeatNumber=%s", (s_id, seat))
                    if c.fetchone()[0] > 0:
                        messagebox.showerror("Hata", "Koltuk dolu!")
                        win.destroy()
                        return
                    c.execute("INSERT INTO Tickets (SessionID, UserID, SeatNumber, Price) VALUES (%s, %s, %s, %s)", (s_id, self.user_id, seat, fiyat))
                    conn.commit()
                    messagebox.showinfo("Başarılı", "Bilet Satıldı!")
                    win.destroy()
                    self.search_sessions()
                except mysql.connector.Error as e:
                    messagebox.showerror("Hata", str(e))
                finally: conn.close()

    def load_reports(self):
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute("SELECT SUM(Price) FROM Tickets")
                total_rev = c.fetchone()[0]
                self.lbl_total_revenue.config(text=f"{total_rev if total_rev else 0:,.2f} TL")

                c.execute("SELECT COUNT(*) FROM Tickets")
                total_tix = c.fetchone()[0]
                self.lbl_total_tickets.config(text=f"{total_tix} Adet")

                for row in self.tree_reports.get_children(): self.tree_reports.delete(row)
                query = """SELECT M.Title, COUNT(T.TicketID), SUM(T.Price) FROM Tickets T
                           JOIN Sessions S ON T.SessionID = S.SessionID JOIN Movies M ON S.MovieID = M.MovieID
                           GROUP BY M.Title ORDER BY SUM(T.Price) DESC"""
                c.execute(query)
                for r in c.fetchall():
                    rev = r[2] if r[2] else 0
                    self.tree_reports.insert("", "end", values=(r[0], r[1], f"{rev:,.2f} TL"))
            finally: conn.close()

if __name__ == "__main__":
    app_root = ttk.Window(themename="superhero") 
    LoginApp(app_root)
    app_root.mainloop()