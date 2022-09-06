# region imports
from AlgorithmImports import *
# endregion

class Trades_Orders(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1) #Set the Start Date
        self.SetEndDate(2021, 1, 1)  # Set the End Date
        self.SetCash(100000)  # Set Strategy Cash

        ## Adding the QQQ equity(QQQ is the symbol for the NASDAQ 100 trust)
        self.qqq = self.AddEquity("QQQ", Resolution.Hour).Symbol

        self.entryTicket = None ## use for the marking the entry price of the ticket
        self.stopMarketTicket = None ## setting the price at which the trade will close

        ## setting the entry time of the order
        self.entryTime = datetime.min

        ## setting the exit time of the order
        self.stopMarketOrderFillTime = datetime.min

        ## keeping the track of the QQQ highest price
        self.highestPrice = 0 ## used for the trading stop loss

        

    def OnData(self, data):

        ## to check if 30days have passed after the last exit
        if(self.Time - self.stopMarketOrderFillTime).days <30:
            return

        price = self.Securities[self.qqq].Price

        ## send an entry limit order for as many shares of QQQ we can buy
        ## we will invest if our portifolio is not invested and there is no open orders for QQQ

        if not self.Portfolio.Invested and not self.Transactions.GetOpenOrders(self.qqq):
            quantity = self.CalculateOrderQuantity(self.qqq, 0.9)

            self.entryTicket = self.LimitOrder(self.qqq, quantity, price, "Entry Order")
            self.entryTime = self.Time

        ## moving the limit price if not filled after 1 day

        if (self.Time - self.entryTime).days > 1 and self.entryTicket.Status != OrderStatus.Filled:
            self.entryTime = self.Time ## making the entry time equal to current time
            updateFields = UpdateOrderFields()
            updateFields.LimitPrice = price
            self.entryTicket.Update(updateFields)

        ## move up the trailing stop price

        if self.stopMarketTicket is not None and self.Portfolio.Invested:
            if price > self.highestPrice:
                self.highestPrice = price
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = price * 0.95
                self.stopMarketTicket.Update(updateFields)


        pass

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status != OrderStatus.Filled:
            return

        ## send the stop loss order if every order is filled
        if self.entryTicket is not None and self.entryTicket.OrderId == orderEvent.OrderId:
            self.stopMarketTicket = self.StopMarketOrder(
                self.qqq, -self.entryTicket.Quantity, 0.95*self.entryTicket.AverageFillPrice)

        ## save fill time of stop loss order
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId:
            self.stopMarketOrderFillTime = self.Time
            self.highestPrice = 0

    
