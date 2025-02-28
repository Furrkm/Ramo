import telebot
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import random
from zoneinfo import ZoneInfo
from flask import Flask, request
import os  # PORT için

# Telegram bot token'ı
TELEGRAM_BOT_TOKEN = "7325325317:AAEPTiFtKJU_LnZX9CN_JKauQoQmhxkfGLI"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
server = Flask(__name__)  # Flask uygulaması 'server' olarak adlandırıldı

API_URL = "http://api.aladhan.com/v1/timingsByCity"
METHOD = 13  # Diyanet İşleri Başkanlığı'nın hesaplama yöntemi
TIMEZONE = ZoneInfo("Europe/Istanbul")

user_last_city = defaultdict(str)

# Mesajlar, dualar, hadisler vb. listeler aynı kalıyor, burada kısaltıyorum
messages = ["Oruç, sabrın en güzel öğretmenidir. (Bakara, 2:183)", "..."]
dualar = ["Allah’ım! Bizi Ramazan’ın feyzinden mahrum bırakma.", "..."]
hadisler = ["Kim bir oruçluya iftar ettirirse, ona sevap yazılır.", "..."]
ramazan_bilgileri = ["Ramazan, Kur’an-ı Kerim’in indirilmeye başlandığı aydır.", "..."]
ayetler = ["Bakara, 2:183: 'Ey iman edenler! Oruç, sizden öncekilere farz kılındığı gibi size de farz kılındı.'", "..."]
ibadetler = ["Kur’an-ı Kerim okumak, Ramazan’ın en kıymetli ibadetlerinden biridir.", "..."]
zikirler = ["Subhânallahi ve bihamdihi - 100 defa (Allah’ı noksan sıfatlardan tenzih ederim ve O’na hamd ederim.)", "..."]
kıssalar = ["Kıssa: Hz. Ebubekir’in İftar Sofrası - Hz. Ebubekir (r.a.), bir gün oruçlu iken yoksul bir aileye iftar için yemek götürdü...", "..."]

def get_prayer_times(city, country="Turkey"):
    params = {'city': city, 'country': country, 'method': METHOD}
    response = requests.get(API_URL, params=params)
    data = response.json()
    timings = data['data']['timings']
    if city.lower() in ["istanbul", "i̇stanbul"]:
        for key in timings:
            time = datetime.strptime(timings[key], '%H:%M')
            time -= timedelta(minutes=1)
            timings[key] = time.strftime('%H:%M')
    return timings

def countdown(target_time):
    now = datetime.now(TIMEZONE)
    target = datetime.strptime(target_time, '%H:%M').replace(
        year=now.year, month=now.month, day=now.day, tzinfo=TIMEZONE
    )
    if target < now:
        target += timedelta(days=1)
    diff = target - now
    total_seconds = int(diff.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours} saat {minutes} dakika"
    return f"{minutes} dakika {seconds} saniye"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    response_message = (
        "🌙 Merhaba, Fenerbahçe Ruhu Ramazan Botu’na hoş geldiniz! Ramazan boyunca size yardımcı olmak için buradayım.\n\n"
        "Komutlar:\n"
        "• /iftar [şehir] - Bugünün iftar vaktini ve kalan süreyi gösterir.\n"
        "• /sahur [şehir] - Bugünün sahur vaktini ve kalan süreyi gösterir.\n"
        "• /ezan veya /Ezan [şehir] - Günlük namaz vakitlerini listeler.\n"
        "• /gununmesaji - Ramazan’a özel bir mesaj paylaşır.\n"
        "• /dua - Ramazan duası gönderir.\n"
        "• /hadis - Ramazan’la ilgili bir hadis paylaşır.\n"
        "• /ramazanbilgi - Ramazan hakkında bilgi verir.\n"
        "• /ayet - Ramazan temalı bir ayet paylaşır.\n"
        "• /ibadet - Ramazan’da yapılabilecek bir ibadet önerir.\n"
        "• /zikir - Ramazan’da okunabilecek zikir, salavat ve sureleri listeler.\n"
        "• /kıssa - Ramazan temalı bir dini hikaye ve hisse paylaşır.\n"
        "\nŞehir belirttikten sonra son şehri hatırlarım, tekrar yazmanıza gerek kalmaz."
    )
    bot.reply_to(message, response_message, parse_mode='HTML')

