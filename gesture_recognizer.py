"""
Modul GestureRecognizer
Menganalisis pergerakan kemiringan telapak tangan (Wrist Tilt Throttle).
Dilengkapi dengan Exponential Moving Average (EMA) dan mekanisme State Machine.
"""
import math

class GestureRecognizer:
    def __init__(self, ema_alpha=0.65):
        self.ema_alpha = ema_alpha
        self.smoothed_y = None
        self.is_currently_engaged = False
        
    def get_fingers_up(self, lm_list):
        """Mendeteksi jari mana saja yang sedang terbuka berdasarkan jarak engsel."""
        fingers = []
        if len(lm_list) == 0:
            return fingers

        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]
        wrist = lm_list[0]
        
        fingers.append(0) 

        for i in range(4):
            tip = lm_list[tip_ids[i]]
            pip = lm_list[pip_ids[i]]
            
            dist_tip = math.hypot(tip[1] - wrist[1], tip[2] - wrist[2])
            dist_pip = math.hypot(pip[1] - wrist[1], pip[2] - wrist[2])
            
            if dist_tip > dist_pip:
                fingers.append(1) 
            else:
                fingers.append(0) 
                
        return fingers

    def get_joystick_state(self, lm_list):
        """
        Mendeteksi kemiringan sudut pergelangan tangan (Tilt).
        Mengisolasi pergerakan lengan dan mengukur kemiringan telapak secara mandiri.
        """
        if len(lm_list) == 0:
            self.is_currently_engaged = False
            return False, None
            
        fingers = self.get_fingers_up(lm_list)
        if len(fingers) < 5:
            return self.is_currently_engaged, self.smoothed_y
            
        index_tip = lm_list[8]
        wrist = lm_list[0]
        index_base = lm_list[5]
        
        # Jarak referensi telapak tangan (digunakan sebagai penyeimbang ukuran 3D)
        ref_dist = math.hypot(index_base[1] - wrist[1], index_base[2] - wrist[2])
        if ref_dist == 0:
            ref_dist = 1
            
        # KALKULASI SUDUT KEMIRINGAN (NORMALIZED TILT)
        # Menghitung jarak Y antara telunjuk dan pergelangan, dibagi ukuran tangan.
        # Angka ini KEBAL terhadap pergeseran lengan Anda di kamera!
        raw_tilt = ((index_tip[2] - wrist[2]) / ref_dist) * 100
        
        # Penghalus Sudut (Meredam getaran mikro pergelangan)
        if self.smoothed_y is None:
            self.smoothed_y = raw_tilt
        else:
            self.smoothed_y = (self.ema_alpha * raw_tilt) + ((1 - self.ema_alpha) * self.smoothed_y)
            
        # LOGIKA STATE MACHINE BERBASIS JARI
        if not self.is_currently_engaged:
            if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                self.is_currently_engaged = True
        else:
            if fingers[2] == 1 and fingers[3] == 1:
                self.is_currently_engaged = False
                
        return self.is_currently_engaged, self.smoothed_y

    def reset_smoothing(self):
        """Mereset seluruh history ketika tangan tidak ada di layar."""
        self.smoothed_y = None
        self.is_currently_engaged = False
