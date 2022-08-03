Algorithmic Trading bot
=
Among all my projects, I am proud of this one, just because it was the most challenging for me. It is an algorithmic trading bot, which implements a very simple strategy and trades cryptocurrencies in time frame of 1 minute. But its abilities are not just limited to crypto and 1m timeframe, it can be modified to trade other commodities as well as other timeframes. 
I use Alpaca API, which provides great features for developers, such as live and historical data of the markets, as well as submitting orders. In addition to this, they provide a paper-trading account, which is a demo account where developers can test their strategies on real-time data.
The bot needs real-time data on the market and I used Websockets to stream live market data. Data is streamed and saved into a Pandas data frame using a thread, and then is analyzed using another thread. 
The strategy uses a pair of simple moving averages (SMA) to recognize buy and sell signals. 
When starting the bot, you can specify a look back time, say 12 hours; Every 12 hours, the bot will analyze the previous 12 hours, and out of all the possible SMA pairs, it will find the most profitable one and will use that pair for the next 12 hours.

<img width="1091" alt="Screen Shot 2022-08-04 at 12 36 09 AM" src="https://user-images.githubusercontent.com/54746341/182724653-40d7b89f-d35b-4a03-af71-3f1fd91f3851.png">
<img width="1187" alt="Screen Shot 2022-08-04 at 12 39 45 AM" src="https://user-images.githubusercontent.com/54746341/182724661-f619823e-6c56-4597-a49f-bcbba6e65ac6.png">
