"""
Modul GestureRecognizer
Menganalisis pergerakan dinamis (Dynamic Motion) dan status sentuhan (Pinch).
Dilengkapi dengan Exponential Moving Average (EMA) dan Hysteresis Buffer.
"""
import math

class GestureRecognizer:
    def __init__(self, ema_alpha=0.65, drop_tolerance_frames=7):
        self.ema_alpha = ema_alpha
        self.smoothed_y = None
        
        # Hysteresis (Anti-Drop) Buffer
        self.drop_tolerance_frames = drop_tolerance_frames
        self.frames_since_drop = 0
        self.stable_pinch_state = False
        
    def get_pinch_state(self, lm_list):
        """
        Mendeteksi apakah pengguna sedang melakukan Pinch.
        Dilengkapi dengan sistem Pemaaf (Hysteresis) agar cubitan tidak hilang saat frame nge-drop.
        """
        if len(lm_list) == 0:
            # Jika tangan benar-benar keluar dari jangkauan kamera, matikan semuanya
            self.stable_pinch_state = False
            self.frames_since_drop = 0
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
            
        raw_is_pinched = pinch_dist < (0.65 * ref_dist)
        
        # LOGIKA HYSTERESIS (ANTI-DROP & ANTI-FLICKER)
        if raw_is_pinched:
            # MediaPipe melihat cubitan dengan jelas
            self.stable_pinch_state = True
            self.frames_since_drop = 0 # Reset penghitung error
        else:
            # MediaPipe gagal melihat cubitan di frame ini
            if self.stable_pinch_state:
                # Jika sebelumnya sedang mencubit, JANGAN LANGSUNG DIMATIKAN!
                self.frames_since_drop += 1
                
                # Jika hilangnya cubitan sudah terlalu lama (melewati toleransi frame)
                if self.frames_since_drop >= self.drop_tolerance_frames:
                    self.stable_pinch_state = False # Baru benar-benar kita matikan
            else:
                self.stable_pinch_state = False
                
        # Kita kembalikan State yang SUDAH STABIL, bukan tebakan mentah dari frame
        return self.stable_pinch_state, self.smoothed_y

    def reset_smoothing(self):
        """Mereset seluruh history ketika tangan tidak ada di layar."""
        self.smoothed_y = None
        self.stable_pinch_state = False
        self.frames_since_drop = 0
