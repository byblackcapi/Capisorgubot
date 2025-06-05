import logging
import json
import asyncio
import os
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from aiohttp import ClientSession, ClientTimeout

# ----------------------
# 1. Gelişmiş Log Ayarları
# ----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CapiSorguBot")

# ----------------------
# 2. Bot Token ve API Listesi
# ----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN", "7655092319:AAEPRJSMWs7DzLHGQ5Tcdh32-3vyphICFps")
APIS = {
    "adsoyad":      "https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={}&soyad={}",
    "adsoyadil":    "https://api.hexnox.pro/sowixapi/adsoyadilce.php?ad={}&soyad={}&il={}",
    "tcpro":        "https://api.hexnox.pro/sowixapi/tcpro.php?tc={}",
    "tcgsm":        "https://api.hexnox.pro/sowixapi/tcgsm.php?tc={}",
    "tapu":         "https://api.hexnox.pro/sowixapi/tapu.php?tc={}",
    "sulale":       "https://api.hexnox.pro/sowixapi/sulale.php?tc={}",
    "okulno":       "https://api.hexnox.pro/sowixapi/okulno.php?tc={}",
    "isyeriyetkili":"https://api.hexnox.pro/sowixapi/isyeriyetkili.php?tc={}",
    "isyeri":       "https://api.hexnox.pro/sowixapi/isyeri.php?tc={}",
    "hane":         "https://api.hexnox.pro/sowixapi/hane.php?tc={}",
    "gsmdetay":     "https://api.hexnox.pro/sowixapi/gsmdetay.php?gsm={}",
    "gsm":          "https://api.hexnox.pro/sowixapi/gsm.php?gsm={}",
    "baba":         "https://api.hexnox.pro/sowixapi/baba.php?tc={}",
    "anne":         "https://api.hexnox.pro/sowixapi/anne.php?tc={}",
    "aile":         "https://api.hexnox.pro/sowixapi/aile.php?tc={}",
    "tc":           "https://api.hexnox.pro/sowixapi/tc.php?tc={}",
    "adres":        "https://api.hexnox.pro/sowixapi/adres.php?tc={}",
    "ip":           "http://192.168.0.18:2000/api/ip/{}",
    "tg":           "http://192.168.0.18:5000/api/{}"
}

# ----------------------
# 3. tmp_images Mutlak Klasör Yolu
# ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_IMAGE_FOLDER = os.path.join(BASE_DIR, "tmp_images")
os.makedirs(TMP_IMAGE_FOLDER, exist_ok=True)

# ----------------------
# 4. JSON Döndüren API Çağrısı (Diğer Servisler İçin)
# ----------------------
async def query_api(url: str) -> dict | list:
    timeout = ClientTimeout(total=10)
    async with ClientSession(timeout=timeout) as session:
        resp = await session.get(url)
        logger.info(f"API çağrısı: {url} | Durum: {resp.status}")
        text = await resp.text(encoding='utf-8')
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}

# ----------------------
# 5. Dosya İçin Düz Metin Oluşturma
# ----------------------
def build_plain_text(data) -> str:
    if isinstance(data, dict):
        if 'data' in data:
            content = data['data']
            if isinstance(content, dict):
                return '\n'.join(f"{k}: {v}" for k, v in content.items())
            if isinstance(content, list):
                parts = []
                for i, item in enumerate(content, 1):
                    if isinstance(item, dict):
                        header = f"-- Sonuç {i} --"
                        lines = '\n'.join(f"{k}: {v}" for k, v in item.items())
                        parts.append(header + '\n' + lines)
                    else:
                        parts.append(str(item))
                return '\n\n'.join(parts)
        return json.dumps(data, ensure_ascii=False, indent=2)

    elif isinstance(data, list):
        parts = []
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                header = f"-- Sonuç {i} --"
                lines = '\n'.join(f"{k}: {v}" for k, v in item.items())
                parts.append(header + '\n' + lines)
            else:
                parts.append(str(item))
        return '\n\n'.join(parts)

    return str(data)

