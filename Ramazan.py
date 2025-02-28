import telebot
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import random
from zoneinfo import ZoneInfo
from flask import Flask, request
import os
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token'ı
TELEGRAM_BOT_TOKEN = "7325325317:AAEPTiFtKJU_LnZX9CN_JKauQoQmhxkfGLI"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
server = Flask(__name__)

API_URL = "http://api.aladhan.com/v1/timingsByCity"
METHOD = 13  # Diyanet İşleri Başkanlığı'nın hesaplama yöntemi
TIMEZONE = ZoneInfo("Europe/Istanbul")

user_last_city = defaultdict(str)

# Motivasyonel mesajlar
messages = [
    "Oruç, sabrın en güzel öğretmenidir. (Bakara, 2:183)",
    "Ramazan, kalbinizi ve ruhunuzu arındırma fırsatıdır.",
    "Allah’ım! Bizi Ramazan’ın feyzinden mahrum bırakma. (İftar Duası)",
    "Bir hurma ile iftar açmak, sünnetin sadeliğini yaşatır.",
    "Ramazan, paylaşmanın ve şükretmenin ayıdır.",
    "Ramazan, Allah’a yakınlaşmanın en güzel zamanıdır.",
    "Oruç, nefsimizi terbiye etmenin yoludur.",
    "Ramazan’da her an ibadetle doludur.",
    "Allah, sabredenlerle beraberdir. (Bakara, 2:153)",
    "Ramazan, rahmet ve mağfiret kapılarının açıldığı aydır."
]

# Ramazan duaları (genişletilmiş)
dualar = [
    "Allah’ım! Bizi Ramazan’ın feyzinden mahrum bırakma.",
    "Allah’ım! Ramazan’ı bizim için bereketli kıl.",
    "Allah’ım! Bize Ramazan’ın sonunu da görmeyi nasip et.",
    "Allah’ım! Ramazan’da günahlarımızı bağışla.",
    "Allah’ım! Bize sabır ve şükür nasip et.",
    "Allah’ım! Ramazan’ın rahmetinden bizi faydalandır.",
    "Allah’ım! Kalplerimizi Ramazan ile nurlandır.",
    "Allah’ım! Orucumuzu kabul eyle.",
    "Allah’ım! Ramazan’da dualarımızı geri çevirme.",
    "Allah’ım! Bizi Ramazan’ın bereketiyle rızıklandır.",
    "Allah’ım! Ramazan’da tövbelerimizi kabul et.",
    "Allah’ım! Bize Ramazan’da huzur ve sağlık ver.",
    "Allah’ım! Ramazan’ın her anını ibadetle geçirmeyi nasip et.",
    "Allah’ım! Ramazan’da bize merhametinle muamele et.",
    "Allah’ım! Ramazan’ı günahlarımızdan arınma vesilesi kıl.",
    "Allah’ım! Bize Ramazan’da bol bol ibadet yapma gücü ver.",
    "Allah’ım! Ramazan’da Kadir Gecesi’ni idrak etmeyi nasip et.",
    "Allah’ım! Ramazan’da ailemizi ve sevdiklerimizi koru.",
    "Allah’ım! Ramazan’da ümmet-i Muhammed’e rahmet ihsan et.",
    "Allah’ım! Ramazan’da açlıkla imtihan olanlara yardım et.",
    "Allah’ım! Ramazan’da bize cennet kapılarını aç.",
    "Allah’ım! Ramazan’da şeytanın şerrinden bizi koru.",
    "Allah’ım! Ramazan’da ibadetlerimizi artır ve kabul buyur.",
    "Allah’ım! Ramazan’da fakir ve muhtaçlara yardım etmeyi nasip et.",
    "Allah’ım! Ramazan’da bize af ve mağfiret ihsan et.",
    "Allah’ım! Ramazan’da Kur’an ile hemhal olmayı nasip et."
]

