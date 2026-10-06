"""
Modul GestureRecognizer
Menganalisis pergerakan dinamis (Dynamic Motion) dan status sentuhan (Pinch).
Dilengkapi dengan algoritma Exponential Moving Average (EMA) untuk membersihkan noise.
"""
import math

class GestureRecognizer:
    def __init__(self, ema_alpha=0.65):
        # Alpha dinaikkan ke 0.65 agar lebih responsif mengikuti tarikan tangan!
        self.ema_alpha = ema_alpha
        self.smoothed_y = None
        
    def get_pinch_state(self, lm_list):
        """
        Mendeteksi apakah pengguna sedang melakukan Pinch (Cubitan Jempol & Telunjuk)
        dan mengembalikan koordinat Y yang sudah diperhalus dari cubitan tersebut.
        """
        if len(lm_list) == 0:
            return False, None
            
        thumb_tip = lm_list[4]
        index_tip = lm_list[8]
        wrist = lm_list[0]
        index_base = lm_list[5]
        
        pinch_dist = math.hypot(index_tip[1] - thumb_tip[1], index_tip[2] - thumb_tip[2])
        ref_dist = math.hypot(index_base[1] - wrist[1], index_base[2] - wrist[2])
        raw_center_y = (thumb_tip[2] + index_tip[2]) / 2
        
        if self.smoothed_y is None:
            self.smoothed_y = raw_center_y
        else:
            self.smoothed_y = (self.ema_alpha * raw_center_y) + ((1 - self.ema_alpha) * self.smoothed_y)
            
        # Toleransi dinaikkan drastis dari 0.35 ke 0.65 agar cubitan mudah "nyangkut" dan tak gampang putus
        is_pinched = pinch_dist < (0.65 * ref_dist)
        
        return is_pinched, self.smoothed_y

    def reset_smoothing(self):
        """Mereset history filter ketika tangan keluar dari jangkauan kamera."""
        self.smoothed_y = None
