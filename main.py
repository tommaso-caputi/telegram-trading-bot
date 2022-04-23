import telebot
import trading
import time
from threading import Thread
import re

api_token = 'insert your telegram bot api token'

telegram_bot = telebot.TeleBot(api_token)
def start():
	telegram_bot.polling()
t = Thread(target=start, daemon=True)
run = False
trading_bot = trading.trading_bot("1m")
last_date = None
	

@telegram_bot.message_handler(func=lambda message: message.text == 'stop' or message.text == 'start' or message.text == 'open trade' or message.text == 'close trade' or message.text == 'data' or message.text == 'long' or message.text == 'short')
def all(message):
	global run 
	
	if message.text == 'start':
		run = True
	
	elif message.text == 'stop':
		run = False
	
	elif message.text == 'long':
		start(message)
		trading_bot.open('buy')
	elif message.text == 'short':
		start(message)
		trading_bot.open('sell')

	elif message.text == 'open trade':
		if trading_bot.opentrade:
			telegram_bot.send_message(message.chat.id, "Can't open a trade")
		else:
			markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
			markup.add(telebot.types.KeyboardButton('long'), 
					   telebot.types.KeyboardButton('short'))
			telegram_bot.send_message(message.chat.id, "Chose side:", reply_markup=markup)
	
	elif message.text == 'close trade':
		if trading_bot.opentrade:
			trading_bot.close()
		else:
			telegram_bot.send_message(message.chat.id, "Can't close trade")
	
	elif message.text == 'data':
		data = "Bot active: "+str(run)+"\nOpen trade: "+str(trading_bot.opentrade)+"\n-------------------------------------------\nBTCUSDT price: "+str(trading_bot.price)+"\nInterval: "+str(trading_bot.interval)+"\nEMA50: "+str(trading_bot.get_EMA()[0])+", "+str(trading_bot.get_trend()[0])+"\nEMA200: "+str(trading_bot.get_EMA()[1])+", "+str(trading_bot.get_trend()[1]+"\n-------------------------------------------\nProfit: "+str(trading_bot.get_profit()[0])+", "+str(round(trading_bot.get_profit()[1], 2))+"%")
		telegram_bot.send_message(message.chat.id, data)


@telegram_bot.message_handler(commands = ['start'])
def start(message):
	markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
	markup.add(telebot.types.KeyboardButton('start '), 
			   telebot.types.KeyboardButton('stop'),
			   telebot.types.KeyboardButton('open trade'),
			   telebot.types.KeyboardButton('close trade'),
			   telebot.types.KeyboardButton('data'))
	telegram_bot.send_message(message.chat.id, "Home:", reply_markup=markup)




if __name__ == "__main__":
	t.start()
	while True:
		trading_bot.refresh_data()

		if run:
			if last_date != trading_bot.date:
				print("Running")
				trend50EMA, trend200EMA = trading_bot.get_trend()[0], trading_bot.get_trend()[1]
				if trend50EMA == trend200EMA == 'BUY':
					if trading_bot.side == 'SELL':
						trading_bot.close()
					trading_bot.open('buy')
				if trend50EMA == trend200EMA == 'SELL':
					if 	trading_bot.side == 'BUY':
						trading_bot.close()
					trading_bot.open('sell')
			else:
				print("Same date!")


			last_date = trading_bot.date
		else:
			print("Not running")

		print(trading_bot.date)
		if 'm' in trading_bot.interval:
			time.sleep(int(re.findall(r'\d+',trading_bot.interval)[0])*60)
	