# ----------------------
# 6. API Komut Handler (await ifadeleri ancak bu fonksiyon içinde çalışır)
# ----------------------
async def api_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    parts = msg.text.split()
    name = parts[0].lstrip('/')
    args = parts[1:]

    if name not in APIS:
        await msg.reply_text("❌ Geçersiz komut! /help ile listeye bak.")
        return

    # ───── /tg KOMUT KISMI ───────────────────────────────────────────────────────
    if name == "tg":
        # 6.1) Argüman kontrolü
        if len(args) < 1:
            await msg.reply_text("❗ Kullanım: /tg <kullanıcı_id>\nÖrnek: /tg 7341654915")
            return

        user_id = args[0]
        waiting = await msg.reply_text("⏳ Telegram API’dan veri alınıyor... Lütfen bekleyin.")
        try:
            # 6.2) HTML çıktıyı çekme
            url = APIS["tg"].format(user_id)
            timeout = ClientTimeout(total=10)
            async with ClientSession(timeout=timeout) as session:
                resp = await session.get(url)
                if resp.status != 200:
                    raise RuntimeError(f"API döndürdü: HTTP {resp.status}")
                html_text = await resp.text(encoding='utf-8')

            # 6.3) HTML metnini uzunluğa göre gönderme
            if len(html_text) <= 4000:
                await msg.reply_text(html_text, parse_mode="HTML", disable_web_page_preview=True)
            else:
                file_name = f"tg_{user_id}.html"
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(html_text)

                with open(file_name, "rb") as f:
                    input_file = InputFile(f, filename=file_name)
                    await msg.reply_document(
                        document=input_file,
                        caption="📄 TG HTML çıktısı",
                        parse_mode="HTML"
                    )
                os.remove(file_name)

            # 6.4) Fotoğrafın inmesi için kısa bekleme
            await asyncio.sleep(2)

            # 6.5) tmp_images klasörünün mutlak yolu
            image_path = os.path.join(TMP_IMAGE_FOLDER, f"{user_id}.png")

            # 6.6) Fotoğraf varsa gönder, yoksa uyarı ver
            if os.path.isfile(image_path):
                with open(image_path, "rb") as photo:
                    await msg.reply_photo(photo=photo, caption="📸 Profil Fotoğrafı")
            else:
                await msg.reply_text("⚠️ Profil fotoğrafı bulunamadı veya henüz indirilemedi.")

            # 6.7) Bekleme mesajını sil (fotoğraf gönderildikten sonra)
            await waiting.delete()

        except Exception as e:
            logger.exception("tg API isteği başarısız")
            try:
                await waiting.edit_text(f"🚨 Hata: {e}")
            except:
                await msg.reply_text(f"🚨 Hata: {e}")
        return
    # ─────────────────────────────────────────────────────────────────────────────

    # ───── DİĞER KOMUTLAR (eski .txt akışı) ────────────────────────────────────
    waiting_msg = await msg.reply_text("⏳ Sorgu yapılıyor... Lütfen bekleyin.")
    try:
        api_response = await query_api(APIS[name].format(*args))
    except Exception as e:
        logger.exception("API isteği başarısız")
        await waiting_msg.edit_text(f"🚨 Hata: {e}")
        return

    # Düz metin hâline çevir, dosyaya yaz, gönder, sonra sil
    plain = build_plain_text(api_response)
    filename = f"{name}_sonuc.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(plain)

    await waiting_msg.delete()

    with open(filename, 'rb') as f:
        input_file = InputFile(f, filename=filename)
        await msg.reply_document(document=input_file, caption=f"📄 {name} sonucu", parse_mode="HTML")
    os.remove(filename)

# ----------------------
# 7. /start Komutu
# ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>👋 Merhaba!</b>\n"
        "Ben <i>Capi Sorgu Bot</i>.\n\n"
        "<b>🔎 Neler Yapabilirim?</b>\n"
        "• TC, GSM, Adres, Tapu, Aile vb. sorgular.\n"
        "• Sonuçları temiz .txt dosyası olarak yollarım.\n"
        "• /tg komutunda hem HTML çıktıyı hem de profil fotoğrafını gönderirim.\n\n"
        "<b>⚙️ Öne Çıkan Komutlar:</b>\n"
        "• <code>/help</code> — Yardım menüsü.\n"
        "• <code>/servisler</code> — Tüm servisler.\n"
    )
    buttons = [
        [
            InlineKeyboardButton("📚 Yardım", callback_data='help'),
            InlineKeyboardButton("🚀 Servisler", callback_data='servisler')
        ],
        [
            InlineKeyboardButton("📢 Resmi Kanal", url='https://t.me/capiyedek_support'),
            InlineKeyboardButton("👤 Sahib", url='https://t.me/capiyedek')
        ]
    ]
    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ----------------------
# 8. Callback Butonları
# ----------------------
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "help":
        await help_command(update, context)
    elif query.data == "servisler":
        await servisler(update, context)

# ----------------------
# 9. /help Komutu
# ----------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = [f"• /<b>{cmd}</b>" for cmd in sorted(APIS.keys())]
    examples = [
        "/tc 12345678910",
        "/gsm 05551234567",
        "/adsoyad Ahmet Yılmaz",
        "/adsoyadil Ahmet Yılmaz İstanbul",
        "/tg Havvaxtekin   ← HTML + fotoğraf"
    ]
    text = (
        "📖 <b>Komut Listesi:</b>\n\n" +
        "\n".join(lines) +
        "\n\nℹ️ Parametreleri doğru kullandığınızdan emin olun.\n\n" +
        "💡 <b>Örnekler:</b>\n" +
        "\n".join([f"   • {ex}" for ex in examples])
    )
    await update.effective_message.reply_text(text, parse_mode="HTML")

# ----------------------
# 10. /servisler Komutu
# ----------------------
async def servisler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = [f"• /<b>{cmd}</b>" for cmd in sorted(APIS.keys())]
    text = (
        f"🚀 <b>Toplam {len(APIS)} Aktif Servis:</b>\n\n" +
        "\n".join(lines)
    )
    await update.effective_message.reply_text(text, parse_mode="HTML")

# ----------------------
# 11. Bilinmeyen Komut
# ----------------------
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "❓ <b>Komutu anlayamadım!</b> /help ile deneyin.", parse_mode="HTML"
    )

# ----------------------
# 12. Bot Başlatma
# ----------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("servisler", servisler))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    for cmd in APIS.keys():
        app.add_handler(CommandHandler(cmd, api_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Bot başlatılıyor...")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
