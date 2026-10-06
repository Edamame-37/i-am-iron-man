"""
Modul GestureRecognizer
Bertugas untuk menganalisis landmark dari tangan dan menentukan jari mana saja yang terbuka.
"""
class GestureRecognizer:
    def __init__(self):
        """
        Inisialisasi ID untuk ujung jari (tip) sesuai dengan definisi titik MediaPipe.
        4: Jempol, 8: Telunjuk, 12: Tengah, 16: Manis, 20: Kelingking
        """
        self.tip_ids = [4, 8, 12, 16, 20]

    def get_fingers_up(self, lm_list):
        """
        Menganalisis koordinat landmark dan mengembalikan list integer (1=buka, 0=tutup)
        untuk kelima jari berurutan: [Jempol, Telunjuk, Tengah, Manis, Kelingking].
        """
        fingers = []
        if len(lm_list) == 0:
            return fingers

        # 1. Logika untuk Jempol: 
        # Kita menggunakan sumbu X. Jika ujung jempol lebih ke luar dibanding sendi bawahnya.
        # (Asumsi untuk tangan kanan. Jika tangan kiri perlu dibalik, tapi untuk sekarang kita fokus jari lain).
        if lm_list[self.tip_ids[0]][1] > lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 2. Logika untuk 4 Jari lainnya:
        # Kita menggunakan sumbu Y (atas/bawah). Titik (0,0) ada di sudut kiri atas layar.
        # Jadi semakin kecil nilai Y, semakin di "atas" posisinya di layar.
        # Jika nilai Y ujung jari (tip) lebih kecil dari nilai Y sendi 2 langkah di bawahnya (pip), berarti jari lurus/terbuka.
        for id in range(1, 5):
            if lm_list[self.tip_ids[id]][2] < lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1) # Jari terbuka
            else:
                fingers.append(0) # Jari tertutup

        return fingers

    def recognize(self, fingers):
        """
        Menentukan gestur berdasarkan list jari yang terbuka.
        Mengembalikan string berisi nama gestur.
        """
        if len(fingers) == 0:
            return "UNKNOWN"
        
        # Aturan Gestur Scroll Up (V Sign / Peace): 
        # Telunjuk [1] dan Tengah [2] terbuka. Manis [3] dan Kelingking [4] tertutup.
        # Kita hiraukan status jempol (entah 0 atau 1) agar pendeteksian lebih tidak kaku.
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            return "SCROLL_UP"
        
        # Aturan Gestur Scroll Down (Menunjuk):
        # Hanya Telunjuk [1] yang terbuka. Sisanya tertutup.
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return "SCROLL_DOWN"
        
        # Jika kelima jari terbuka semua (Netral / Stop)
        if fingers.count(1) == 5:
            return "NEUTRAL"
            
        # Jika mengepal semua (Netral / Stop)
        if fingers.count(1) == 0 or (fingers.count(1) == 1 and fingers[0] == 1): # Mengepal atau hanya jempol
            return "NEUTRAL"
            
        return "UNKNOWN"
