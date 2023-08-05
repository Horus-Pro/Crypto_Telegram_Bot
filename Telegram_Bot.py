from datetime import datetime, timedelta
from telegram.ext import *
from pycoingecko import CoinGeckoAPI
from telegram import *
import time
import json
import mysql.connector
import requests
import logging
import logging.handlers as handlers
import os, signal
import configparser

#logging.basicConfig(level=logging.DEBUG, filename='logs.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

## Here we define our formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

debuglogHandler = handlers.TimedRotatingFileHandler('Logs/debug.log', when='midnight', interval=1, backupCount=0, encoding='utf8')
debuglogHandler.setLevel(logging.DEBUG)
debuglogHandler.setFormatter(formatter)

logHandler = handlers.TimedRotatingFileHandler('Logs/info.log', when='midnight', interval=1, backupCount=0, encoding='utf8')
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)

errorLogHandler = handlers.RotatingFileHandler('Logs/error.log', maxBytes=5000, backupCount=0,  encoding='utf8')
errorLogHandler.setLevel(logging.ERROR)
errorLogHandler.setFormatter(formatter)

logger.addHandler(debuglogHandler)
logger.addHandler(logHandler)
logger.addHandler(errorLogHandler)

bot_key = 'Telegram bot key here'
bot_name = 'Bot Name'
bot_link = 'Bot Telegram Link'
telegram_user = "Put your telegram user code here"

def dateandtime():
    date_time = datetime.now()
    updated_time = date_time.strftime("%d/%m/%Y - %I:%M %p")
    return str(updated_time)

def connection():
    test_con = f"https://api.telegram.org/bot{bot_key}/getMe"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }
    test = requests.get(test_con, headers=headers)
    logging.info(f"Testing Connection {test}")
    print(f"{dateandtime()} - Testing Connection {test}")

def send_update(chat_id, msg):
    url = f"https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat_id}&text={msg}"
    requests.get(url)

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', ' K', ' M', ' B', ' T', ' Q'][magnitude])

def sample_responses(input_text):
    connection()
    user_message = str(input_text).lower()

    if user_message in ("hello","hi" , "sup"):
        return "Hey! How's it going?"

    if user_message in ("who are you", "who are you?"):
        return "I am CryptoVerse Bot"

    if user_message in ("time", "time?"):
        return dateandtime()

    #print("I don't understand you")
    return "I don't understand you"

def users(UserID, username, first_name, last_name, language_code):
    mydb = mysql.connector.connect(
        host="Host Name",
        user="Username",
        password="Password",
        database="CryptoVerse_db"
    )
    mycursor = mydb.cursor()
    sql = "SELECT * FROM users WHERE UserID = %s"
    val = (UserID,)
    mycursor.execute(sql, val)
    number_of_rows = mycursor.fetchall()
    nums = len(number_of_rows)
    if nums < 1:
        sql = "INSERT INTO users (UserID, username, first_name, last_name, language_code, notifications, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (UserID, username, first_name, last_name, language_code, 1, 1)
        mycursor.execute(sql, val)
        mydb.commit()
        logging.info(f"[Database] {mycursor.rowcount} record inserted.")
        print(f"{dateandtime()} - [Database] {mycursor.rowcount} record inserted.")
        response = f"[Bot] ✅ New User added to Database [username: {username} - id: {UserID} - Name: {first_name} {last_name} - language_code : {language_code}]"
        logging.info(f"{response}")
        print(f"{dateandtime()} - {response}")
    mycursor.close()
    mydb.close()

def groups(group_id, group_username, group_name, group_type):
    mydb = mysql.connector.connect(
        host="Host Name",
        user="Username",
        password="Password",
        database="CryptoVerse_db"
    )
    mycursor = mydb.cursor()
    sql = "SELECT * FROM groups WHERE group_id = %s"
    val = (group_id,)
    mycursor.execute(sql, val)
    number_of_rows = mycursor.fetchall()
    nums = len(number_of_rows)
    if nums < 1:
        sql = "INSERT INTO groups (group_id, username, group_name, type, notifications, status) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (group_id, group_username, group_name, group_type, 1, 1)
        mycursor.execute(sql, val)
        mydb.commit()
        logging.info(f"[Database] {mycursor.rowcount} record inserted.")
        print(f"{dateandtime()} - [Database] {mycursor.rowcount} record inserted.")
        response = f"[Bot] ✅ New group added to Database [username: {group_username} - id: {group_id} - Name: {group_name} - type : {group_type}]"
        logging.info(f"{response}")
        print(f"{dateandtime()} - {response}")
    mycursor.close()
    mydb.close()

def check_user(UserID):
    mydb = mysql.connector.connect(
        host="Host Name",
        user="Username",
        password="Password",
        database="CryptoVerse_db"
    )
    mycursor = mydb.cursor()
    sql = "SELECT * FROM users WHERE UserID = %s"
    val = (UserID,)
    mycursor.execute(sql, val)
    number_of_rows = mycursor.fetchall()
    nums = len(number_of_rows)
    mycursor.close()
    mydb.close()
    if nums > 0:
        return True
    if nums < 1:
        return False

