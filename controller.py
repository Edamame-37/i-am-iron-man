"""
Modul SystemController
Mengeksekusi pergerakan scroll dengan mekanika Virtual Joystick dan Speed Smoothing.
"""
import pyautogui
import pygetwindow as gw

class SystemController:
    def __init__(self, sensitivity=0.4, deadzone=30):
        self.sensitivity = sensitivity 
        # Deadzone dilebarkan dari 20 ke 30 agar tangan yang diam / tremor alami tidak tereksekusi
        self.deadzone = deadzone       
        
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # State Tracking
        self.is_engaged = False
        self.anchor_y = None
        self.has_paged_in_current_swipe = False 
        
        # Filter Penghalus Kecepatan (Speed EMA)
        self.smoothed_speed = 0.0
        self.speed_ema_alpha = 0.3 # 0.3 berarti kecepatan berganti secara perlahan (akselerasi mulus)

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
        Mengeksekusi scroll dinamis berdasarkan sistem Virtual Joystick (Auto-Scroll).
        Dilengkapi dengan akselerator kecepatan anti-getar.
        """
        if current_y is None:
            self._reset_state()
            return "IDLE"

        is_presentation = self.is_presentation_active()

        if is_pinched:
            if not self.is_engaged:
                self.is_engaged = True
                self.anchor_y = current_y 
                self.has_paged_in_current_swipe = False
                self.smoothed_speed = 0.0 # Reset kecepatan saat kunci anchor
                return "ENGAGED (ANCHOR LOCKED)"
            else:
                offset_y = current_y - self.anchor_y
                
                if is_presentation:
                    swipe_threshold = 40 
                    if not self.has_paged_in_current_swipe:
                        if offset_y < -swipe_threshold:
                            pyautogui.press('pagedown')
                            self.has_paged_in_current_swipe = True
                            return "SWIPED: NEXT SLIDE"
                        elif offset_y > swipe_threshold:
                            pyautogui.press('pageup')
                            self.has_paged_in_current_swipe = True
                            return "SWIPED: PREV SLIDE"
                else:
                    # JOYSTICK AUTO-SCROLL MODE
                    if abs(offset_y) > self.deadzone:
                        # Dapatkan kecepatan mentah (Raw Speed)
                        raw_speed = (abs(offset_y) - self.deadzone) * self.sensitivity
                        
                        # PENYARINGAN SPEED (ANTI-NOISE):
                        # Rumus EMA ini membuat pergantian kecepatan berjalan bertahap.
                        # Hentakan kecepatan akibat tangan bergetar akan dinetralkan.
                        self.smoothed_speed = (self.speed_ema_alpha * raw_speed) + ((1 - self.speed_ema_alpha) * self.smoothed_speed)
                        
                        final_speed = int(self.smoothed_speed)
                        
                        if final_speed < 1:
                            final_speed = 1
                            
                        if offset_y < 0:
                            pyautogui.scroll(final_speed)
                            return f"AUTO-SCROLL UP ({final_speed})"
                        else:
                            pyautogui.scroll(-final_speed)
                            return f"AUTO-SCROLL DOWN ({final_speed})"
                    else:
                        # Jika kembali masuk ke dalam area Deadzone (Tangan direnggangkan balik ke tengah),
                        # turunkan kecepatan ke 0 secara mulus (Pengereman Otomatis)
                        self.smoothed_speed = (1 - self.speed_ema_alpha) * self.smoothed_speed
                
                return "HOLDING ANCHOR"
        else:
            self._reset_state()
            return "IDLE"

    def _reset_state(self):
        """Mereset ke posisi netral ketika tangan dilepas/menghilang"""
        self.is_engaged = False
        self.anchor_y = None
        self.has_paged_in_current_swipe = False
        self.smoothed_speed = 0.0
