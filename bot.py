import os
import subprocess
from telebot import TeleBot, types
import redis

token = "419817808:AAFEqzmBQzvE8wfhdjxmobRHSvi_0yjDVCU"
bot = TeleBot(token)
admins = [
    163509666
] # Admins
db = redis.Redis("localhost", decode_responses=True)
''


@bot.message_handler(commands=['start', 'help'])
def start(msg):
    text = '''
سلام {} اهلا بكم في بوت فيس اب .. البوت الذي يغير ملامح و شكل صورتك قم ب ارسال صورتك فقط موضحا شكل وجهك للحصول على تعابير واضحة
'''.format(msg.from_user.first_name)
    bot.send_chat_action(msg.chat.id, "typing")
    bot.send_message(msg.chat.id, text)
    db.sadd("faceapp:users", msg.from_user.id)


@bot.message_handler(content_types=['photo'])
def send_photo(msg):
    try:
        file_info = bot.get_file(msg.photo[len(msg.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("pics/pic:{}.jpg".format(str(msg.from_user.id)), 'wb') as fl:
            fl.write(downloaded_file)
        key = types.InlineKeyboardMarkup()
        key.add(types.InlineKeyboardButton("جذاب", callback_data="hot"),
                types.InlineKeyboardButton("مبتسم", callback_data="smile_2"),
                types.InlineKeyboardButton("رجل", callback_data="male"))
        key.add(types.InlineKeyboardButton("انثئ", callback_data="female"),
                types.InlineKeyboardButton("صغير ب العمر", callback_data="young"),
                types.InlineKeyboardButton("كبير ب العمر", callback_data="old"))
        text = 'تم استلام صورتك...\nختر عنصرا واحدا\nتابع @facegram1.'
        bot.send_message(msg.chat.id, text, reply_markup=key)
    except:
        bot.send_message(msg.chat.id, "حدثت مشكلة ... \ n إعادة إرسال الصورة ")

@bot.callback_query_handler(func=lambda call: call.data)
def send_edited_photo(call):
    try:
        tp = call.data
        bot.send_chat_action(call.message.chat.id, "upload_photo")
        subprocess.call(["faceapp", tp, "pics/pic:{}.jpg".format(str(call.from_user.id)), "out.jpg"],
                        stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        fl = open("out.jpg", "rb")
        bot.send_photo(call.message.chat.id, fl)
        fl.close()
    except:
        bot.send_message(call.message.chat.id, "مشکلی پیش آمد...\nعکس را دوباره ارسال کنید")


@bot.message_handler(func=lambda msg: msg.from_user.id in admins)
def admins_handler(msg):
    if msg.text:
        if msg.text == '/stats':
            users = db.scard("faceapp:users")
            bot.send_message(msg.chat.id, "USERS: {}".format(str(users)))
        if msg.text.startswith('/bc '):
            users = db.smembers("faceapp:users")
            text = msg.text.replace("/bc ", "")
            for i in users:
                try:
                    bot.send_message(i, text, parse_mode="HTML")
                except:
                    pass


bot.polling()
