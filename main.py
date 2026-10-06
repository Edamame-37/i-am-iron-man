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
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    tracker = HandTracker(detection_con=0.8, track_con=0.8)
    recognizer = GestureRecognizer(ema_alpha=0.65)
    controller = SystemController(sensitivity=0.4, deadzone=20)

    print("==================================================")
    print("IRON MAN COMPUTER VISION CONTROLLER AKTIF!")
    print("==================================================")
    print("Mekanika Virtual Joystick (Auto-Scroll):")
    print("  1. Pinch/Cubit untuk mengunci Titik Nol (Anchor).")
    print("  2. Tarik sedikit ke Atas/Bawah dan TAHAN untuk Auto-Scroll.")
    print("     (Semakin jauh ditarik, semakin cepat layarnya meluncur)")
    print("  3. Buka cubitan untuk mengerem (berhenti).")
    print("==================================================")
    print("Fitur Cerdas:")
    print("  - EMA Smoothing Aktif (Anti-Noise Jitter).")
    print("  - Adaptive Pinch Scale (Kebal Jarak Kamera).")
    print("  - Paging Mode Otomatis di PowerPoint/Slide.")
    print("Tekan 'q' pada jendela video untuk keluar dari program.")
    print("==================================================")

    p_time = 0

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = tracker.find_hands(img)
        lm_list = tracker.get_position(img)

        status_text = "NO HAND"

        if len(lm_list) != 0:
            is_pinched, current_y = recognizer.get_pinch_state(lm_list)
            status_text = controller.process_dynamic_motion(is_pinched, current_y)
            
            # Gambarkan UI Visual Feedback saat "Menyentuh" Layar
            if is_pinched:
                thumb_tip = lm_list[4]
                index_tip = lm_list[8]
                cx = int((thumb_tip[1] + index_tip[1]) / 2)
                cy = int((thumb_tip[2] + index_tip[2]) / 2)
                
                # Visualisasi Titik Jangkar
                anchor = controller.anchor_y
                if anchor is not None:
                    # Gambar titik merah kecil sebagai Anchor Nol (Pusat)
                    cv2.circle(img, (cx, int(anchor)), 5, (0, 0, 255), cv2.FILLED)
                    # Gambar garis pembatas (Jarak Joystick)
                    cv2.line(img, (cx, int(anchor)), (cx, cy), (255, 0, 0), 2)
                
                # Lingkaran hijau menyala menandakan posisi jari saat ini
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED) 
        else:
            recognizer.reset_smoothing()
            status_text = controller.process_dynamic_motion(False, None)

        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.putText(img, f'Status: {status_text}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        cv2.imshow("Iron Man Vision Controller", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Program dihentikan.")

if __name__ == "__main__":
    main()