def start_command(update, context):
    connection()
    response = "Hello this is me CryptoVerse [Bot] 🤖\nI am here to assist you in Crypto World 🤑\nTo know how please enter /help ⚙️"
    update.message.reply_text(response)
    text = str(update.message.text)
    user = update.message.from_user
    #chat_id = update.message.chat_id
    #print(chat_id)
    logging.info(f"@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']} - Message : {text}")
    logging.info(f"[Bot] Type something random to get start!\n{dateandtime()} Telegram message: {update.message}")
    print(f"{dateandtime()} - @{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']} - Message : {text}")
    print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
    is_group = update.message['chat']['type']
    UserID = user['id']
    username = user['username']
    first_name = user['first_name']
    last_name = user['last_name']
    language_code = user['language_code']
    group_id = update.message['chat']['id']
    group_username = update.message['chat']['username']
    group_name = update.message['chat']['title']
    group_type = update.message['chat']['type']
    if is_group == "private":
        users(UserID, username, first_name, last_name, language_code)
    elif is_group == "group" or is_group == "supergroup":
        groups(group_id, group_username, group_name, group_type)

def help_command(update, context):
    connection()
    text = str(update.message.text)
    user = update.message.from_user
    is_group = update.message['chat']['type']
    if is_group == "private":
        response = "I can help you check any crypto currency info and set price alerts and manage them and much more. 😉\n\n<b>Private Chat Commands:</b>\n/coin [coin_name]   <i>show balance</i>\n<i>[Example: /coin btc]</i>\n\n/pair [pair_name]   <i>show balance of pair</i>\n<i>[Example: /pair btcusdt] <b>Binance only</b></i>\n\n/alert coin_name > or &lt; price  <i>\n[Example: /alert btc > 50000]</i>\n\n/alerts show all alerts and allow you to delete\n\n/btc_eth on <i><b>or</b></i> off (prices notification every 6 hours)\n\n#Binance coin listing announcement and reminder 1 hour prior trading launch\n\n\n<b>Group Commands:</b> <i>(Add me to your group)</i>\n/signals show all signals set by group's admins <i>(Admins mention #signals in a post to add [limit 15])</i>\n\n/ideas show all trading analysis of group's admins <i>(Admins mention #ideas in a post to add [limit 10])</i>\n\n#Notices send regular custom messages set by admins every 2 hours <i>(Admins mention #notice in a post to add [limit 6 - interval 2 hour]</i>\n\n/delnotice allow admins delete notices\n/dellnotice_all allow Group Creator (Owner) to delete all notices\n\n#BTC & #ETH prices notification every 6 hours\n\n<i>To enjoy my free group services just add me to your group without permissions i'm only messenger bot</i> 📨 🤖"
        logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
        logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
        print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        #update.message.bot.send_message(chat_id=user['id'], text=response, parse_mode='Markdown')
    else:
        group_name = update.message['chat']['title']
        if update.effective_user.id in get_admin_ids(context.bot, update.message.chat_id):
            UserID = user['id']
            if check_user(UserID) == True:
                response = f"Hi {user['first_name']} {user['last_name']} - <i>[Admin] 👮🏻</i>\nI can help you check any crypto currency info and set price alerts and manage them and much more. 😉\n\n/coin [coin_name]   <i>show balance</i>\n<i>[Example: /coin btc]</i>\n/pair [pair_name]   <i>show balance of pair</i>\n<i>[Example: /pair btcusdt] <b>Binance only</b></i>\n/alert coin_name > or &lt; price  <i>\n[Example: /alert btc > 50000]</i>\n/alerts show all alerts and allow you to delete\n/signals show all signals of {group_name} admins\n/ideas show all trading analysis of {group_name} admins\n\n<i>Admin Tools sent to you {bot_link}</i>"
                admin_tools = f"Hi {user['first_name']} {user['last_name']} - Admin of {group_name} 👮🏻\nHere are some commands assist you managing your group: 🧞‍♂️ \n\n#signals put it in any post and this post will be saved in /signals list so members of your group can see it (limit 15)\n#ideas put it in any post and this post will be saved in /ideas list so members of your group can see it (limit 10)\n#notice put it in any post and this post will be sent to all members (limit 6 - interval 2 hour)\n/delnotice delete notices created by admins\n/dellnotice\_all delete all notices created by Group Creator or Admins\n\nMuch more coming soon 😉"
                send_update(UserID, f"{admin_tools}")
                update.message.bot.send_message(chat_id=user['id'], text=admin_tools, parse_mode='Markdown')
                logging.info(f"[Bot] {admin_tools}\n{dateandtime()} Telegram message: {update.message}")
                print(f"{dateandtime()} - [Bot] {admin_tools}\n{dateandtime()} Telegram message: {update.message}")
            else:
                response = f"I can help you check any crypto currency info and set price alerts and manage them and much more. 😉\n\n/coin [coin_name]   <i>show balance</i>\n<i>[Example: /coin btc]</i>\n/pair [pair_name]   <i>show balance of pair</i>\n<i>[Example: /pair btcusdt] <b>Binance only</b></i>\n/alert coin_name > or &lt; price  <i>\n[Example: /alert btc > 50000]</i>\n/alerts show all alerts and allow you to delete\n/signals show all signals of {group_name} admins\n/ideas show all trading analysis of {group_name} admins\n\n<i>Admin Tools {bot_link} press start then type in {group_name} /help again.</i>"
            logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
            logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
            print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        else:
            response = f"I can help you check any crypto currency info and set price alerts and manage them and much more. 😉\n\n/coin [coin_name]   <i>show balance</i>\n<i>[Example: /coin btc]</i>\n/pair [pair_name]   <i>show balance of pair</i>\n<i>[Example: /pair btcusdt] <b>Binance only</b></i>\n/alert coin_name > or &lt; price  <i>\n[Example: /alert btc > 50000]</i>\n/alerts show all alerts and allow you to delete\n/signals show all signals of {group_name} admins\n/ideas show all trading analysis of {group_name} admins"
            logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
            logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
            print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
    update.message.reply_text(response)
    UserID = user['id']
    username = user['username']
    first_name = user['first_name']
    last_name = user['last_name']
    language_code = user['language_code']
    group_id = update.message['chat']['id']
    group_username = update.message['chat']['username']
    group_name = update.message['chat']['title']
    group_type = update.message['chat']['type']
    if is_group == "private":
        users(UserID, username, first_name, last_name, language_code)
    elif is_group == "group" or is_group == "supergroup":
        groups(group_id, group_username, group_name, group_type)