# Ramazan hadisleri
hadisler = [
    "Kim bir oruçluya iftar ettirirse, ona sevap yazılır.",
    "Sahurda bereket vardır, uyanmaktan geri durma.",
    "Oruç tut, sıhhat bul.",
    "Ramazan’da bir iyilik, yetmiş kat sevap getirir.",
    "Oruç, Allah için terk edilen her şeyin mükafatıdır.",
    "Ramazan ayı girdiğinde cennet kapıları açılır.",
    "Oruçlu için iki sevinç vardır: İftar vakti ve Rabbine kavuşma anı.",
    "Kim Ramazan’da oruç tutarsa, geçmiş günahları bağışlanır.",
    "Ramazan’da dua edenin duası geri çevrilmez.",
    "Oruç, kötülüklerden koruyan bir kalkandır.",
    "Sahura kalkın, çünkü sahurda bereket vardır.",
    "Ramazan’da sadaka vermek sevabı katlar."
]

# Ramazan bilgileri
ramazan_bilgileri = [
    "Ramazan, Kur’an-ı Kerim’in indirilmeye başlandığı aydır.",
    "Oruç, İslam’ın beş temel ibadetinden biridir.",
    "Ramazan, sabır ve şükür ayı olarak bilinir.",
    "Ramazan’da teravih namazı kılınır.",
    "Ramazan, rahmet ve mağfiret ayıdır.",
    "Ramazan Bayramı, orucun tamamlanmasının sevincidir.",
    "Ramazan’da sadaka vermek çok faziletlidir.",
    "Ramazan, nefsimizi terbiye etme zamanıdır.",
    "Ramazan’da Kur’an tilaveti teşvik edilir.",
    "Ramazan, fakirleri hatırlama ve yardım etme ayıdır."
]

# Ramazan’a özel ayetler (birkaç ekleme yapıldı)
ayetler = [
    "Bakara, 2:183: 'Ey iman edenler! Oruç, sizden öncekilere farz kılındığı gibi size de farz kılındı.'",
    "Bakara, 2:185: 'Ramazan ayı, insanlara yol gösterici olan Kur’an’ın indirildiği aydır.'",
    "Âl-i İmrân, 3:133: 'Rabbinizin bağışlamasına ve genişliği göklerle yer kadar olan cennete koşun.'",
    "Bakara, 2:186: 'Kullarım beni sorarsa, şüphesiz ben yakınım; dua edince duasına icabet ederim.'",
    "Tâhâ, 20:114: 'Rabbim! İlmimi artır, diye dua et.'",
    "Mü’minûn, 23:60: 'Rablerine dönecekleri için kalpleri titreyerek iyilik yapanlar...'",
    "Fâtır, 35:29: 'Allah’ın kitabını okuyanlar, namazı kılanlar... Onların sevabı kat kat artar.'",
    "Kadr, 97:1: 'Biz onu (Kur’an’ı) Kadir Gecesi’nde indirdik.'",
    "Bakara, 2:187: 'Oruç gecelerinde eşlerinizle birleşmek size helal kılındı.'",
    "Nahl, 16:97: 'Kim salih amel işlerse, ona güzel bir hayat yaşatırız.'",
    "İsrâ, 17:79: 'Gecenin bir kısmında uyanıp namaz kıl, bu sana fazladan bir ibadet olsun.'",  # Ek
    "Şu’arâ, 26:89: 'Ancak Allah’a temiz bir kalp ile gelenler kurtuluşa erer.'",  # Ek
    "Zümer, 39:53: 'Ey kullarım! Günah işleyerek kendinize zulmedenler, Allah’ın rahmetinden ümit kesmeyin.'"  # Ek
]

# Ramazan’da yapılabilecek ibadetler
ibadetler = [
    "Kur’an-ı Kerim okumak, Ramazan’ın en kıymetli ibadetlerinden biridir.",
    "Teravih namazı kılmak, Ramazan gecelerini bereketlendirir.",
    "Sadaka vermek, Ramazan’da sevabı kat kat artırır.",
    "Fakir ve muhtaçlara yardım etmek, Ramazan’ın ruhuna uygundur.",
    "Zikir çekmek, kalbi Ramazan’da huzurla doldurur.",
    "Bol bol dua etmek, Ramazan’da makbuldür.",
    "Kaza namazı kılmak, Ramazan’da eksik ibadetleri tamamlar.",
    "Tesbih namazı kılmak, Ramazan’da büyük sevap kazandırır.",
    "İftar sofralarına misafir davet etmek, Ramazan bereketini artırır.",
    "Kadir Gecesi’ni ibadetle geçirmek, bin aydan hayırlıdır."
]

