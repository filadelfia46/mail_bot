import email

import telebot
import imaplib

from telebot import types
import config

TOKEN = '5544464435:AAGMjK8GrxRRVYq29JCTCmibqznMK4UsZ4s'  # тут поставить свой токен
bot = telebot.TeleBot(TOKEN)


# CHANNEL_NAME = '@NewMail'

naiming = []
password = []


def see(e_id,imap,message): #вывод содержимого письма
    result, data = imap.fetch(e_id, "(RFC822)")
    raw_email = data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)
    k = len(email_message['To'])
    bot.send_message(message.chat.id, 'На почту '+ email_message['To'][:(-k//2)] +' пришло новое сообщение!' )
    #print(email_message['To'])
    #print(email.utils.parseaddr(email_message['From']))
    #print(email_message['Date'])
    #print(email_message['Subject'])
   # print(email_message['Message-Id'])
   # if email_message.is_multipart():
        #for payload in email_message.get_payload():
           # body = payload.get_payload(decode=True).decode('utf-8')
            #print(body)
    #else:
       # body = email_message.get_payload(decode=True).decode('utf-8')
        #print(body)


def reads(username, password, message, sender_of_interest=None): #проверка новых писем

    imap = imaplib.IMAP4_SSL("imap.yandex.ru", 993)  # тут можно изменить тип почты
    imap.login(username, password)
    imap.select('INBOX')
    if sender_of_interest:
        status, response = imap.uid('search', None, 'UNSEEN', 'FROM {0}'.format(sender_of_interest))
    else:
        status, response = imap.uid('search', None, 'UNSEEN')
    if status == 'OK':
        unread_msg_nums = response[0].split()
    else:
        unread_msg_nums = []
    data_list = []

    #
    global check
    if check == 0:
        check = 1
        bot.send_message(message.chat.id,
                         'Регистрация прошла успешно! Здесь будут появляться уведомления о новых сообщениях')
        bot.send_message(message.chat.id,
                         'Напиши /new, если захочешь добавить почту')
    #

    for e_id in unread_msg_nums:
        see(e_id, imap, message)
        e_id = e_id.decode('utf-8')
        _, response = imap.uid('fetch', e_id, '(RFC822)')

        html = response[0][1] .decode('utf-8')
        email_message = email.message_from_string(html)
        data_list.append(email_message.get_payload())



    if message.text == '/start':
        start(message)

    #for elem in data_list:
        #bot.send_message(message.chat.id, 'Пришло новое сообщение!')


def new(message):
    global naiming
    global password
    global check

    if check == 0:
        naiming = naiming[:-1]
        password = password[:-1]
        bot.send_message(message.chat.id, 'Неверные данные почты(')

    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так(')

    bot.send_message(message.chat.id, 'Перезапуск...')
    start(message)


name = ''
passw = ''
check = 0

@bot.message_handler(commands=["start"])
def start(message):
    global naiming

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить почту")
    btn2 = types.KeyboardButton("Начать работу")
    markup.add(btn1, btn2)
    #bot.register_next_step_handler(message, func)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я буду помогать тебе проверять почту)".format(
                         message.from_user), reply_markup=markup)
    bot.register_next_step_handler(message, func)

def func(message):
    a = telebot.types.ReplyKeyboardRemove()
    if message.text == "Добавить почту":
        bot.send_message(message.from_user.id,
                         "Для начала работы необходимо провести настройку https://www.dmosk.ru/miniinstruktions.php?mini=connect-imap-mail")
        bot.send_message(message.from_user.id, "Мне нужно название почты Яндекс (без @yandex.ru)", reply_markup=a)
        bot.register_next_step_handler(message, get_name)
    elif message.text == "Начать работу":
        bot.send_message(message.from_user.id, "Напиши /new, если захочешь добавить почту", reply_markup=a)
        bot.send_message(message.chat.id, 'Здесь будут появляться уведомления о новых сообщениях')
        bot.register_next_step_handler(message, run)


def get_name(message):  # получаем название
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Введите пароль')
    bot.register_next_step_handler(message, get_password)


def get_password(message):  # получаем пароль
    global passw
    passw = message.text
    run(message)#


def run(message):
    global check
    global naiming
    global password
    global passw
    global name

    check = 0

    naiming.append(name)
    password.append(passw)

    print(naiming[0], password[0])
    while True:
        try:
            for i in range(len(naiming)-1, -1, -1):
                a = naiming[i] + '@yandex.ru'
                reads(a, password[i], message)  # имя пароль для почты яндекс

        except Exception:
            break
    new(message)


@bot.message_handler(commands=["new"])#добавить почту
def new_name_mail(message):
    get_name(message)


bot.polling(non_stop=True)
