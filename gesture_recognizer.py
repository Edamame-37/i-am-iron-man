"""
Modul GestureRecognizer
Menganalisis pergerakan dinamis (Dynamic Motion) dan status sentuhan (Pinch).
Dilengkapi dengan algoritma Exponential Moving Average (EMA) untuk membersihkan noise.
"""
import math

class GestureRecognizer:
    def __init__(self, ema_alpha=0.3):
        # alpha untuk EMA (0.0 sampai 1.0). 
        # Semakin kecil, semakin mulus tapi semakin lambat (delay) merespons.
        self.ema_alpha = ema_alpha
        self.smoothed_y = None
        
    def get_pinch_state(self, lm_list):
        """
        Mendeteksi apakah pengguna sedang melakukan Pinch (Cubitan Jempol & Telunjuk)
        dan mengembalikan koordinat Y yang sudah diperhalus dari cubitan tersebut.
        """
        if len(lm_list) == 0:
            return False, None
            
        # Titik Landmark yang relevan
        thumb_tip = lm_list[4]
        index_tip = lm_list[8]
        wrist = lm_list[0]
        index_base = lm_list[5] # Pangkal telunjuk
        
        # 1. Menghitung jarak cubitan
        pinch_dist = math.hypot(index_tip[1] - thumb_tip[1], index_tip[2] - thumb_tip[2])
        
        # 2. Mencari Jarak Referensi (Pergelangan ke Pangkal Telunjuk)
        # Digunakan agar sistem mengenali skala telapak tangan. 
        # Jadi seberapa pun jauh/dekat tangan ke kamera, sistem cubitan tetap akurat.
        ref_dist = math.hypot(index_base[1] - wrist[1], index_base[2] - wrist[2])
        
        # 3. Menentukan Sumbu Y Tengah Cubitan (Raw)
        raw_center_y = (thumb_tip[2] + index_tip[2]) / 2
        
        # 4. Memproses EMA Filter (Menghilangkan Micro-Jitters)
        if self.smoothed_y is None:
            self.smoothed_y = raw_center_y
        else:
            self.smoothed_y = (self.ema_alpha * raw_center_y) + ((1 - self.ema_alpha) * self.smoothed_y)
            
        # 5. Threshold Cubitan
        # Jika jarak cubitan kurang dari 35% ukuran tangan referensi, maka dianggap mencubit ("Engaged")
        is_pinched = pinch_dist < (0.35 * ref_dist)
        
        return is_pinched, self.smoothed_y

    def reset_smoothing(self):
        """Mereset history filter ketika tangan keluar dari jangkauan kamera."""
        self.smoothed_y = None
