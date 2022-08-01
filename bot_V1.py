import email

import telebot
import imaplib

TOKEN = '5544464435:AAGMjK8GrxRRVYq29JCTCmibqznMK4UsZ4s'  # тут поставить свой токен
bot = telebot.TeleBot(TOKEN)


# CHANNEL_NAME = '@NewMail'


def reads(username, password, message, sender_of_interest=None):
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
    for e_id in unread_msg_nums:
        e_id = e_id.decode('utf-8')
        _, response = imap.uid('fetch', e_id, '(RFC822)')
        html = response[0][1].decode('utf-8')
        email_message = email.message_from_string(html)
        data_list.append(email_message.get_payload())

    for elem in data_list:
        bot.send_message(message.chat.id, 'Пришло новое сообщение!')


@bot.message_handler(commands=["start"])
def newmail(message):
    bot.send_message(message.chat.id, 'Привет! Тут будут появлятся уведомления о новых письмах)')
    while True:
        reads('fortestingbots@yandex.ru', 'fortestingbots12345', message)  # имя пароль для почты яндекс


bot.polling(non_stop=True)
