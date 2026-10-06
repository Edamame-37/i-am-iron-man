"""
Modul GestureRecognizer
Bertugas untuk menganalisis landmark dari tangan dan menentukan orientasi telapak tangan secara matematis.
"""
import math

class GestureRecognizer:
    def __init__(self):
        # ID ujung jari (Tip) pada MediaPipe:
        # 4: Jempol, 8: Telunjuk, 12: Tengah, 16: Manis, 20: Kelingking
        self.tip_ids = [4, 8, 12, 16, 20]

    def get_fingers_up(self, lm_list):
        """
        Menganalisis koordinat landmark dan mengembalikan list integer (1=buka, 0=tutup)
        untuk kelima jari berurutan: [Jempol, Telunjuk, Tengah, Manis, Kelingking].
        Menghitung berdasarkan jarak Euclidean (tidak bergantung pada rotasi tangan).
        """
        fingers = []
        if len(lm_list) == 0:
            return fingers

        wrist = lm_list[0]
        for id in range(5):
            tip = lm_list[self.tip_ids[id]]
            # Ambil sendi 2 tingkat di bawah ujung jari sebagai pembanding
            pip = lm_list[self.tip_ids[id] - 2]
            
            # Hitung jarak ujung jari ke pergelangan vs sendi tengah ke pergelangan
            dist_tip = math.hypot(tip[1] - wrist[1], tip[2] - wrist[2])
            dist_pip = math.hypot(pip[1] - wrist[1], pip[2] - wrist[2])
            
            # Jika ujung jari lebih jauh dari pergelangan, berarti jari sedang diluruskan (terbuka)
            if dist_tip > dist_pip:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def recognize(self, lm_list):
        """
        Menentukan gestur berdasarkan sudut arah tangan (Jika tangan terbuka).
        Mengembalikan string berisi nama gestur.
        """
        if len(lm_list) == 0:
            return "UNKNOWN"
            
        fingers = self.get_fingers_up(lm_list)
        
        # Syarat utama: Tangan harus terbuka (Minimal 3 atau 4 jari terbuka).
        # Jika mengepal (kurang dari 3 jari terbuka), langsung ke NEUTRAL
        if fingers.count(1) < 3:
            return "NEUTRAL"
            
        # --- MENGHITUNG SUDUT ORIENTASI TANGAN ---
        # Titik 0 adalah Pergelangan, Titik 9 adalah Pangkal Jari Tengah
        x0, y0 = lm_list[0][1], lm_list[0][2]
        x9, y9 = lm_list[9][1], lm_list[9][2]
        
        # Hitung selisih koordinat
        dy = y9 - y0
        dx = x9 - x0
        
        # Hitung sudut dalam derajat
        angle = math.degrees(math.atan2(dy, dx))
        
        # Analisis Arah (Mengingat koordinat Y layar komputer membesar ke Bawah)
        if -135 <= angle < -45:
            return "SCROLL_UP"    # Tangan menunjuk tegak ke atas
        elif 45 <= angle < 135:
            return "SCROLL_DOWN"  # Tangan menunjuk tegak ke bawah
        elif -45 <= angle < 45:
            return "ALT_TAB"      # Tangan menunjuk ke arah Kanan layar
        elif angle >= 135 or angle < -135:
            return "CTRL_TAB"     # Tangan menunjuk ke arah Kiri layar
            
        return "UNKNOWN"
