"""
Modul SystemController
Mengeksekusi pergerakan scroll dinamis ke OS, lengkap dengan sistem kalkulasi Delta Y dan Deadzone.
"""
import pyautogui
import pygetwindow as gw

class SystemController:
    def __init__(self, sensitivity=1.2, deadzone=4):
        # Pengaturan untuk gaya scroll dinamis
        self.sensitivity = sensitivity # Pengali kecepatan scroll
        self.deadzone = deadzone       # Batas minimum piksel untuk memicu pergeseran layar
        
        pyautogui.FAILSAFE = False
        
        # State Tracking
        self.is_engaged = False
        self.last_y = None
        self.has_paged_in_current_swipe = False # Untuk menjaga satu swipe = satu halaman presentasi

    def is_presentation_active(self):
        """Mengecek apakah jendela aktif saat ini adalah aplikasi slide presentasi."""
        try:
            window = gw.getActiveWindow()
            if window and window.title:
                title = window.title.lower()
                keywords = ["powerpoint", "slide", "presentasi", "presentation", "canva"]
                return any(kw in title for kw in keywords)
        except Exception:
            pass
        return False

    def process_dynamic_motion(self, is_pinched, current_y):
        """
        Mengeksekusi scroll dinamis berdasarkan sistem Touch-and-Drag layaknya Smartphone.
        """
        # Jika tidak ada tangan
        if current_y is None:
            self.is_engaged = False
            self.last_y = None
            self.has_paged_in_current_swipe = False
            return "IDLE"

        is_presentation = self.is_presentation_active()

        # Mekanika Interaksi Cubit (Pinch = Sentuh Layar)
        if is_pinched:
            if not self.is_engaged:
                # Titik Pertama Kali Sentuh (Touch Down)
                self.is_engaged = True
                self.last_y = current_y
                self.has_paged_in_current_swipe = False
                return "ENGAGED (TOUCH)"
            else:
                # Sedang Menarik Layar (Drag)
                delta_y = current_y - self.last_y
                
                # Memilah Eksekusi: Presentasi (Paging) vs Normal (Continuous)
                if is_presentation:
                    swipe_threshold = 30 # Jarak tarikan tangan minimal untuk ganti slide
                    
                    if not self.has_paged_in_current_swipe:
                        if delta_y < -swipe_threshold:
                            pyautogui.press('pagedown')
                            self.has_paged_in_current_swipe = True
                            return "SWIPED: NEXT SLIDE"
                        elif delta_y > swipe_threshold:
                            pyautogui.press('pageup')
                            self.has_paged_in_current_swipe = True
                            return "SWIPED: PREV SLIDE"
                else:
                    # Normal Scroll (Proporsional dengan seberapa jauh menarik tangan)
                    if abs(delta_y) > self.deadzone:
                        # Di komputer, menarik tangan ke Atas (delta Y negatif) harus men-scroll ke BAWAH
                        # Persis seperti cara kerja layar sentuh handphone.
                        # pyautogui.scroll(nilai negatif) berfungsi untuk men-scroll turun.
                        scroll_amount = int(delta_y * self.sensitivity)
                        pyautogui.scroll(scroll_amount)
                        
                        # Setel patokan (anchor) baru hanya jika berhasil melewati deadzone
                        self.last_y = current_y
                        return f"SCROLLING ({scroll_amount})"
                
                return "HOLDING"
        else:
            # Jari Diangkat (Release)
            self.is_engaged = False
            self.last_y = None
            self.has_paged_in_current_swipe = False
            return "IDLE"
