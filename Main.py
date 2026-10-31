import telebot
import sqlite3
import datetime

# Initialize bot and database
API_TOKEN =9195514516:AAG4OeWANXniHEXj5-ta0PxgqQNMcAFxqOQ
bot = telebot.TeleBot(API_TOKEN)
conn = sqlite3.connect('premium_users.db', check_same_thread=False)
cursor = conn.cursor()

# Create table for users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiry_date TEXT
    )
''')
conn.commit()

# Helper function to check premium status
def is_premium(user_id):
    cursor.execute('SELECT expiry_date FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        expiry_date = datetime.datetime.strptime(result[0], '%Y-%m-%d')
        if expiry_date > datetime.datetime.now():
            return True
        else:
            # Remove expired user
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            conn.commit()
    return False

# Command: /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Premium Bot!")

# Command: /add_premium <user_id> <days>
@bot.message_handler(commands=['add_premium'])
def add_premium(message):
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "Usage: /add_premium <user_id> <days>")
            return
        
        user_id = int(args[1])
        days = int(args[2])
        
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
        expiry_date_str = expiry_date.strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, expiry_date)
            VALUES (?, ?)
        ''', (user_id, expiry_date_str))
        conn.commit()
        
        bot.reply_to(message, f"User {user_id} added to premium until {expiry_date_str}.")
    except Exception as e:
        bot.reply_to(message, "Failed to add premium. Make sure you use the correct format.")

# Command: Protected feature example
@bot.message_handler(commands=['premium_feature'])
def premium_feature(message):
    if is_premium(message.from_user.id):
        bot.reply_to(message, "Here is your premium content!")
    else:
        bot.reply_to(message, "This feature is for premium users only.")

bot.polling()
