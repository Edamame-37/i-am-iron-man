"""
Modul Main
Titik masuk dari aplikasi Iron Man Controller.
Membuka kamera, membaca frame, dan menggabungkan semua modul.
"""
import cv2
import time
from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from controller import SystemController

def main():
    """
    Fungsi utama program.
    """
    # 1. Inisialisasi Kamera (Indeks 0 biasanya adalah webcam bawaan laptop/komputer)
    cap = cv2.VideoCapture(0)
    
    # Resolusi kamera (opsional, diset ke ukuran yang nyaman agar tidak terlalu berat)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # 2. Inisialisasi Modul-modul kita
    tracker = HandTracker(detection_con=0.8, track_con=0.8) # Confidence tinggi agar akurat
    recognizer = GestureRecognizer()
    controller = SystemController(scroll_speed=40) # Kecepatan scroll

    print("==================================================")
    print("IRON MAN COMPUTER VISION CONTROLLER AKTIF!")
    print("==================================================")
    print("Gestur Baru (Orientasi Tangan Terbuka):")
    print("  - Tunjuk/Geser Ke Atas   : Scroll Atas")
    print("  - Tunjuk/Geser Ke Bawah  : Scroll Bawah")
    print("  - Tunjuk/Geser Ke Kiri   : CTRL + TAB (Pindah Tab)")
    print("  - Tunjuk/Geser Ke Kanan  : ALT + TAB (Pindah Aplikasi)")
    print("  - Tangan Mengepal        : Berhenti (Netral)")
    print("==================================================")
    print("Fitur Cerdas:")
    print("  - Paging Mode akan aktif otomatis di PowerPoint/Slide.")
    print("Tekan 'q' pada jendela video untuk keluar dari program.")
    print("==================================================")

    p_time = 0 # Variabel untuk menghitung FPS (waktu frame sebelumnya)

    while True:
        # Baca frame per frame dari kamera
        success, img = cap.read()
        if not success:
            print("Gagal membaca kamera. Pastikan kamera tidak sedang digunakan aplikasi lain.")
            break

        # Balikkan gambar secara horizontal (seperti cermin) agar lebih intuitif bagi pengguna
        img = cv2.flip(img, 1)

        # Temukan tangan dan gambarkan landmark di atas frame
        img = tracker.find_hands(img)
        
        # Dapatkan list koordinat landmark (jika ada tangan)
        lm_list = tracker.get_position(img)

        current_gesture = "UNKNOWN"

        # Jika tangan terdeteksi (list tidak kosong)
        if len(lm_list) != 0:
            # 1. Analisis orientasi arah jari untuk mendapatkan gestur
            current_gesture = recognizer.recognize(lm_list)
            
            # 2. Kirim gestur tersebut ke kontroler untuk mengeksekusi aksi di OS
            controller.execute_gesture(current_gesture)
        else:
            # Jika tidak ada tangan, reset state debounce ke Netral
            controller.execute_gesture("NEUTRAL")
            current_gesture = "NO HAND"

        # Hitung Frame Per Second (FPS) untuk melihat kecepatan program
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        # Tampilkan teks informasi (FPS & Gestur Aktif) langsung pada layar
        cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.putText(img, f'Gesture: {current_gesture}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Tampilkan jendela aplikasi
        cv2.imshow("Iron Man Vision Controller", img)

        # Jika pengguna menekan tombol 'q' di keyboard saat jendela aktif, keluar dari loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 3. Bersihkan memori saat program ditutup
    cap.release()
    cv2.destroyAllWindows()
    print("Program dihentikan.")

if __name__ == "__main__":
    main()