# Ramazan’da zikirler, salavatlar ve sureler (okunuşlarıyla)
zikirler = [
    "Subhânallahi ve bihamdihi - 100 defa (Allah’ı noksan sıfatlardan tenzih ederim ve O’na hamd ederim.)",
    "Lâ ilâhe illallah - 100 defa (Allah’tan başka ilah yoktur.)",
    "Allahu Ekber - 100 defa (Allah en büyüktür.)",
    "Estağfirullah - 100 defa (Allah’tan bağışlanma dilerim.)",
    "Hasbunallahu ve ni’mel vekil - 100 defa (Allah bize yeter, O ne güzel vekildir.)",
    "Lâ havle velâ kuvvete illâ billâhil aliyyil azîm - 100 defa (Güç ve kuvvet ancak yüce ve büyük Allah’tandır.)",
    "Salavat: Allâhumme salli alâ seyyidinâ Muhammedin ve alâ âli seyyidinâ Muhammed - 100 defa (Allah’ım! Efendimiz Muhammed’e ve onun ailesine salât ve selam eyle.)",
    "Salavat: Sallallahu aleyhi ve sellem - 100 defa (Allah’ın salât ve selamı onun üzerine olsun.)",
    "Salavat: Allâhumme salli ve sellim ve bârik alâ seyyidinâ Muhammedin ve alâ âlihi ve sahbihi ecmaîn - 100 defa (Allah’ım! Efendimiz Muhammed’e, ailesine ve tüm sahabelerine salât, selam ve bereket ihsan et.)",
    "Subhânallah - 33 defa (Allah’ı noksan sıfatlardan tenzih ederim.)",
    "Elhamdulillah - 33 defa (Hamd Allah’a mahsustur.)",
    "Allahu Ekber - 34 defa (Allah en büyüktür.)",
    "Fatiha Suresi: Elhamdü lillâhi rabbil âlemîn. Errahmânirrahîm. Mâliki yevmiddîn. İyyâke na’büdü ve iyyâke neste’în. İhdinas-sırâtal müstekîm. Sırâtallezîne en’amte aleyhim ğayril mağdûbi aleyhim ve leddâllîn.",
    "İhlas Suresi: Kul hüvallahu ehad. Allahüs-samed. Lem yelid ve lem yûled. Ve lem yekün lehû küfüven ehad.",
    "Felak Suresi: Kul e’ûzü birabbil felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerrin neffâsâti fil ukad. Ve min şerri hâsidin izâ hased.",
    "Nas Suresi: Kul e’ûzü birabbinnâs. Melikinnâs. İlâhinnâs. Min şerril vesvâsil hannâs. Ellezî yüvesvisü fî sudûrinnâs. Minel cinnati vennâs.",
    "Kevser Suresi: İnnâ a’taynâkel kevser. Fesalli lirabbike venhar. İnne şânieke hüvel ebter.",
    "Kafirun Suresi: Kul yâ eyyühel kâfirûn. Lâ a’büdü mâ ta’büdûn. Ve lâ entüm âbidûne mâ a’büd. Ve lâ ene âbidün mâ abedtüm. Ve lâ entüm âbidûne mâ a’büd. Leküm dînüküm ve liye dîn."
]

