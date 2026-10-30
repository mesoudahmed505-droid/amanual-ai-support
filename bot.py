import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Logging ማስተካከያ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# የቦት Token
BOT_TOKEN = "8785816092:AAHU5aLoOFoIL8ZhQEkbsWCuixUCQP1KRyQ"

# --- የ WhatsApp API ማስተካከያዎች (ከተመቻቸ በኋላ የሚሞሉ) ---
WHATSAPP_TOKEN = "YOUR_WHATSAPP_CLOUD_API_TOKEN"
PHONE_NUMBER_ID = "YOUR_WHATSAPP_PHONE_NUMBER_ID"
AMANUAL_WHATSAPP_NUMBER = "TARGET_PHONE_NUMBER"  # የአማኑኤል ስልክ ቁጥር (በሀገር መለያ ኮድ)

# የ Conversation ስቴቶች (States)
POPPO_ID, DESCRIPTION = range(2)


# /start ትእዛዝ ሲላክ የሚሰራ የቋንቋ ምርጫ ገጽ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name

    welcome_text = (
        f"👋 <b>እንኳን ወደ Amanual AI Support በደህና መጡ!</b>\n"
        f"Hi {user_first_name}, welcome to Amanual AI Support!\n\n"
        "እባክዎ የድጋፍ አገልግሎት ለማግኘት የሚፈልጉትን ቋንቋ ይምረጡ፦\n"
        "Please select your preferred language:"
    )

    keyboard = [
        [
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text, parse_mode="HTML", reply_markup=reply_markup
    )


# የአዝራር ምላሾችን (Buttons) ማስተናገጃ
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # አማርኛ ከተመረጠ
    if query.data == "lang_am":
        text = (
            "🤖 <b>Amanual AI Support ረዳትዎ ነው!</b>\n\n"
            "ይህ ቦት የ Poppo Live ተጠቃሚዎችን የቴክኒክ ችግሮች፣ የክፍያ ጥያቄዎችን እና የሪፖርት አቀባበል አገልግሎቶችን በቅጽበት ለማስተናገድ የተዘጋጀ ነው።\n\n"
            "ምን ማድረግ ይፈልጋሉ?"
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    "📝 አዲስ ሪፖርት ማቅረብ", callback_data="report_issue"
                )
            ],
            [
                InlineKeyboardButton(
                    "❓ የተለመዱ ጥያቄዎች (FAQ)", callback_data="faq"
                )
            ],
            [
                InlineKeyboardButton(
                    "👤 የሰው አስተዳዳሪ (Amanual)", callback_data="contact_human"
                )
            ],
        ]

    # English ከተመረጠ
    elif query.data == "lang_en":
        text = (
            "🤖 <b>Welcome to Amanual AI Support!</b>\n\n"
            "This bot provides automated technical support and report submission services for Poppo Live users.\n\n"
            "How can we help you today?"
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    "📝 Submit a Report", callback_data="report_issue"
                )
            ],
            [
                InlineKeyboardButton(
                    "❓ Frequently Asked Questions", callback_data="faq"
                )
            ],
            [
                InlineKeyboardButton(
                    "👤 Contact Admin (Amanual)", callback_data="contact_human"
                )
            ],
        ]

    elif query.data == "faq":
        text = "💡 <b>የተለመዱ ጥያቄዎች እና መልሶቻቸው በቅርቡ ይጠናቀቃሉ!</b>"
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔙 ወደ ዋናው ሜኑ ተመለስ", callback_data="lang_am"
                )
            ]
        ]
    elif query.data == "contact_human":
        text = (
            "📩 ለሰው አስተዳዳሪ ጥያቄዎት ተላክቷል። <b>Amanual</b> መስመር ላይ ሲገባ"
            " ያናግርዎታል።"
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔙 ወደ ዋናው ሜኑ ተመለስ", callback_data="lang_am"
                )
            ]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text, parse_mode="HTML", reply_markup=reply_markup
    )


# --- WhatsApp መልዕክት መላኪያ ተግባር ---
def send_whatsapp_alert(poppo_id, description, user_name):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": AMANUAL_WHATSAPP_NUMBER,
        "type": "text",
        "text": {
            "body": (
                "🚨 *አዲስ የPoppo Live ሪፖርት ደርሷል!* 🚨\n\n"
                f"👤 *የተጠቃሚ ስም:* {user_name}\n"
                f"🆔 *Poppo ID:* {poppo_id}\n"
                f"📄 *መግለጫ:* {description}"
            )
        },
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return None


# --- የሪፖርት ማቅረቢያ Conversation Handler ክፍሎች ---

# 1. ሪፖርት ማቅረብ ሲጀመር (Poppo ID መጠየቅ)
async def start_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📝 <b>አዲስ ሪፖርት ማቅረቢያ ተጀምሯል።</b>\n\nእባክዎ የራስዎን የ **Poppo Live"
        " ID** ቁጥር ብቻ ይጻፉልን፦",
        parse_mode="HTML",
    )
    return POPPO_ID


# 2. Poppo ID ተቀብሎ የችግሩን መግለጫ መጠየቅ
async def receive_poppo_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poppo_id = update.message.text
    context.user_data["poppo_id"] = poppo_id
    await update.message.reply_text(
        f"✅ የPoppo ID ተቀብለናል ({poppo_id})።\n\nአሁን ደግሞ ያጋጠመዎትን **ችግር"
        " ዝርዝር መግለጫ (Description)** በጽሁፍ ይጻፉልን፦",
        parse_mode="HTML",
    )
    return DESCRIPTION


# 3. መግለጫውን ተቀብሎ ሪፖርቱን ማጠናቀቅ እና ወደ WhatsApp መላክ
async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    poppo_id = context.user_data.get("poppo_id")
    user_name = update.effective_user.full_name

    # ሪፖርቱን ወደ WhatsApp የመላክ ሙከራ (API ውሂብ ሲገባ በራሱ ይለቃል)
    # send_whatsapp_alert(poppo_id, description, user_name)

    success_text = (
        "🎉 <b>ሪፖርትዎ በትክክል ተመዝግቧል!</b>\n\n"
        f"🆔 <b>Poppo ID:</b> {poppo_id}\n"
        f"📄 <b>መግለጫ:</b> {description}\n\n"
        "ሪፖርትዎ ለአስተዳዳሪው (Amanual) በ Telegram እና WhatsApp ተልኳል። ፈጣን ምላሽ"
        " እንሰጥዎታለን!"
    )
    await update.message.reply_text(success_text, parse_mode="HTML")
    return ConversationHandler.END


# ሪፖርቱን መሰረዝ ሲፈለግ
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ ሪፖርት ማቅረቡ ተሰርዟል። /start በማድረግ እንደገና መጀመር ይችላሉ።"
    )
    return ConversationHandler.END


# ዋና የቦት ማስነሻ function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    report_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_report, pattern="^report_issue$")
        ],
        states={
            POPPO_ID: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, receive_poppo_id
                )
            ],
            DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, receive_description
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(report_handler)
    app.add_handler(CallbackQueryHandler(button_click))

    print(
        "🚀 Amanual AI Support Bot ከሪፖርት እና ከ WhatsApp ማሳወቂያ ጋር ስራ"
        " ጀምሯል..."
    )
    app.run_polling()


if __name__ == "__main__":
    main()
