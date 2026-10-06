"""
Modul SystemController
Mengeksekusi pergerakan scroll dinamis ke OS, lengkap dengan sistem kalkulasi Delta Y dan Deadzone.
"""
import pyautogui
import pygetwindow as gw

class SystemController:
    def __init__(self, sensitivity=1.5, deadzone=15):
        self.sensitivity = sensitivity 
        # Deadzone diperbesar agar Windows mengumpulkan sedikit pergerakan sebelum men-scroll sekaligus
        self.deadzone = deadzone       
        
        pyautogui.FAILSAFE = False
        
        # MENGHAPUS JEDA BAWAAN! Inilah penyebab utama lag / frame patah-patah!
        pyautogui.PAUSE = 0
        
        # State Tracking
        self.is_engaged = False
        self.last_y = None
        self.has_paged_in_current_swipe = False 
        
        # Penampung pergerakan. Mengumpulkan tarikan jari sebelum dibuang ke OS.
        self.scroll_accumulator = 0.0

    def is_presentation_active(self):
        """Mengecek apakah jendela aktif saat ini adalah aplikasi presentasi."""
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
        if current_y is None:
            self.is_engaged = False
            self.last_y = None
            self.has_paged_in_current_swipe = False
            self.scroll_accumulator = 0.0
            return "IDLE"

        is_presentation = self.is_presentation_active()

        if is_pinched:
            if not self.is_engaged:
                self.is_engaged = True
                self.last_y = current_y
                self.has_paged_in_current_swipe = False
                self.scroll_accumulator = 0.0
                return "ENGAGED (TOUCH)"
            else:
                delta_y = current_y - self.last_y
                self.last_y = current_y # Selalu perbarui titik referensi Y
                
                if is_presentation:
                    swipe_threshold = 40 
                    self.scroll_accumulator += delta_y
                    
                    if not self.has_paged_in_current_swipe:
                        if self.scroll_accumulator < -swipe_threshold:
                            pyautogui.press('pagedown')
                            self.has_paged_in_current_swipe = True
                            return "SWIPED: NEXT SLIDE"
                        elif self.scroll_accumulator > swipe_threshold:
                            pyautogui.press('pageup')
                            self.has_paged_in_current_swipe = True
                            return "SWIPED: PREV SLIDE"
                else:
                    self.scroll_accumulator += delta_y
                    
                    # Jika tarikan tangan terkumpul sudah melewati batas deadzone
                    if abs(self.scroll_accumulator) >= self.deadzone:
                        scroll_amount = int(self.scroll_accumulator * self.sensitivity)
                        
                        # Eksekusi scroll! (pyautogui.PAUSE=0 membuatnya instan)
                        pyautogui.scroll(scroll_amount)
                        
                        # Kosongkan akumulator untuk mulai menghitung tarikan berikutnya
                        self.scroll_accumulator = 0.0
                        return f"SCROLLING ({scroll_amount})"
                
                return "HOLDING"
        else:
            self.is_engaged = False
            self.last_y = None
            self.has_paged_in_current_swipe = False
            self.scroll_accumulator = 0.0
            return "IDLE"