# Ramazan temalı kıssalar ve hisseler
kıssalar = [
    "Kıssa: Hz. Ebubekir’in İftar Sofrası - Hz. Ebubekir (r.a.), bir gün oruçlu iken yoksul bir aileye iftar için yemek götürdü. Kendi evinde yiyecek kalmamış olmasına rağmen, o ailenin çocuklarının aç kalmasına gönlü razı olmadı. Hisse: Ramazan, paylaşmanın ve fedakârlığın en güzel ayıdır.",
    "Kıssa: Hz. Ali’nin Ekmeği - Hz. Ali (r.a.), bir Ramazan günü elindeki son ekmeği bir yetime verdi. O gece rüyasında Peygamber Efendimiz’i gördü ve ona cennet müjdesi verildi. Hisse: Ramazan’da yapılan küçük bir iyilik, büyük mükâfatlar kazandırır.",
    "Kıssa: Yoksul ve Hurma - Bir yoksul, Ramazan’da iftarını açmak için tek bir hurma buldu. O hurmayı bir dilenciyle paylaştı. Ertesi gün eline bir sepet dolusu hurma geçti. Hisse: Ramazan’da paylaşmak, bereketi artırır.",
    "Kıssa: Hz. Osman’ın Sadakası - Hz. Osman (r.a.), Ramazan’da bir yoksula büyük bir sadaka verdi. Yoksul, bunu alınca dua etti ve Hz. Osman o gece rüyasında cennet bahçelerini gördü. Hisse: Ramazan’da sadaka, hem veren hem alan için rahmettir.",
    "Kıssa: Ashab-ı Suffe’nin Orucu - Ashab-ı Suffe’den biri, Ramazan’da gün boyu aç kaldı. İftar vakti bir parça ekmek buldu ve onu bir arkadaşıyla paylaştı. O gece rüyasında Peygamberimiz ona teşekkür etti. Hisse: Ramazan’da paylaşmak, Allah’ın rızasını kazandırır.",
    "Kıssa: Hz. Fatıma’nın İftar Sofrası - Hz. Fatıma (r.a.), bir Ramazan günü iftar için hazırladığı yemeği kapısına gelen bir yetime verdi. O gece evine bereket yağdı. Hisse: Ramazan’da verilen sadaka, evinize bolluk getirir.",
    "Kıssa: Peygamberimizin Sahuru - Peygamber Efendimiz (s.a.v.), bir Ramazan sabahı sahur için sadece bir hurma ve su ile yetindi. Ashabına da sade bir sahuru tavsiye etti. Hisse: Ramazan’da sadelik, ibadetin özüdür.",
    "Kıssa: Hz. Ömer’in Adaleti - Hz. Ömer (r.a.), Ramazan’da bir yoksulun evine gizlice yemek bıraktı. Kimse bilmesin diye geceyi bekledi. Hisse: Ramazan’da iyilik, gizli yapıldığında daha makbuldur.",
    "Kıssa: Ramazan’da Bir Hurma - Bir sahabe, Ramazan’da iftarını bir hurma ile açtı ve şükretti. O gece rüyasında cennet hurmalarını gördü. Hisse: Ramazan’da şükür, azı çok yapar.",
    "Kıssa: Kadir Gecesi’nin Bereketi - Bir mümin, Ramazan’da Kadir Gecesi’ni ibadetle geçirdi. Sabahında kalbi huzurla doldu ve hayatı bereketlendi. Hisse: Ramazan’da Kadir Gecesi’ni aramak, büyük bir nimettir."
]

def get_prayer_times(city, country="Turkey"):
    try:
        params = {'city': city, 'country': country, 'method': METHOD}
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        timings = data['data']['timings']
        if city.lower() in ["istanbul", "i̇stanbul"]:
            for key in timings:
                time = datetime.strptime(timings[key], '%H:%M')
                time -= timedelta(minutes=1)
                timings[key] = time.strftime('%H:%M')
        return timings
    except Exception as e:
        logger.error(f"Prayer times alınamadı: {e}")
        return {}

def countdown(target_time):
    try:
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
    except Exception as e:
        logger.error(f"Kalan süre hesaplanamadı: {e}")
        return "Hesaplama hatası"

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
    if not prayer_times:
        bot.reply_to(message, "Vakitler alınamadı, lütfen tekrar deneyin.")
        return

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
    if not prayer_times:
        bot.reply_to(message, "Vakitler alınamadı, lütfen tekrar deneyin.")
        return

    current_date = datetime.now(TIMEZONE).strftime("%d-%m-2025")
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
    try:
        msg = random.choice(messages)
        response_message = f"🌙 <b>Günün Mesajı</b> 🌙\n────────────────\n{msg}\n────────────────"
        bot.reply_to(message, response_message, parse_mode='HTML')
        logger.info(f"Günün mesajı gönderildi: {msg}")
    except Exception as e:
        logger.error(f"Günün mesajı gönderilemedi: {e}")
        bot.reply_to(message, "Bir hata oluştu, lütfen tekrar deneyin.")

@bot.message_handler(commands=['dua'])
def send_dua(message):
    try:
        dua = random.choice(dualar)
        response_message = f"🤲 <b>Ramazan Duası</b> 🤲\n────────────────\n{dua}\n────────────────"
        bot.reply_to(message, response_message, parse_mode='HTML')
        logger.info(f"Dua gönderildi: {dua}")
    except Exception as e:
        logger.error(f"Dua gönderilemedi: {e}")
        bot.reply_to(message, "Bir hata oluştu, lütfen tekrar deneyin.")

