"""
Modul SystemController
Mengeksekusi pergerakan scroll dengan mekanika Virtual Joystick (Auto-Scroll).
"""
import pyautogui
import pygetwindow as gw

class SystemController:
    def __init__(self, sensitivity=0.4, deadzone=20):
        # Sensitivity jauh lebih kecil karena kini diakumulasi berdasar kecepatan konstan per frame
        self.sensitivity = sensitivity 
        # Deadzone cukup besar agar ada area "netral" di tengah jangkar untuk posisi tangan diam
        self.deadzone = deadzone       
        
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # State Tracking
        self.is_engaged = False
        self.anchor_y = None
        self.has_paged_in_current_swipe = False 

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
        """
        if current_y is None:
            self.is_engaged = False
            self.anchor_y = None
            self.has_paged_in_current_swipe = False
            return "IDLE"

        is_presentation = self.is_presentation_active()

        if is_pinched:
            if not self.is_engaged:
                # Kunci Titik Nol (Anchor) pada frame pertama cubitan
                self.is_engaged = True
                self.anchor_y = current_y 
                self.has_paged_in_current_swipe = False
                return "ENGAGED (ANCHOR LOCKED)"
            else:
                # Menghitung seberapa jauh tangan menyimpang dari Titik Nol
                offset_y = current_y - self.anchor_y
                
                if is_presentation:
                    # Mode Presentasi tetap berupa sentuhan statis (Swipe 1 kali)
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
                    # Jika penyimpangan tangan melewati zona netral (Deadzone)
                    if abs(offset_y) > self.deadzone:
                        # Kecepatan dihitung berdasar jauhnya tangan dari deadzone
                        speed = int((abs(offset_y) - self.deadzone) * self.sensitivity)
                        
                        # Set minimal kecepatan agar tetap meluncur lambat jika digeser sangat sedikit
                        if speed < 1:
                            speed = 1
                            
                        if offset_y < 0:
                            # Tangan berada di ATAS titik jangkar -> Gulung layar ke ATAS
                            # (Kursor/pandangan ditarik ke atas dokumen)
                            pyautogui.scroll(speed)
                            return f"AUTO-SCROLL UP ({speed})"
                        else:
                            # Tangan berada di BAWAH titik jangkar -> Gulung layar ke BAWAH
                            pyautogui.scroll(-speed)
                            return f"AUTO-SCROLL DOWN ({speed})"
                
                return "HOLDING ANCHOR"
        else:
            # Cubitan dilepas (Rem/Stop)
            self.is_engaged = False
            self.anchor_y = None
            self.has_paged_in_current_swipe = False
            return "IDLE"
