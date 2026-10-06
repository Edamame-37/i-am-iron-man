"""
Modul SystemController
Mengeksekusi pergerakan scroll dengan mekanika Virtual Joystick dan Speed Smoothing.
"""
import pyautogui
import pygetwindow as gw

class SystemController:
    def __init__(self, sensitivity=0.4, deadzone=30):
        self.sensitivity = sensitivity 
        self.deadzone = deadzone       
        
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # State Tracking
        self.is_engaged = False
        self.anchor_y = None
        self.has_paged_in_current_swipe = False 
        
        # Filter Penghalus Kecepatan (Speed EMA)
        self.smoothed_speed = 0.0
        self.speed_ema_alpha = 0.3

    def is_presentation_active(self):
        try:
            window = gw.getActiveWindow()
            if window and window.title:
                title = window.title.lower()
                keywords = ["powerpoint", "slide", "presentasi", "presentation", "canva"]
                return any(kw in title for kw in keywords)
        except Exception:
            pass
        return False

    def process_dynamic_motion(self, is_active, current_y):
        if current_y is None:
            self._reset_state()
            return "IDLE"

        is_presentation = self.is_presentation_active()

        if is_active:
            if not self.is_engaged:
                self.is_engaged = True
                self.anchor_y = current_y 
                self.has_paged_in_current_swipe = False
                self.smoothed_speed = 0.0
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
                    if abs(offset_y) > self.deadzone:
                        raw_speed = (abs(offset_y) - self.deadzone) * self.sensitivity
                        self.smoothed_speed = (self.speed_ema_alpha * raw_speed) + ((1 - self.speed_ema_alpha) * self.smoothed_speed)
                        
                        final_speed = int(self.smoothed_speed)
                        if final_speed < 1:
                            final_speed = 1
                            
                        # Logika Arah (Sesuai Permintaan)
                        # offset_y < 0 artinya Telunjuk ditarik ke ATAS (karena Y=0 ada di atas layar).
                        if offset_y < 0:
                            pyautogui.scroll(final_speed) # Scroll layar ke ATAS
                            return f"AUTO-SCROLL UP ({final_speed})"
                        else:
                            pyautogui.scroll(-final_speed) # Scroll layar ke BAWAH
                            return f"AUTO-SCROLL DOWN ({final_speed})"
                    else:
                        self.smoothed_speed = (1 - self.speed_ema_alpha) * self.smoothed_speed
                
                return "HOLDING ANCHOR"
        else:
            self._reset_state()
            return "IDLE"

    def _reset_state(self):
        self.is_engaged = False
        self.anchor_y = None
        self.has_paged_in_current_swipe = False
        self.smoothed_speed = 0.0
