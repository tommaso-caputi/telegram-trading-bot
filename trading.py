import tradingview_ta
import mysql.connector


class trading_bot:
    def __init__(self, interval):
        self.interval = interval
        self.date = None
        self.EMA50Value = None
        self.EMA200Value = None
        self.price = None
        self.handler = tradingview_ta.TA_Handler(
            symbol="BTCUSDT",
            exchange="BYBIT",
            screener="crypto",
            interval=str(interval),
            timeout=None
        )
        self.analysis = None
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="tradingdb"
        )
        self.dbcursor = self.mydb.cursor()
        self.dbcursor.execute("SELECT * FROM trades ORDER BY ID DESC LIMIT 1")
        try:
            last_row = self.dbcursor.fetchall()[0]
            if last_row[5] == '':
                self.opentrade = True
            else:
                self.opentrade = False
        except:
            self.opentrade = False
        self.side = None


    def refresh_data(self):
        self.analysis = self.handler.get_analysis()
        self.EMA50Value = int(float(self.analysis.indicators['EMA50']))
        self.EMA200Value = int(float(self.analysis.indicators['EMA200']))
        self.date = str(self.analysis.time)[:16]
        self.price = int(float(self.analysis.indicators['open']))

    def get_EMA(self):
        return self.EMA50Value, self.EMA200Value, self.date
    
    def get_trend(self):
        return self.analysis.moving_averages['COMPUTE']['EMA50'], self.analysis.moving_averages['COMPUTE']['EMA200']

    def open(self, side):
        if not self.opentrade:
            self.side = side
            self.opentrade = True
            if side == 'buy':
                pass# add exchange actions
            else:
                pass# add exchange actions
            self.dbcursor.execute("SELECT count(*) FROM trades;")
            self.dbcursor.execute("INSERT INTO trades (id, symbol, side, opendate, openprice) VALUES (%s, %s, %s, %s, %s)"
                                    , [(str(int(self.dbcursor.fetchall()[0][0])+1)),("BTCUSDT"),(str(side)),(str(self.date)),(self.price)])
            self.mydb.commit()

    def close(self):
        if self.opentrade:
            self.opentrade = False
            self.dbcursor.execute("UPDATE trades SET closedate=%s, closeprice=%s WHERE iD=(SELECT MAX(iD) FROM trades)", [(str(self.date)),(self.price)])
            self.mydb.commit()
            self.dbcursor.execute("SELECT * FROM trades ORDER BY ID DESC LIMIT 1")
            last_row = self.dbcursor.fetchall()[0]
            profit = int(last_row[4]) - int(last_row[6])
            profitperc = profit / self.price * 100 
            if last_row[2] == 'buy':
                profit = -profit
                profitperc = -profitperc
            self.dbcursor.execute("UPDATE trades SET profit=%s, profitperc=%s WHERE iD=(SELECT MAX(iD) FROM trades)", [(str(profit)),(str(profitperc)+'%')])
            self.mydb.commit()

    def data(self):
        self.dbcursor.execute("SELECT * FROM trades")
        return self.dbcursor.fetchall()[-1]

    def get_profit(self):
        self.dbcursor.execute("SELECT SUM(profit), SUM(profitperc) FROM trades")
        p = self.dbcursor.fetchall()
        return p[0][0], p[0][1]

