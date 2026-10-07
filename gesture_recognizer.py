"""
Modul GestureRecognizer
Menganalisis pergerakan kemiringan telapak tangan (Wrist Tilt Throttle).
Dilengkapi dengan 1 Euro Filter (Standar Industri) dan Frame Debouncing.
"""
import math
import time

def smoothing_factor(t_e, cutoff):
    r = 2 * math.pi * cutoff * t_e
    return r / (r + 1)

def exponential_smoothing(a, x, x_prev):
    return a * x + (1 - a) * x_prev

class OneEuroFilter:
    """
    1 Euro Filter (Low-Pass Filter Adaptif)
    Menghilangkan jitter (getaran) saat kursor diam, 
    dan menghilangkan lag (jeda) saat kursor digerakkan cepat.
    """
    def __init__(self, t0, x0, dx0=0.0, min_cutoff=0.05, beta=1.5, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = x0
        self.dx_prev = dx0
        self.t_prev = t0

    def __call__(self, t, x):
        t_e = t - self.t_prev
        if t_e <= 0:
            return x 
            
        a_d = smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = exponential_smoothing(a_d, dx, self.dx_prev)
        
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        
        a = smoothing_factor(t_e, cutoff)
        x_hat = exponential_smoothing(a, x, self.x_prev)
        
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        return x_hat

class GestureRecognizer:
    def __init__(self):
        self.one_euro_filter = None
        
        # State Tracking
        self.is_currently_engaged = False
        
        # Frame Debouncing (Memori Logika)
        self.release_frames_count = 0
        self.REQUIRED_RELEASE_FRAMES = 3 # Membutuhkan 3 frame optik yang konsisten untuk validasi pelepasan
        
    def get_fingers_up(self, lm_list):
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
        if len(lm_list) == 0:
            self.reset_smoothing()
            return False, None
            
        fingers = self.get_fingers_up(lm_list)
        if len(fingers) < 5:
            return self.is_currently_engaged, (self.one_euro_filter.x_prev if self.one_euro_filter else None)
            
        index_tip = lm_list[8]
        wrist = lm_list[0]
        index_base = lm_list[5]
        
        ref_dist = math.hypot(index_base[1] - wrist[1], index_base[2] - wrist[2])
        if ref_dist == 0:
            ref_dist = 1
            
        raw_tilt = ((index_tip[2] - wrist[2]) / ref_dist) * 100
        current_time = time.time()
        
        # =======================================================
        # 1 EURO FILTER: Membunuh Jitter & Lag
        # =======================================================
        if self.one_euro_filter is None:
            # min_cutoff: Kunci kestabilan (Makin kecil makin stabil saat diam)
            # beta: Gesit saat bergerak (Makin besar makin responsif)
            self.one_euro_filter = OneEuroFilter(current_time, raw_tilt, min_cutoff=0.1, beta=1.0)
            smoothed_tilt = raw_tilt
        else:
            smoothed_tilt = self.one_euro_filter(current_time, raw_tilt)
            
        # =======================================================
        # FRAME DEBOUNCING & STATE MACHINE
        # =======================================================
        if not self.is_currently_engaged:
            # Syarat ON: Menunjuk murni. Dinyalakan seketika tanpa delay.
            if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                # Basic Spatial Validation: Ujung telunjuk harus berada lebih tinggi (Y piksel lebih kecil) dari pergelangan.
                # Ini mencegah tuas aktif tak sengaja saat tangan menghadap terbalik ke lantai.
                if index_tip[2] < wrist[2]:
                    self.is_currently_engaged = True
                    self.release_frames_count = 0
        else:
            # Syarat OFF: Tangan membuka
            if fingers[2] == 1 and fingers[3] == 1:
                self.release_frames_count += 1
                # Filter Frame: Mencegah kamera nge-glitch 1 frame 
                if self.release_frames_count >= self.REQUIRED_RELEASE_FRAMES:
                    self.is_currently_engaged = False
                    self.release_frames_count = 0
            else:
                # Reset antrean jika jari tak sengaja mengepal kembali di tengah jalan
                self.release_frames_count = 0
                
        return self.is_currently_engaged, smoothed_tilt

    def reset_smoothing(self):
        self.one_euro_filter = None
        self.is_currently_engaged = False
        self.release_frames_count = 0