@bot.message_handler(commands=['hadis'])
def send_hadis(message):
    try:
        hadis = random.choice(hadisler)
        response_message = f"📜 <b>Ramazan Hadisi</b> 📜\n────────────────\n{hadis}\n────────────────"
        bot.reply_to(message, response_message, parse_mode='HTML')
        logger.info(f"Hadis gönderildi: {hadis}")
    except Exception as e:
        logger.error(f"Hadis gönderilemedi: {e}")
        bot.reply_to(message, "Bir hata oluştu, lütfen tekrar deneyin.")

@bot.message_handler(commands=['ramazanbilgi'])
def send_ramazan_bilgi(message):
    try:
        bilgi = random.choice(ramazan_bilgileri)
        response_message = f"ℹ️ <b>Ramazan Bilgisi</b> ℹ️\n────────────────\n{bilgi}\n────────────────"
        bot.reply_to(message, response_message, parse_mode='HTML')
        logger.info(f"Ramazan bilgisi gönderildi: {bilgi}")
    except Exception as e:
        logger.error(f"Ramazan bilgisi gönderilemedi: {e}")
        bot.reply_to(message, "Bir hata oluştu, lütfen tekrar deneyin.")

@bot.message_handler(commands=['ayet'])
def send_ayet(message):
    try:
        ayet = random.choice(ayetler)
        response_message = f"📖 <b>Ramazan Ayeti</b> 📖\n────────────────\n{ayet}\n────────────────"
        bot.reply_to(message, response_message, parse_mode='HTML')
        logger.info(f"Ayet gönderildi: {ayet}")
    except Exception as e:
        logger.error(f"Ayet gönderilemedi: {e}")
        bot.reply_to(message, "Bir hata oluştu, lütfen tekrar deneyin.")

@bot.message_handler(commands=['ibadet'])
def send_ibadet(message):
    try:
        ibadet = random.choice(ibadetler)
        response_message = f"🕋 <b>Ramazan İbadeti</b> 🕋\n────────────────\n{ibadet}\n────────────────"
        bot.reply_to(message, response_message, parse_mode='HTML')
        logger.info(f"İbadet gönderildi: {ibadet}")
    except Exception as e:
        logger.error(f"İbadet gönderilemedi: {e}")
        bot.reply_to(message, "Bir hata oluştu, lütfen tekrar deneyin.")

@bot.message_handler(commands=['zikir'])
def send_zikir(message):
    try:
        zikir = random.choice(zikirler)
        response_message = f"🧎‍♂️ <b>Ramazan Zikri</b> 🧎‍♂️\n────────────────\n{zikir}\n────────────────"
        bot.reply_to(message, response_message, parse_mode='HTML')
        logger.info(f"Zikir gönderildi: {zikir}")
    except Exception as e:
        logger.error(f"Zikir gönderilemedi: {e}")
        bot.reply_to(message, "Bir hata oluştu, lütfen tekrar deneyin.")

@bot.message_handler(commands=['kıssa'])
def send_kissa(message):
    try:
        kissa = random.choice(kıssalar)
        response_message = f"📜 <b>Kıssadan Hisse</b> 📜\n────────────────\n{kissa}\n────────────────"
        bot.reply_to(message, response_message, parse_mode='HTML')
        logger.info(f"Kıssa gönderildi: {kissa}")
    except Exception as e:
        logger.error(f"Kıssa gönderilemedi: {e}")
        bot.reply_to(message, "Bir hata oluştu, lütfen tekrar deneyin.")

@server.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def get_message():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        logger.info("Mesaj işlendi: %s", update)
        return "!", 200
    except Exception as e:
        logger.error(f"Mesaj işlenirken hata: {e}")
        return "Error", 500

@server.route('/')
def webhook():
    try:
        bot.remove_webhook()
        webhook_url = f'https://ramobot.onrender.com/{TELEGRAM_BOT_TOKEN}'  # Kendi Render URL’nizi buraya yazın
        bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook ayarlandı: {webhook_url}")
        return "Webhook set!", 200
    except Exception as e:
        logger.error(f"Webhook ayarlanırken hata: {e}")
        return "Webhook setting failed", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)
