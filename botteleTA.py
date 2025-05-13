import requests
import time
from telegram import Bot
from telegram.error import TelegramError

# Config
TELEGRAM_TOKEN = '7633151627:AAFowoEJTa9In8nYpHccAi9fSBP92Vw5lik'
CHAT_ID = '6451128792'

# Inisialisasi bot
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        print("Pesan terkirim!")
    except TelegramError as e:
        print(f"Error mengirim pesan: {e}")

# Contoh fungsi pemantauan kecepatan
def monitor_speed():
    while True:
        # Ambil data kecepatan dari sensor (contoh dummy)
        speed = get_speed_from_sensor()  # Ganti dengan implementasi aktual
        
        # Format pesan
        message = f"🚨 PEMANTAUAN KECEPATAN 🚨\n"
        message += f"Waktu: {time.ctime()}\n"
        message += f"Kecepatan: {speed} km/h\n"
        
        # Kirim ke Telegram
        send_telegram(message)
        
        # Cek kecepatan melebihi batas
        if speed > 40:
            send_telegram("⚠️ Peringatan! Kecepatan melebihi batas maksimum!")
        
        time.sleep(60)  # Update setiap 1 menit

def get_speed_from_sensor():
    # Contoh implementasi dummy
    # Ganti dengan kode pembacaan sensor sebenarnya
    return 75  # Dalam km/h

if __name__ == "__main__":
    send_telegram("🔔 Sistem pemantauan kecepatan aktif!")
    monitor_speed()