"""
Modul GestureRecognizer
Menganalisis pergerakan dinamis berdasarkan gestur Jari Telunjuk.
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

        # ID Landmark Ujung dan Pangkal Jari (Telunjuk, Tengah, Manis, Kelingking)
        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]
        wrist = lm_list[0]
        
        # Jempol (index 0) kita jadikan 0 saja karena tidak terlalu krusial di logika ini
        fingers.append(0) 

        for i in range(4):
            tip = lm_list[tip_ids[i]]
            pip = lm_list[pip_ids[i]]
            
            dist_tip = math.hypot(tip[1] - wrist[1], tip[2] - wrist[2])
            dist_pip = math.hypot(pip[1] - wrist[1], pip[2] - wrist[2])
            
            # Jika jarak ujung jari ke pergelangan lebih jauh dari jarak pangkal ke pergelangan, 
            # berarti jari sedang terentang/terbuka.
            if dist_tip > dist_pip:
                fingers.append(1) # Terbuka
            else:
                fingers.append(0) # Tertutup
                
        return fingers

    def get_joystick_state(self, lm_list):
        """
        Mendeteksi apakah pengguna sedang mengacungkan telunjuk (Engage) atau membuka tangan (Release).
        Menggunakan Dual-Threshold berbasis status jari.
        """
        if len(lm_list) == 0:
            self.is_currently_engaged = False
            return False, None
            
        fingers = self.get_fingers_up(lm_list)
        if len(fingers) < 5:
            return self.is_currently_engaged, self.smoothed_y
            
        # Sumbu Y untuk pergerakan diambil murni dari koordinat Ujung Jari Telunjuk
        index_tip = lm_list[8]
        raw_y = index_tip[2]
        
        # Penghalus Koordinat Y (Meredam getaran mikro telunjuk)
        if self.smoothed_y is None:
            self.smoothed_y = raw_y
        else:
            self.smoothed_y = (self.ema_alpha * raw_y) + ((1 - self.ema_alpha) * self.smoothed_y)
            
        # LOGIKA STATE MACHINE BERBASIS JARI
        if not self.is_currently_engaged:
            # Mode "Belum Aktif" -> Mencari Titik Kunci (ENGAGE)
            # Syaratnya KETAT: Telunjuk terbuka, TAPI jari Tengah, Manis, Kelingking HARUS tertutup (menggenggam).
            if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                self.is_currently_engaged = True
        else:
            # Mode "Sedang Aktif" -> Mempertahankan Kuncian / Mencari Titik Lepas (RELEASE)
            # Syarat matinya LONGGAR: Jika Jari Tengah dan Manis mulai dibuka lebar (Tangan Netral).
            # Ini memberikan respons pengereman seketika saat tangan dibuka.
            if fingers[2] == 1 and fingers[3] == 1:
                self.is_currently_engaged = False
                
        return self.is_currently_engaged, self.smoothed_y

    def reset_smoothing(self):
        """Mereset seluruh history ketika tangan tidak ada di layar."""
        self.smoothed_y = None
        self.is_currently_engaged = False
