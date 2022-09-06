from AlgorithmImports import *
## making a trading bot that trades SPY i.e buy and sell Spy before it drops or rises a certain amount. 

## making a class for the quant algorithm
class Predictions(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1) # Set Start Date
        self.SetEndDate(2021, 1, 1) # Set End Date
        self.SetCash(100000)  # ## set the cash amount on which it has to be traded
        
        ##set the type of trading we want to do
        spy = self.AddEquity("SPY", Resolution.Daily)
        
        ## setting the normalization mode
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
        self.spy = spy.Symbol
        
        ## Setting the benchmark
        self.SetBenchmark("SPY")

        ## Setting the brokerage model
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        
        ## Setting the entry price
        self.entryPrice = 0

        ## Setting the period for 31days
        self.period = timedelta(31)

        ## Setting the time when we should start investing and since we are investing right now we are making it equal to self.time
        self.nextEntryTime = self.Time


    def OnData(self, data):

        ## to check if the requested data already exits
        if not self.spy in data:
            return
        
        ## taking the closing price of the SPY
        price = data[self.spy].Close

        ## other methods of taking the close price of spy data are
        ##price = data.Bars[self.spy].Close
        ## price = self.Securities[self.spy].Close

        ## to check if the bot is already invested
        
        if not self.Portfolio.Invested:

            ## we will hold the cash for one month and thene we will buy and sell again
            if self.nextEntryTime <= self.Time:

                ## to manually calculate the order size
                self.SetHoldings(self.spy, 1)

                # self.MarketOrder(self.spy, int(self.Portfolio.Cash / price) )
                
                ## logging the SPY
                self.Log("BUY SPY @" + str(price))
                
                self.entryPrice = price
        
        ## implementing the exit process

        elif self.entryPrice * 1.1 < price or self.entryPrice * 0.90 > price:

            self.Liquidate() ## liquidate all the positions in the portfolios

            self.Log("SELL SPY @" + str(price))

            ## for next 30days we will stay in cash
            self.nextEntryTime = self.Time + self.period