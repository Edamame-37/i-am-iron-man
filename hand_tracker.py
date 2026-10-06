"""
Modul HandTracker
Bertugas untuk mendeteksi tangan dan mendapatkan posisi landmark menggunakan MediaPipe.
"""
import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.7):
        """
        Inisialisasi HandTracker dengan parameter MediaPipe.
        :param mode: False untuk mendeteksi jika tracker kehilangan tangan
        :param max_hands: Jumlah maksimum tangan yang dideteksi
        :param detection_con: Minimum tingkat kepercayaan (confidence) untuk deteksi awal
        :param track_con: Minimum tingkat kepercayaan untuk melacak (tracking) tangan
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        # Inisialisasi MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=float(self.detection_con),
            min_tracking_confidence=float(self.track_con)
        )
        # Utility untuk menggambar titik-titik (landmarks) dan garis di layar
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        """
        Mendeteksi tangan dalam frame gambar.
        Mengembalikan frame asli yang sudah digambar landmark-nya jika draw=True.
        """
        # Konversi gambar dari BGR (format default OpenCV) ke RGB (format yang dibutuhkan MediaPipe)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Proses gambar untuk mencari tangan
        self.results = self.hands.process(img_rgb)

        # Jika ditemukan tangan, dan kita ingin menggambarnya
        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                # Menggambar titik dan garis penghubung tangan ke frame gambar
                self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        
        return img

    def get_position(self, img, hand_no=0):
        """
        Mendapatkan posisi (x, y) dari setiap sendi/landmark tangan yang terdeteksi.
        Mengembalikan list berisi [id_sendi, koordinat_x, koordinat_y].
        """
        lm_list = []
        if self.results.multi_hand_landmarks:
            # Mengambil data dari tangan pertama (indeks ke-0)
            my_hand = self.results.multi_hand_landmarks[hand_no]
            
            # Mendapatkan dimensi dari gambar (Tinggi, Lebar, Channel/Warna)
            h, w, c = img.shape
            
            for id, lm in enumerate(my_hand.landmark):
                # Landmark.x dan .y berupa rasio dari 0 hingga 1.
                # Kita perlu mengalikannya dengan lebar dan tinggi asli layar untuk mendapat posisi pixel sebenarnya.
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
        return lm_list
