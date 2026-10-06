"""
Modul SystemController
Bertugas untuk mengeksekusi perintah sistem ke OS (dalam hal ini scroll) menggunakan PyAutoGUI.
"""
import pyautogui

class SystemController:
    def __init__(self, scroll_speed=40):
        """
        Inisialisasi Controller dengan mengatur kecepatan scroll.
        :param scroll_speed: Seberapa besar pixel/garis untuk di-scroll setiap iterasi.
        """
        self.scroll_speed = scroll_speed
        
        # Matikan FAILSAFE sementara. (FAILSAFE standar pyautogui akan memberhentikan program jika mouse di pojok layar)
        pyautogui.FAILSAFE = False

    def scroll_up(self):
        """
        Melakukan aksi scroll mouse ke atas.
        Catatan: PyAutoGUI scroll pada Windows, nilai positif berarti scroll ke atas.
        """
        pyautogui.scroll(self.scroll_speed)

    def scroll_down(self):
        """
        Melakukan aksi scroll mouse ke bawah.
        Nilai negatif berarti scroll ke bawah.
        """
        pyautogui.scroll(-self.scroll_speed)

    def execute_gesture(self, gesture):
        """
        Menerima string hasil pembacaan gestur dan meneruskannya ke aksi nyata.
        """
        if gesture == "SCROLL_UP":
            self.scroll_up()
        elif gesture == "SCROLL_DOWN":
            self.scroll_down()
        elif gesture == "NEUTRAL" or gesture == "UNKNOWN":
            pass # Tidak melakukan apa-apa, aman.