def hash_text(update, context):
    text = str(update.message.text).lower()
    user = update.message.from_user
    chat_id = update.message.chat_id
    is_group = update.message['chat']['type']
    group_name = update.message['chat']['title']
    message_id = update.message['message_id']
    if is_group == "group" or is_group == "supergroup":
        if update.effective_user.id in get_admin_ids(context.bot, update.message.chat_id):
            if "#signals" in text:
                    mydb = mysql.connector.connect(
                        host="Host Name",
                        user="Username",
                        password="Password",
                        database="CryptoVerse_db"
                    )
                    mycursor = mydb.cursor()
                    sql = "SELECT * FROM signals WHERE chat_id = %s"
                    val = (update.message.chat.id,)
                    mycursor.execute(sql, val)
                    number_of_rows = mycursor.fetchall()
                    nums = len(number_of_rows)
                    logging.info(f"[Database] number of rows {nums}")
                    print(f"{dateandtime()} - [Database] number of rows {nums}")
                    sql = "INSERT INTO signals (UserID, username, first_name, last_name, group_name, chat_id, message_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (user['id'], user['username'], user['first_name'], user['last_name'], group_name, chat_id, message_id, 1)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    logging.info(f"[Database] {mycursor.rowcount} record inserted.")
                    print(f"{dateandtime()} - [Database] {mycursor.rowcount} record inserted.")
                    response = f"✅ This signal has been saved in /signals list."
                    update.message.reply_text(response)
                    limit = 15
                    rows = nums - limit + 1
                    if nums >= limit:
                        sql = "DELETE FROM signals WHERE chat_id = %s ORDER BY id ASC LIMIT %s"
                        val = (chat_id, rows)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        logging.info(f"[Bot] Old signal(s) has been deleted ✅")
                        logging.info(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                        print(f"{dateandtime()} - [Bot]  Old signal(s) has been deleted ✅")
                        print(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                    mycursor.close()
                    mydb.close()
                    logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                    logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
                    print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                    print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            if "#ideas" in text:
                    #update.message.bot.forward_message(chat_id=user['id'], from_chat_id=update.message.chat.id,message_id=message_id)
                    mydb = mysql.connector.connect(
                        host="Host Name",
                        user="Username",
                        password="Password",
                        database="CryptoVerse_db"
                    )
                    mycursor = mydb.cursor()
                    sql = "SELECT * FROM ideas WHERE chat_id = %s"
                    val = (update.message.chat.id,)
                    mycursor.execute(sql, val)
                    number_of_rows = mycursor.fetchall()
                    nums = len(number_of_rows)
                    logging.info(f"[Database] number of rows {nums}")
                    print(f"{dateandtime()} - [Database] number of rows {nums}")
                    sql = "INSERT INTO ideas (UserID, username, first_name, last_name, group_name, chat_id, message_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (user['id'], user['username'], user['first_name'], user['last_name'], group_name, chat_id, message_id, 1)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    logging.info(f"[Database] {mycursor.rowcount} record inserted.")
                    print(f"{dateandtime()} - [Database] {mycursor.rowcount} record inserted.")
                    response = f"✅ This idea has been saved in /ideas list."
                    update.message.reply_text(response)
                    limit = 10
                    rows = nums - limit + 1
                    if nums >= limit:
                        sql = "DELETE FROM ideas WHERE chat_id = %s ORDER BY id ASC LIMIT %s"
                        val = (chat_id, rows)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        logging.info(f"[Bot] Old ideas(s) has been deleted ✅")
                        logging.info(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                        print(f"{dateandtime()} - [Bot]  Old ideas(s) has been deleted ✅")
                        print(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                    mycursor.close()
                    mydb.close()
                    logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                    logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
                    print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                    print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            if "#notice" in text:
                    #update.message.bot.forward_message(chat_id=user['id'], from_chat_id=update.message.chat.id,message_id=message_id)
                    mydb = mysql.connector.connect(
                        host="Host Name",
                        user="Username",
                        password="Password",
                        database="CryptoVerse_db"
                    )
                    mycursor = mydb.cursor()
                    sql = "SELECT * FROM notice WHERE chat_id = %s"
                    val = (update.message.chat.id,)
                    mycursor.execute(sql, val)
                    number_of_rows = mycursor.fetchall()
                    nums = len(number_of_rows)
                    logging.info(f"[Database] number of rows {nums}")
                    print(f"{dateandtime()} - [Database] number of rows {nums}")
                    sql = "INSERT INTO notice (UserID, username, first_name, last_name, group_name, chat_id, message_id, cycle, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (user['id'], user['username'], user['first_name'], user['last_name'], group_name, chat_id, message_id, 3, 1)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    logging.info(f"[Database] {mycursor.rowcount} record inserted.")
                    print(f"{dateandtime()} - [Database] {mycursor.rowcount} record inserted.")
                    response = f"✅ This notice has been saved in notification list."
                    update.message.reply_text(response)
                    limit = 6
                    rows = nums - limit + 1
                    if nums >= limit:
                        print(chat_id)
                        print(nums)
                        sql = "DELETE FROM notice WHERE chat_id = %s ORDER BY id ASC LIMIT %s"
                        val = (chat_id, rows)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        logging.info(f"[Bot] Old notice(s) has been deleted ✅")
                        logging.info(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                        print(f"{dateandtime()} - [Bot]  Old notice(s) has been deleted ✅")
                        print(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                    mycursor.close()
                    mydb.close()
                    logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                    logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
                    print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                    print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
    else:
        response = "I'm a bot so I try to interact with humans and learn to become usefel robot 😊\nI can help you check any crypto currency info and set price alerts and manage them and much more. 😉\n\n<b>Private Chat Commands:</b>\n/coin [coin_name]   <i>show balance</i>\n<i>[Example: /coin btc]</i>\n\n/pair [pair_name]   <i>show balance of pair</i>\n<i>[Example: /pair btcusdt] <b>Binance only</b></i>\n\n/alert coin_name > or &lt; price  <i>\n[Example: /alert btc > 50000]</i>\n\n/alerts show all alerts and allow you to delete\n\n/btc_eth on <i><b>or</b></i> off (prices notification every 6 hours)\n\n#Binance coin listing announcement and reminder 1 hour prior trading launch\n\n\n<b>Group Commands:</b> <i>(Add me to your group)</i>\n/signals show all signals set by group's admins <i>(Admins mention #signals in a post to add [limit 15])</i>\n\n/ideas show all trading analysis of group's admins <i>(Admins mention #ideas in a post to add [limit 10])</i>\n\n#Notices send regular custom messages set by admins every 2 hours <i>(Admins mention #notice in a post to add [limit 6 - interval 2 hour]</i>\n\n/delnotice allow admins delete notices\n/dellnotice_all allow Group Creator (Owner) to delete all notices\n\n#BTC & #ETH prices notification every 6 hours\n\n<i>To enjoy my free group services just add me to your group without permissions i'm only messenger bot</i> 📨 🤖"
        update.message.reply_text(response)
        logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
        logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
        print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")

def hash_media(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    is_group = update.message['chat']['type']
    group_name = update.message['chat']['title']
    message_id = update.message['message_id']
    if update.message['photo']:
        text = str(update.message['caption']).lower()
    elif update.message['document']:
        text = str(update.message['caption']).lower()
    else:
        text = f"{dateandtime()} - [Bot] Unable to insert this message \n{dateandtime()} Telegram message: {update.message}"
        logging.warning(f"[Bot] {text}\n{dateandtime()} Telegram message: {update.message}")
        print(f"{dateandtime()} - [Bot] {text}\n{dateandtime()} Telegram message: {update.message}")
    if is_group == "group" or is_group == "supergroup":
        if update.effective_user.id in get_admin_ids(context.bot, update.message.chat_id):
            if "#signals" in text:
                    #update.message.bot.forward_message(chat_id=user['id'], from_chat_id=update.message.chat.id,message_id=message_id)
                    mydb = mysql.connector.connect(
                        host="Host Name",
                        user="Username",
                        password="Password",
                        database="CryptoVerse_db"
                    )
                    mycursor = mydb.cursor()
                    sql = "SELECT * FROM signals WHERE chat_id = %s"
                    val = (update.message.chat.id,)
                    mycursor.execute(sql, val)
                    number_of_rows = mycursor.fetchall()
                    nums = len(number_of_rows)
                    logging.info(f"[Database] number of rows {nums}")
                    print(f"{dateandtime()} - [Database] number of rows {nums}")
                    sql = "INSERT INTO signals (UserID, username, first_name, last_name, group_name, chat_id, message_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (user['id'], user['username'], user['first_name'], user['last_name'], group_name, chat_id, message_id, 1)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    logging.info(f"[Database] {mycursor.rowcount} record inserted.")
                    print(f"{dateandtime()} - [Database] {mycursor.rowcount} record inserted.")
                    response = f"✅ This signal has been saved in /signals list."
                    update.message.reply_text(response)
                    limit = 15
                    rows = nums - limit + 1
                    if nums >= limit:
                        sql = "DELETE FROM signals WHERE chat_id = %s ORDER BY id ASC LIMIT %s"
                        val = (chat_id, rows)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        logging.info(f"[Bot] Old signal(s) has been deleted ✅")
                        logging.info(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                        print(f"{dateandtime()} - [Bot]  Old signal(s) has been deleted ✅")
                        print(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                    mycursor.close()
                    mydb.close()
                    logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] [Media Message] {str(update.message['caption'])}")
                    logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
                    print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] [Media Message] {str(update.message['caption'])}")
                    print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            if "#ideas" in text:
                    #update.message.bot.forward_message(chat_id=user['id'], from_chat_id=update.message.chat.id,message_id=message_id)
                    mydb = mysql.connector.connect(
                        host="Host Name",
                        user="Username",
                        password="Password",
                        database="CryptoVerse_db"
                    )
                    mycursor = mydb.cursor()
                    sql = "SELECT * FROM ideas WHERE chat_id = %s"
                    val = (update.message.chat.id,)
                    mycursor.execute(sql, val)
                    number_of_rows = mycursor.fetchall()
                    nums = len(number_of_rows)
                    logging.info(f"[Database] number of rows {nums}")
                    print(f"{dateandtime()} - [Database] number of rows {nums}")
                    sql = "INSERT INTO ideas (UserID, username, first_name, last_name, group_name, chat_id, message_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (user['id'], user['username'], user['first_name'], user['last_name'], group_name, chat_id, message_id, 1)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    logging.info(f"[Database] {mycursor.rowcount} record inserted.")
                    print(f"{dateandtime()} - [Database] {mycursor.rowcount} record inserted.")
                    response = f"✅ This idea has been saved in /ideas list."
                    update.message.reply_text(response)
                    limit = 10
                    rows = nums - limit + 1
                    if nums >= limit:
                        sql = "DELETE FROM ideas WHERE chat_id = %s ORDER BY id ASC LIMIT %s"
                        val = (chat_id, rows)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        logging.info(f"[Bot] Old idea(s) has been deleted ✅")
                        logging.info(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                        print(f"{dateandtime()} - [Bot]  Old idea(s) has been deleted ✅")
                        print(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                    mycursor.close()
                    mydb.close()
                    logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] [Media Message] {str(update.message['caption'])}")
                    logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
                    print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] [Media Message] {str(update.message['caption'])}")
                    print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            if "#notice" in text:
                # update.message.bot.forward_message(chat_id=user['id'], from_chat_id=update.message.chat.id,message_id=message_id)
                mydb = mysql.connector.connect(
                    host="Host Name",
                    user="Username",
                    password="Password",
                    database="CryptoVerse_db"
                )
                mycursor = mydb.cursor()
                sql = "SELECT * FROM notice WHERE chat_id = %s"
                val = (update.message.chat.id,)
                mycursor.execute(sql, val)
                number_of_rows = mycursor.fetchall()
                nums = len(number_of_rows)
                logging.info(f"[Database] number of rows {nums}")
                print(f"{dateandtime()} - [Database] number of rows {nums}")
                sql = "INSERT INTO notice (UserID, username, first_name, last_name, group_name, chat_id, message_id, cycle, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (user['id'], user['username'], user['first_name'], user['last_name'], group_name, chat_id, message_id, 3, 1)
                mycursor.execute(sql, val)
                mydb.commit()
                logging.info(f"[Database] {mycursor.rowcount} record inserted.")
                print(f"{dateandtime()} - [Database] {mycursor.rowcount} record inserted.")
                response = f"✅ This notice has been saved in notifications list."
                update.message.reply_text(response)
                limit = 6
                rows = nums - limit + 1
                if nums >= limit:
                    sql = "DELETE FROM notice WHERE chat_id = %s ORDER BY id ASC LIMIT %s"
                    val = (chat_id, rows)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    logging.info(f"[Bot] Old notice(s) has been deleted ✅")
                    logging.info(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                    print(f"{dateandtime()} - [Bot]  Old notice(s) has been deleted ✅")
                    print(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                mycursor.close()
                mydb.close()
                logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] [Media Message] {str(update.message['caption'])}")
                logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
                print(
                    f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] [Media Message] {str(update.message['caption'])}")
                print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        else:
            response = f"This feature is only available in Groups\nAdd me to your group and enjoy my services 😉"
            update.message.reply_text(response)
            logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
    else:
        response = "I'm a bot so I try to interact with humans and learn to become usefel robot 😊\nI can help you check any crypto currency info and set price alerts and manage them and much more soon. 😉\n\n/coin [coin_name]\n<i>[Example: /coin btc]</i>\n/alert coin_name > or &lt; price  <i>\n[Example: /alert btc > 50000]</i>\n/alerts show all alerts and allow you to delete"
        update.message.reply_text(response)
        logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
        logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {text}")
        print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")

def error(update, context):
    logging.error(f"Update {update} caused error {context.error}")
    print(f"{dateandtime()} ERROR: Update {update} caused error {context.error}")

def coin_command(update, context):
    connection()
    symbol = str(update.message.text).lower().replace("/coin ", "")
    user = update.message.from_user
    # Opening JSON file
    with open('coins_list.json', encoding="utf8") as json_file:
        data = json.load(json_file)
        # Define a function to search the item
        def search_price(name):
            for keyval in data:
                if name.lower() == keyval['symbol'].lower() or name.lower() == keyval['id'].lower()or name.lower() == keyval['name'].lower():
                    return keyval['id']
        # Check the return value and print message
        if (search_price(symbol) != None):
            coin = search_price(symbol)
        else:
            response = "❌ Invalid coin name, Please try again.\n<i>[Example: /coin btc]</i>"
            logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            logging.warning(f"[Bot] {response}")
            print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            print(f"{dateandtime()} - [Bot] {response}")
            update.message.reply_text(response)

    cg = CoinGeckoAPI()
    get_price = cg.get_price(coin, vs_currencies='usd', include_market_cap=True, include_24hr_vol=True, include_24hr_change=True, include_last_updated_at=True)

    if 'e' in str(get_price[coin]['usd']):
        price = "%.12f" % get_price[coin]['usd']
    else:
        price = get_price[coin]['usd']

    usd_market_cap = human_format(get_price[coin]['usd_market_cap'])
    usd_24h_vol = human_format(get_price[coin]['usd_24h_vol'])
    usd_24h_change = '{:.1f}'.format(get_price[coin]['usd_24h_change'])
    last_updated_at = get_price[coin]['last_updated_at']
    updated_date_time = datetime.fromtimestamp(last_updated_at) + timedelta(hours=-17)
    trx_date_time = updated_date_time.strftime("%d/%m/%Y - %I:%M %p")
    response = f"🔹<b>{coin.title()}</b>🔹\n💰Price: {price} 💵\n🧢Market Cap: {usd_market_cap}\n💧24h Volume: {usd_24h_vol}\n📊24h Change: {usd_24h_change}%\n⏱Updated: {trx_date_time} (UTC)"
    update.message.reply_text(response)
    logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
    logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
    print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
    print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")

def get_price(symbol):
    prices = requests.get('https://api.binance.com/api/v3/ticker/price').json()
    for price in prices:
        if symbol == price['symbol']:
            if float(price['price']) < 1:
                subprice = "%.12f" % float(price['price'])
                price = subprice.rstrip('0').rstrip('.')
            else:
                price = float(price['price'])
            return price

def binancepair_command(update, context):
    connection()
    user = update.message.from_user
    if len(context.args) > 0 and len(context.args) < 2:
        pair = context.args[0].upper()
        if get_price(pair) is not None:
            price = get_price(pair)
            response = f"🔹<b>{pair}</b>🔹\n💰Binance Price: {price}"
        else:
            response = f"❌ Invalid pair or {pair} is not listed in Binance, Please try again.\n<i>[Example: /pair btcusdt]</i>"
    else:
        response = "❌ Invalid command, Please try again.\n<i>[Example: /pair btcusdt]</i>"
    logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
    logging.warning(f"[Bot] {response}")
    print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
    print(f"{dateandtime()} - [Bot] {response}")
    update.message.reply_text(response)

def set_alert_command(update, context):
    connection()
    user = update.message.from_user
    message = update.message
    is_group = message['chat']['type']
    if is_group == "private":
        if len(context.args) > 2:
            crypto = context.args[0].lower()
            sign = context.args[1]
            alert_price = context.args[2]
            # Opening JSON file
            with open('coins_list.json', encoding="utf8") as json_file:
                data = json.load(json_file)
                # Define a function to search the item
                def search_price(name):
                    for keyval in data:
                        if name.lower() == keyval['symbol'].lower() or name.lower() == keyval['id'].lower() or name.lower() == keyval['name'].lower():
                            return keyval['id']
                # Check the return value and print message
                if (search_price(crypto) != None):
                    coin = search_price(crypto)

                    cg = CoinGeckoAPI()
                    get_price = cg.get_price(coin, vs_currencies='usd', include_market_cap=True, include_24hr_vol=True, include_24hr_change=True, include_last_updated_at=True)

                    if 'e' in str(get_price[coin]['usd']):
                        price = "%.10f" % get_price[coin]['usd']
                    else:
                        price = get_price[coin]['usd']

                    if sign == ">" or sign == "<":
                        mydb = mysql.connector.connect(
                            host="Host Name",
                            user="Username",
                            password="Password",
                            database="CryptoVerse_db"
                        )
                        mycursor = mydb.cursor()
                        sql = "SELECT * FROM price_alert WHERE UserID = %s"
                        val = (user['id'],)
                        mycursor.execute(sql, val)
                        number_of_rows = mycursor.fetchall()
                        nums = len(number_of_rows)
                        logging.info(f"[Database] number of rows {nums}")
                        print(f"{dateandtime()} - [Database] number of rows {nums}")
                        limit = 15
                        if nums < limit:
                            sql = "INSERT INTO price_alert (UserID, username, first_name, last_name, coin, price, current_price, sign, alert_price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            val = (user['id'], user['username'], user['first_name'], user['last_name'], coin, price, price, sign, alert_price, 1)
                            mycursor.execute(sql, val)
                            mydb.commit()
                            logging.info(f"[Database] {mycursor.rowcount} record inserted.")
                            print(f"{dateandtime()} - [Database] {mycursor.rowcount} record inserted.")
                            if sign == "<":
                                sign_symbol = "&lt;"
                            else:
                                sign_symbol = ">"
                            response = f"✅ Alarm set successfully as <b>{crypto} {sign_symbol} {alert_price}</b>\nI will send you a message when the price of <b>{crypto.upper()}</b> reaches <b>{alert_price} USD</b> ⏰\n"
                            response += f"The current price of <b>{crypto.upper()}</b> is <b>{price} USD</b>"
                        else:
                            response = f"⚠️ Maximum alerts limit reached. [{limit}]\nPlease enter /alerts to show your alerts list and delete some of them."
                        mycursor.close()
                        mydb.close()
                    else:
                        response = "Wrong sign please use > or < only."
                else:
                    response = "❌ Invalid coin name, Please try again."
        else:
            response = '⚠️ Please provide a coin name and a price value \n<i>/alert coin name > or &lt; price\n [Example: /alert btc > 50000]</i>'
    else:
        group_name = message['chat']['title']
        response = f"This feature is only available in private mode\nMessage me @CryptoVerse_RoBot privately to set your alerts."

    update.message.reply_text(response)
    logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
    logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
    print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
    print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")

def alert_list_command(update: Update, context: CallbackContext) -> None:
    connection()
    user = update.message.from_user
    is_group = update.message['chat']['type']
    if is_group == "private":
        mydb = mysql.connector.connect(
            host="Host Name",
            user="Username",
            password="Password",
            database="CryptoVerse_db"
        )
        mycursor = mydb.cursor()
        sql = "SELECT * FROM price_alert WHERE UserID = %s"
        val = (user['id'],)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
        print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
        for x in myresult:
            #print(f"{x[6]} {x[8]} {x[9]}")
            #print(f"{dateandtime()} - [Bot] @{user['username']} - id: {user['id']} fetched all alerts \n{dateandtime()} Telegram message: {update.message}")
            option = f"{x[5].title()} {x[8]} {x[9]}"
            data = x[0]
            keyboard = [
                [
                    InlineKeyboardButton(f"{option} ❌", callback_data=data)
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Please click on the alert to delete it:', reply_markup=reply_markup)
            time.sleep(2)
        mycursor.close()
        mydb.close()
        logging.info(f"[Bot] @{user['username']} - id: {user['id']} fetched all alerts \n{dateandtime()} Telegram message: {update.message}")
        print(f"{dateandtime()} - [Bot] @{user['username']} - id: {user['id']} fetched all alerts \n{dateandtime()} Telegram message: {update.message}")
    else:
        response = f"This feature is only available in private mode\nMessage me {bot_link} privately to set, check and delete your alerts."
        update.message.reply_text(response)
        logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
        logging.warning(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
        print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.edit_message_text(text=f"✅ Alert has been deleted")
    mydb = mysql.connector.connect(
        host="Host Name",
        user="Username",
        password="Password",
        database="CryptoVerse_db"
    )
    mycursor = mydb.cursor()
    sql = "DELETE FROM price_alert WHERE id = %s"
    adr = (query.data,)
    mycursor.execute(sql, adr)
    mydb.commit()
    mycursor.close()
    mydb.close()
    logging.info(f"[Bot] Alert id: {query.data} has been deleted ✅")
    logging.info(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
    print(f"{dateandtime()} - [Bot] Alert id: {query.data} has been deleted ✅")
    print(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")

def btceth_notification_command(update, context):
    connection()
    user = update.message.from_user
    message = update.message
    is_group = message['chat']['type']
    if is_group == "private":
        if len(context.args) > 0:
            onoff = context.args[0].lower()
            if onoff == "on":
                mydb = mysql.connector.connect(
                    host="Host Name",
                    user="Username",
                    password="Password",
                    database="CryptoVerse_db"
                )
                mycursor = mydb.cursor()
                sql = "UPDATE users SET notifications = %s WHERE UserID = %s"
                val = (1, user['id'])
                mycursor.execute(sql, val)
                mydb.commit()
                response = f"🟢 #BTC & #ETH notifications turned on."
            elif onoff == "off":
                mydb = mysql.connector.connect(
                    host="Host Name",
                    user="Username",
                    password="Password",
                    database="CryptoVerse_db"
                )
                mycursor = mydb.cursor()
                sql = "UPDATE users SET notifications = %s WHERE UserID = %s"
                val = (0, user['id'])
                mycursor.execute(sql, val)
                mydb.commit()
                response = f"🔴 #BTC & #ETH notifications turned off."
            else:
                response = f"❌ Invalid command please type /btc_eth on  <b><i>or</i></b>  /btc_eth off"
            update.message.reply_text(response)
            logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")

def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    #for item in bot.get_chat_administrators(chat_id):
    #    print(item)
    #    print(item['status'])
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

def get_admin_ids2(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    admins_list = []
    for item in bot.get_chat_administrators(chat_id):
        #print(item)
        #print(item['status'])
        admins_list.append(item)
    return admins_list

def signals_command(update, context):
    connection()
    #text = str(update.message.text).lower()
    user = update.message.from_user
    is_group = update.message['chat']['type']
    group_name = update.message['chat']['title']
    chat_id = update.message.chat_id
    if is_group == "group" or is_group == "supergroup":
        UserID = user['id']
        if check_user(UserID) == True:
            mydb = mysql.connector.connect(
                host="Host Name",
                user="Username",
                password="Password",
                database="CryptoVerse_db"
            )
            mycursor = mydb.cursor()
            sql = "SELECT * FROM signals WHERE chat_id = %s"
            val = (chat_id,)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            for x in myresult:
                update.message.bot.forward_message(chat_id=user['id'], from_chat_id=update.message.chat.id, message_id=x[7])
                time.sleep(2)
            mycursor.close()
            mydb.close()
            logging.info(f"[Bot] {mycursor.rowcount} signal(s) sent to @{user['username']} - id: {user['id']}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [Bot] {mycursor.rowcount} signal(s) sent to @{user['username']} - id: {user['id']}\n{dateandtime()} Telegram message: {update.message}")
            response = f"All signals of {group_name} sent {bot_link}"
            update.message.reply_text(response)
            logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        else:
            response = f"Please message me first {bot_link} click start to allow me send you group's signals 😉"
            update.message.reply_text(response)
            logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
    else:
        response = f"This feature is only available in Groups\nAdd me to your group and enjoy my services 😉"
        update.message.reply_text(response)
        logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
        logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
        print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")

def ideas_command(update, context):
    connection()
    user = update.message.from_user
    is_group = update.message['chat']['type']
    group_name = update.message['chat']['title']
    chat_id = update.message.chat_id
    if is_group == "group" or is_group == "supergroup":
        UserID = user['id']
        if check_user(UserID) == True:
            mydb = mysql.connector.connect(
                host="Host Name",
                user="Username",
                password="Password",
                database="CryptoVerse_db"
            )
            mycursor = mydb.cursor()
            sql = "SELECT * FROM ideas WHERE chat_id = %s"
            val = (chat_id,)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            for x in myresult:
                update.message.bot.forward_message(chat_id=user['id'], from_chat_id=update.message.chat.id, message_id=x[7])
                time.sleep(2)
            mycursor.close()
            mydb.close()
            logging.info(f"[Bot] {mycursor.rowcount} idea(s) sent to @{user['username']} - id: {user['id']}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [Bot] {mycursor.rowcount} idea(s) sent to @{user['username']} - id: {user['id']}\n{dateandtime()} Telegram message: {update.message}")
            response = f"All ideas of {group_name} sent {bot_link}"
            update.message.reply_text(response)
            logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        else:
            response = f"Please message me first {bot_link} click start to allow me send you group's ideas 😉"
            update.message.reply_text(response)
            logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
            print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
            print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
    else:
        response = f"This feature is only available in Groups\nAdd me to your group and enjoy my services 😉"
        update.message.reply_text(response)
        logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
        logging.info(f"[Bot] {response}\n{dateandtime()} Telegram message: {update.message}")
        print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
        print(f"{dateandtime()} - [Bot] {response}\n{dateandtime()} Telegram message: {update.message}")

def del_notice_command(update, context):
    #connection()
    user = update.message.from_user
    is_group = update.message['chat']['type']
    group_name = update.message['chat']['title']
    #group_link = update.message['chat']['username']
    if is_group == "group" or is_group == "supergroup":
        if update.effective_user.id in get_admin_ids(context.bot, update.message.chat_id):
            UserID = user['id']
            mydb = mysql.connector.connect(
                host="Host Name",
                user="Username",
                password="Password",
                database="CryptoVerse_db"
                )
            mycursor = mydb.cursor()
            sql = "DELETE FROM notice WHERE chat_id = %s AND UserID = %s"
            adr = (update.message.chat_id, UserID)
            mycursor.execute(sql, adr)
            mydb.commit()
            mycursor.close()
            mydb.close()
            if mycursor.rowcount > 0:
                if check_user(UserID) == True:
                    response = f"✅ {mycursor.rowcount} notices(s) deleted of {group_name}\n"
                    send_update(UserID, f"{response}")
                    #context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
                else:
                    response = f"✅ {mycursor.rowcount} notices(s) deleted of {group_name}\n<i>Please message me {bot_link} click start for future notifications</i>"
                    update.message.reply_text(response)
                logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                logging.info(f"[Bot] {response}")
                logging.info(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                print(f"{dateandtime()} - [Bot] {response}")
                print(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")

def delall_notice_command(update, context):
    #connection()
    user = update.message.from_user
    is_group = update.message['chat']['type']
    group_name = update.message['chat']['title']
    #group_link = update.message['chat']['username']
    if is_group == "group" or is_group == "supergroup":
        if update.effective_user.id in get_admin_ids(context.bot, update.message.chat_id):
            admin_dict = get_admin_ids2(context.bot, update.message.chat_id)
            def in_dictlist(key, value, my_dictlist):
                for entry in my_dictlist:
                    if entry[key] == value:
                        return entry
                return {}
            # dict of creators
            creator_status = in_dictlist("status", "creator", admin_dict)
            UserID = user['id']
            if creator_status['user'] == user:
                mydb = mysql.connector.connect(
                    host="Host Name",
                    user="Username",
                    password="Password",
                    database="CryptoVerse_db"
                    )
                mycursor = mydb.cursor()
                sql = "DELETE FROM notice WHERE chat_id = %s"
                adr = (update.message.chat_id,)
                mycursor.execute(sql, adr)
                mydb.commit()
                mycursor.close()
                mydb.close()
                if mycursor.rowcount > 0:
                    if check_user(UserID) == True:
                        response = f"✅ {mycursor.rowcount} notices(s) deleted of {group_name}\n"
                        send_update(UserID, f"{response}")
                    else:
                        response = f"✅ {mycursor.rowcount} notices(s) deleted of {group_name}\n<i>Please message me {bot_link} click start for future notifications</i>"
                        update.message.reply_text(response)
                    logging.info(f"[@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                    print(f"{dateandtime()} - [@{user['username']} - id: {user['id']} - Name: {user['first_name']} {user['last_name']}] {str(update.message.text)}")
                    logging.info(f"[Bot] {response}")
                    logging.info(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")
                    print(f"{dateandtime()} - [Bot] {response}")
                    print(f"{dateandtime()} - [Database] {mycursor.rowcount} record(s) deleted")

def delete_join_leaving(update, context):
    context.bot.delete_message(chat_id=-1001666988056, message_id=update.message.message_id)
    logging.info(f"[Bot] Auto removing of joining & leaving messages\n{dateandtime()} Telegram message: {update.message}")
    print(f"{dateandtime()} - [Bot] Auto removing of joining & leaving messages\n{dateandtime()} Telegram message: {update.message}")

# def shutdown():
#     updater.stop()
#     updater.is_idle = False

def stop(update: Update, context: CallbackContext) -> None:
    text = f"🔴 {bot_name} shutdown.\nPID: {os.getpid()} - signal: {signal.SIGINT}"
    logging.info(f"{text}\n{dateandtime()} Telegram message: {update.message}")
    print(f"{dateandtime()} {text}\n{dateandtime()} Telegram message: {update.message}")
    update.message.bot.send_message(chat_id=telegram_user, text=text)
    os.kill(os.getpid(), signal.SIGINT)
    #threading.Thread(target=shutdown).start()

def main():
    config = configparser.ConfigParser()
    config.read('Telegram_Bot.ini')
    # worker_nums = int(config["DEFAULT"]['worker_nums'])
    config["DEFAULT"]['pid'] = str(os.getpid())
    with open('Telegram_Bot.ini', 'w') as configfile:  # save
        config.write(configfile)
    start = f"🟢 {bot_name} started... PID: {os.getpid()}"
    logging.info(start)
    print(f"{dateandtime()} {start}")
    send_update(telegram_user, start)
    connection()
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("coin", coin_command))
    dp.add_handler(CommandHandler("pair", binancepair_command))
    dp.add_handler(CommandHandler("alert", set_alert_command))
    dp.add_handler(CommandHandler("alerts", alert_list_command))
    dp.add_handler(CommandHandler("signals", signals_command))
    dp.add_handler(CommandHandler("ideas", ideas_command))
    dp.add_handler(CommandHandler("delnotice", del_notice_command))
    dp.add_handler(CommandHandler("delnotice_all", delall_notice_command))
    dp.add_handler(CommandHandler("btc_eth", btceth_notification_command))
    dp.add_handler(CommandHandler('stop429122022', stop))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, delete_join_leaving))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, delete_join_leaving))
    dp.add_handler(MessageHandler(Filters.text, hash_text))
    dp.add_handler(MessageHandler(Filters.caption, hash_media))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

updater = Updater(bot_key, use_context=True, defaults=Defaults(parse_mode=ParseMode.HTML))

if __name__ == '__main__':
    main()
