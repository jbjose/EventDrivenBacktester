import Queue
import datetime
import os

from edbacktester.data import HistoricCSVDataHandler
from edbacktester.execution import SimulatedExecutionHandler
from edbacktester.portfolio import NaivePortfolio
from edbacktester.strategy import BuyAndHoldStrategy

events = Queue.Queue()
start_date = datetime.datetime(2016, 1, 5, 0, 0)
# config = ConfigParser.ConfigParser()
# config.read(os.path.join(os.path.dirname(__file__), 'config.cfg'))
csv_dir = os.path.join(os.path.dirname(__file__), 'data')
symbol_list = ['AAPL', 'GOOG']

bars = HistoricCSVDataHandler(events, csv_dir, symbol_list)  # DataHandler(..)
strategy = BuyAndHoldStrategy(bars, events)  # Strategy(..)
port = NaivePortfolio(bars, events, start_date, initial_capital=100000.0)  # Portfolio(..)
broker = SimulatedExecutionHandler(events)  # (..)

while True:
    # Update the bars (specific backtest code, as opposed to live trading)
    if bars.continue_backtest:
        bars.update_bars()
    else:
        break

    # Handle the events
    while True:
        try:
            event = events.get(False)
        except Queue.Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    port.update_fill(event)

print port
    # 10-Minute heartbeat
    # time.sleep(10*60)