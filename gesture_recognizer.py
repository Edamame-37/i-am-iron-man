"""
Modul GestureRecognizer
Bertugas untuk menganalisis landmark dari tangan dan menentukan kombinasi jari.
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
        Menghitung berdasarkan jarak Euclidean (tahan terhadap rotasi tangan).
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
        Menentukan gestur berdasarkan jari-jari yang terbuka.
        Mengembalikan string berisi nama gestur.
        """
        if len(lm_list) == 0:
            return "UNKNOWN"
            
        fingers = self.get_fingers_up(lm_list)
        
        # Aturan Gestur Scroll Up (Shaka / Call Me): 
        # Jempol [0] dan Kelingking [4] terbuka. Telunjuk, Tengah, Manis tertutup.
        if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
            return "SCROLL_UP"
        
        # Aturan Gestur Scroll Down (Menunjuk):
        # Hanya Telunjuk [1] yang terbuka. Tengah, Manis, Kelingking tertutup.
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return "SCROLL_DOWN"
        
        # Selain itu (misalnya kelima jari terbuka, atau tangan mengepal penuh)
        return "NEUTRAL"