@bot.message_handler(commands=['iftar', 'sahur'])
def send_prayer_time(message):
    user_id = message.from_user.id
    command, *args = message.text.split()
    city = args[0] if args else user_last_city[user_id]

    if not city:
        bot.reply_to(message, "Lütfen bir şehir ismi giriniz. 🕌")
        return

    prayer_times = get_prayer_times(city)
    prayer_name = 'İftar' if command == '/iftar' else 'Sahur'
    prayer_key = 'Maghrib' if command == '/iftar' else 'Fajr'
    prayer_time = prayer_times[prayer_key]
    remaining_time = countdown(prayer_time)

    response_message = f"📍 Şehir: <b>{city.upper()}</b>\n"
    response_message += f"🕌 {prayer_name} Vakti: {prayer_time}\n"
    response_message += f"⏰ {prayer_name}a Kalan Süre: {remaining_time}"

    bot.reply_to(message, response_message, parse_mode='HTML')
    user_last_city[user_id] = city

@bot.message_handler(commands=['Ezan', 'ezan'])
def send_all_prayer_times(message):
    user_id = message.from_user.id
    city = message.text.split()[1] if len(message.text.split()) > 1 else user_last_city[user_id]

    if not city:
        bot.reply_to(message, "Lütfen bir şehir ismi giriniz. 🕌")
        return

    prayer_times = get_prayer_times(city)
    current_date = datetime.now().strftime("%d-%m-2025")
    response_message = (
        f"📍 <b>{city.upper()}</b>\n"
        f"📅 {current_date}\n"
        f"🏙 İmsak   : {prayer_times['Imsak']}\n"
        f"🌅 Güneş   : {prayer_times['Sunrise']}\n"
        f"🌇 Öğle    : {prayer_times['Dhuhr']}\n"
        f"🌆 İkindi  : {prayer_times['Asr']}\n"
        f"🌃 Akşam   : {prayer_times['Maghrib']}\n"
        f"🌌 Yatsı   : {prayer_times['Isha']}"
    )

    bot.reply_to(message, response_message, parse_mode='HTML')
    user_last_city[user_id] = city

@bot.message_handler(commands=['gununmesaji'])
def send_daily_message(message):
    msg = random.choice(messages)
    bot.reply_to(message, f"🌙 <b>Günün Mesajı</b> 🌙\n────────────────\n{msg}\n────────────────", parse_mode='HTML')

@bot.message_handler(commands=['dua'])
def send_dua(message):
    dua = random.choice(dualar)
    bot.reply_to(message, f"🤲 <b>Ramazan Duası</b> 🤲\n────────────────\n{dua}\n────────────────", parse_mode='HTML')

@bot.message_handler(commands=['hadis'])
def send_hadis(message):
    hadis = random.choice(hadisler)
    bot.reply_to(message, f"📜 <b>Ramazan Hadisi</b> 📜\n────────────────\n{hadis}\n────────────────", parse_mode='HTML')

@bot.message_handler(commands=['ramazanbilgi'])
def send_ramazan_bilgi(message):
    bilgi = random.choice(ramazan_bilgileri)
    bot.reply_to(message, f"ℹ️ <b>Ramazan Bilgisi</b> ℹ️\n────────────────\n{bilgi}\n────────────────", parse_mode='HTML')

@bot.message_handler(commands=['ayet'])
def send_ayet(message):
    ayet = random.choice(ayetler)
    bot.reply_to(message, f"📖 <b>Ramazan Ayeti</b> 📖\n────────────────\n{ayet}\n────────────────", parse_mode='HTML')

@bot.message_handler(commands=['ibadet'])
def send_ibadet(message):
    ibadet = random.choice(ibadetler)
    bot.reply_to(message, f"🕋 <b>Ramazan İbadeti</b> 🕋\n────────────────\n{ibadet}\n────────────────", parse_mode='HTML')

@bot.message_handler(commands=['zikir'])
def send_zikir(message):
    zikir = random.choice(zikirler)
    bot.reply_to(message, f"🧎‍♂️ <b>Ramazan Zikri</b> 🧎‍♂️\n────────────────\n{zikir}\n────────────────", parse_mode='HTML')

@bot.message_handler(commands=['kıssa'])
def send_kissa(message):
    kissa = random.choice(kıssalar)
    bot.reply_to(message, f"📜 <b>Kıssadan Hisse</b> 📜\n────────────────\n{kissa}\n────────────────", parse_mode='HTML')

# Webhook işleyicisi
@server.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route('/')
def webhook():
    bot.remove_webhook()
    # Render URL'nizi buraya kendi URL'nizle değiştirin
    bot.set_webhook(url=f'https://ramazan-bot.onrender.com/{TELEGRAM_BOT_TOKEN}')
    return "Webhook set!", 200

if __name__ == "__main__":
    # Render'ın PORT ortam değişkenini kullan, yoksa 5000
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
