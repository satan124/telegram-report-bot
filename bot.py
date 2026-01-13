import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8078343743:AAG8pqSv_CqQBHVoCi6JzZaHgopogeTx0ek"
OWNER_ID = 8286004637  # 👈 apni Telegram user ID yahan daalo

bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

user_state = {}
report_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Create Report", callback_data="create_report"))
    bot.send_message(
        message.chat.id,
        "Click below to create a report.",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda call: call.data == "create_report")
def choose_report(call):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("User Report", callback_data="user_report"),
        InlineKeyboardButton("Imp Report", callback_data="imp_report")
    )
    bot.edit_message_text(
        "Choose report type:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda call: call.data in ["user_report", "imp_report"])
def ask_reported_user(call):
    user_state[call.message.chat.id] = "await_reported"
    report_data[call.message.chat.id] = {
        "type": call.data
    }
    bot.edit_message_text(
        "Enter the reported username or user ID:",
        call.message.chat.id,
        call.message.message_id
    )

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "await_reported")
def get_reported_user(message):
    report_data[message.chat.id]["reported"] = message.text
    user_state[message.chat.id] = "await_proof"

    # notify owner immediately
    bot.send_message(
        OWNER_ID,
        f"🆕 NEW REPORT STARTED\n\n"
        f"Reported: {message.text}\n"
        f"Reporter ID: {message.from_user.id}\n"
        f"Reporter Username: @{message.from_user.username}"
    )

    bot.send_message(
        message.chat.id,
        "📎 Now create a separate Telegram group.\n"
        "Upload all proof screenshots there.\n\n"
        "After that, send the GROUP LINK here."
    )

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "await_proof")
def get_proof_group(message):
    report_data[message.chat.id]["proof_group"] = message.text
    user_state[message.chat.id] = "confirm"

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Submit Report", callback_data="submit_report"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_report")
    )

    bot.send_message(
        message.chat.id,
        "Please confirm your report:",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda call: call.data == "submit_report")
def submit_report(call):
    data = report_data.get(call.message.chat.id)

    final_text = (
        "🚨 REPORT SUBMITTED\n\n"
        f"Type: {data['type']}\n"
        f"Reported User: {data['reported']}\n\n"
        f"Reporter ID: {call.from_user.id}\n"
        f"Reporter Username: @{call.from_user.username}\n\n"
        f"Proof Group Link:\n{data['proof_group']}"
    )

    bot.send_message(OWNER_ID, final_text)

    bot.edit_message_text(
        "✅ Your report has been submitted successfully.",
        call.message.chat.id,
        call.message.message_id
    )

    user_state.pop(call.message.chat.id, None)
    report_data.pop(call.message.chat.id, None)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_report")
def cancel_report(call):
    user_state.pop(call.message.chat.id, None)
    report_data.pop(call.message.chat.id, None)

    bot.edit_message_text(
        "❌ Report cancelled.",
        call.message.chat.id,
        call.message.message_id
    )

bot.infinity_polling()
