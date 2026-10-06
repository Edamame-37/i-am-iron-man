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

    window_name = "Iron Man Vision Controller"
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    show_window = True

    print("==================================================")
    print("IRON MAN COMPUTER VISION CONTROLLER AKTIF!")
    print("==================================================")
    print("Mekanika Virtual Joystick (Auto-Scroll):")
    print("  1. Acungkan JARI TELUNJUK untuk mengunci Titik Nol (Anchor).")
    print("  2. Tarik Telunjuk ke Atas/Bawah dan TAHAN posisinya.")
    print("     - Telunjuk ke ATAS = Scroll layar ke ATAS")
    print("     - Telunjuk ke BAWAH = Scroll layar ke BAWAH")
    print("  3. Buka seluruh tangan (Rentangkan Jari) untuk berhenti/mengerem.")
    print("==================================================")
    print("Fitur UI & Mode Latar Belakang:")
    print("  - Jendela Kamera Selalu di Atas (Always on Top).")
    print("  - Klik silang 'X' untuk masuk Mode Latar Belakang (Headless).")
    print("  - Tekan 'q' pada jendela ATAU Ctrl+C di terminal untuk keluar.")
    print("==================================================")

    p_time = 0

    try:
        while True:
            success, img = cap.read()
            if not success:
                break

            img = cv2.flip(img, 1)
            img = tracker.find_hands(img)
            lm_list = tracker.get_position(img)

            status_text = "NO HAND"

            if len(lm_list) != 0:
                # Menggunakan deteksi gestur Telunjuk
                is_active, current_y = recognizer.get_joystick_state(lm_list)
                status_text = controller.process_dynamic_motion(is_active, current_y)
                
                if is_active:
                    # Titik koordinat adalah ujung Telunjuk
                    index_tip = lm_list[8]
                    cx = index_tip[1]
                    cy = index_tip[2]
                    
                    anchor = controller.anchor_y
                    if anchor is not None:
                        # Jangkar divisualisasikan dari ujung telunjuk
                        cv2.circle(img, (cx, int(anchor)), 5, (0, 0, 255), cv2.FILLED)
                        cv2.line(img, (cx, int(anchor)), (cx, cy), (255, 0, 0), 2)
                    
                    cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED) 
            else:
                recognizer.reset_smoothing()
                status_text = controller.process_dynamic_motion(False, None)

            c_time = time.time()
            fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
            p_time = c_time

            if show_window:
                try:
                    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                        show_window = False
                        cv2.destroyWindow(window_name)
                        print("\n[INFO] Jendela ditutup. Sistem berjalan mulus di LATAR BELAKANG (Headless Mode).")
                        print("[INFO] Tekan 'Ctrl + C' di terminal ini untuk mematikan program sepenuhnya.")
                except cv2.error:
                    show_window = False
                    
            if show_window:
                cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                cv2.putText(img, f'Status: {status_text}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                
                cv2.imshow(window_name, img)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
            else:
                pass

    except KeyboardInterrupt:
        print("\n[INFO] Dihentikan paksa oleh pengguna melalui Terminal (Ctrl+C).")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Program dimatikan secara aman.")

if __name__ == "__main__":
    main()
