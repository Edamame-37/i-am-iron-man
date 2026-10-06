"""
Modul SystemController
Bertugas untuk mengeksekusi perintah sistem ke OS, deteksi window presentasi, dan debouncing.
"""
import pyautogui
import pygetwindow as gw

class SystemController:
    def __init__(self, scroll_speed=40):
        self.scroll_speed = scroll_speed
        pyautogui.FAILSAFE = False
        self.previous_gesture = "NEUTRAL"

    def is_presentation_active(self):
        """Mengecek apakah jendela OS aktif saat ini adalah aplikasi presentasi."""
        try:
            window = gw.getActiveWindow()
            if window and window.title:
                title = window.title.lower()
                # Kata kunci untuk mengenali aplikasi presentasi yang butuh "Paging Mode"
                keywords = ["powerpoint", "slide", "presentasi", "presentation", "canva"]
                for kw in keywords:
                    if kw in title:
                        return True
        except Exception:
            pass # Abaikan dengan aman jika akses pembacaan window ditolak sistem
        return False

    def scroll_up(self):
        pyautogui.scroll(self.scroll_speed)

    def scroll_down(self):
        pyautogui.scroll(-self.scroll_speed)

    def page_up(self):
        """Navigasi slide ke atas (Sebelumnya)."""
        pyautogui.press('pageup')

    def page_down(self):
        """Navigasi slide ke bawah (Selanjutnya)."""
        pyautogui.press('pagedown')

    def alt_tab(self):
        """Pindah Jendela / Aplikasi Aktif."""
        pyautogui.hotkey('alt', 'tab')

    def ctrl_tab(self):
        """Pindah Tab dalam Browser / Aplikasi."""
        pyautogui.hotkey('ctrl', 'tab')

    def execute_gesture(self, current_gesture):
        """
        Mengeksekusi aksi berdasarkan gestur yang dibaca.
        Menggunakan sistem Debounce (Anti-Spam) untuk membatasi eksekusi aksi berulang.
        """
        is_presentation = self.is_presentation_active()

        # DEBOUNCE: Jika gestur yang masuk BERBEDA dari frame sebelumnya (Baru dipicu)
        if current_gesture != self.previous_gesture:
            if current_gesture == "ALT_TAB":
                self.alt_tab()
            elif current_gesture == "CTRL_TAB":
                self.ctrl_tab()
            elif current_gesture == "SCROLL_UP":
                if is_presentation:
                    self.page_up()
                else:
                    self.scroll_up()
            elif current_gesture == "SCROLL_DOWN":
                if is_presentation:
                    self.page_down()
                else:
                    self.scroll_down()
        else:
            # Jika gestur yang ditahan SAMA dengan frame sebelumnya (Pengguna sedang menahan pose):
            # Kita HANYA mengizinkan aksi berulang untuk Scroll Kontinu,
            # dengan syarat jendela aktif saat ini BUKAN aplikasi presentasi.
            if current_gesture == "SCROLL_UP" and not is_presentation:
                self.scroll_up()
            elif current_gesture == "SCROLL_DOWN" and not is_presentation:
                self.scroll_down()

        # Simpan state gestur saat ini sebagai patokan di loop berikutnya
        self.previous_gesture = current_gesture
