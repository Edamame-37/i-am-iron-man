"""
Modul GestureRecognizer
Menganalisis pergerakan dinamis (Dynamic Motion) dan status sentuhan (Pinch).
Dilengkapi dengan Exponential Moving Average (EMA) dan mekanisme Schmitt Trigger (Batas Ganda).
"""
import math

class GestureRecognizer:
    def __init__(self, ema_alpha=0.65):
        self.ema_alpha = ema_alpha
        self.smoothed_y = None
        
        # Schmitt Trigger State
        self.is_currently_pinched = False
        
    def get_pinch_state(self, lm_list):
        """
        Mendeteksi apakah pengguna sedang melakukan Pinch.
        Menggunakan Dual-Threshold agar jari harus benar-benar menyentuh untuk mulai,
        namun rilis seketika (tanpa delay) saat dibuka lebar.
        """
        if len(lm_list) == 0:
            # Jika tangan benar-benar keluar dari jangkauan kamera, matikan semuanya
            self.is_currently_pinched = False
            return False, None
            
        thumb_tip = lm_list[4]
        index_tip = lm_list[8]
        wrist = lm_list[0]
        index_base = lm_list[5]
        
        pinch_dist = math.hypot(index_tip[1] - thumb_tip[1], index_tip[2] - thumb_tip[2])
        ref_dist = math.hypot(index_base[1] - wrist[1], index_base[2] - wrist[2])
        raw_center_y = (thumb_tip[2] + index_tip[2]) / 2
        
        # Penghalus Koordinat Y (Meredam getaran mikro)
        if self.smoothed_y is None:
            self.smoothed_y = raw_center_y
        else:
            self.smoothed_y = (self.ema_alpha * raw_center_y) + ((1 - self.ema_alpha) * self.smoothed_y)
            
        # Kalkulasi rasio jarak pinch terhadap ukuran tangan referensi
        ratio = pinch_dist / ref_dist if ref_dist > 0 else 1.0
        
        # LOGIKA DUAL-THRESHOLD (SCHMITT TRIGGER)
        if not self.is_currently_pinched:
            # State "Belum Mencubit" -> Mencari Titik Kunci (ENGAGE)
            # Syaratnya SANGAT KETAT (< 20%). Jari harus 100% bertemu untuk menyalakan Anchor.
            if ratio < 0.20:
                self.is_currently_pinched = True
        else:
            # State "Sedang Mencubit" -> Mempertahankan Kuncian / Mencari Titik Lepas (RELEASE)
            # Syarat matinya SANGAT LONGGAR (> 80%). Kebal ilusi optik kamera saat tangan diputar.
            if ratio > 0.80:
                self.is_currently_pinched = False
                
        return self.is_currently_pinched, self.smoothed_y

    def reset_smoothing(self):
        """Mereset seluruh history ketika tangan tidak ada di layar."""
        self.smoothed_y = None
        self.is_currently_pinched = False
