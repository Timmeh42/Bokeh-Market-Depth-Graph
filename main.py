import sys, math, json, time, threading, websocket, datetime
import numpy as np
from functools import partial
from bokeh.io import curdoc, show
from bokeh.layouts import column, row
from bokeh.models import Button, ColumnDataSource, Slider, BasicTickFormatter, BasicTicker
#from bokeh.models.glyphs import Ray
from bokeh.models.widgets import Panel, Tabs

from bokeh.plotting.figure import Figure
from bokeh.plotting import figure
from DepthGraph import DepthGraph
from bokeh.plotting.helpers import _glyph_function
Figure.depth = _glyph_function(DepthGraph)

class Trade_pair():
	def __init__(self, base, quote):
		self.pair_string = base+"_"+quote
		self.base = base
		self.quote = quote

		self.sells = []
		self.buys = []

		self.update_buffer = []
		self.prev_update = 0

		self.status = "OFF"
		self.connect_ws()

		self.xrange_perc = 0.5

		self.range_slider = Slider(start=0.01, end=1, value=0.5, step=0.01, title='X-range percentage')
		self.range_slider.on_change('value', self.slider_callback)
		self.my_col = column(self.range_slider)
		self.my_tab = Panel(child=self.my_col, title=self.pair_string)
		current_doc.add_next_tick_callback(partial(call_tab_append, parent=main_tabs, child=self.my_tab))

	def slider_callback(self, attr, old, new):
		self.xrange_perc = new
		current_doc.add_next_tick_callback(partial(call_update_cds, cds=self.buys_cds, data=steppify(self.buys, self.xrange_perc)))
		current_doc.add_next_tick_callback(partial(call_update_cds, cds=self.sells_cds, data=steppify(self.sells, self.xrange_perc)))


	def connect_ws(self):
		self.status = "ON"
		self.ws = websocket.WebSocketApp("wss://api2.poloniex.com",
			on_message = self.ws_receive,
			on_error = self.ws_error,
			on_close = self.ws_close,
			on_open = self.ws_open)
		self.ws_thread = threading.Thread(target=self.ws.run_forever)
		self.ws_thread.start()

	def ws_receive(self, ws, message):
		self.log('update')
		parsed = json.loads(message)
		if (parsed[0] == 1010):
			return False					# detect heartbeat
		if (self.prev_update == 0):
			self.prev_update = parsed[1]-1
		self.update_buffer.append(parsed)
		self.update_buffer.sort(key = lambda x: x[1])
		while (len(self.update_buffer) != 0 and self.update_buffer[0][1] == self.prev_update+1):
			self.prev_update = self.update_buffer[0][1]
			new_data = self.update_buffer.pop(0)[2]
			if (new_data[0][0] == "i"):
				self.init_orders(new_data[0])
			else:
				self.update_orders(new_data)

	def ws_error(self, ws, error):
		self.log(error)

	def ws_close(self, ws):
		self.log("Websocket closed")
		if (self.status != "OFF"):
			self.connect_ws()

	def ws_open(self, ws):
		while not ws.sock.connected:
			sleep(2)
		ws.send('{"command":"subscribe","channel":"'+self.pair_string+'"}')
		self.log("Subscribed to websocket")
		self.prev_update = 0

	def log(self, msg):
		log_str = ""
		log_str += datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | "
		log_str += self.pair_string + " | "
		log_str += str(msg)
		print(log_str, flush=True)

	def find_sell_price(self, price):
		index = -1
		for i in range(len(self.sells)):
			if (self.sells[i][0] == price):
				index = i
				break
		return index

	def find_buy_price(self, price):
		index = -1
		for i in range(len(self.buys)):
			if (self.buys[i][0] == price):
				index = i
				break
		return index

	def find_sell_depth(self, depth):
		index = -1
		total_depth = 0
		for i in range(len(self.sells)):
			total_depth += self.sells[i][1]*self.sells[i][0]
			if (total_depth >= depth):
				index = i
				break
		return index

	def find_buy_depth(self, depth):
		index = -1
		total_depth = 0
		for i in range(len(self.buys)):
			total_depth += self.buys[i][1]*self.buys[i][0]
			if (total_depth >= depth):
				index = i
				break
		return index

	def set_sell(self, price, volume):
		index = self.find_sell_price(price)
		if (index == -1):
			self.sells.append([price, volume])
		else:
			self.sells[index] = [price, volume]
			if (volume == 0):
				self.sells.pop(index)

	def set_buy(self, price, volume):
		index = self.find_buy_price(price)
		if (index == -1):
			self.buys.append([price, volume])
		else:
			self.buys[index] = [price, volume]
			if (volume == 0):
				self.buys.pop(index)

	def init_orders(self, data):
		self.sells = []
		self.buys = []
		for rawprice in data[1]["orderBook"][0]:	# sells
			price = float(rawprice)
			vol = float(data[1]["orderBook"][0][rawprice])
			self.set_sell(price, vol)
		for rawprice in data[1]["orderBook"][1]:	# buys
			price = float(rawprice)
			vol = float(data[1]["orderBook"][1][rawprice])
			self.set_buy(price, vol)
		self.sells.sort(key=lambda x: x[0])
		self.buys.sort(key=lambda x: x[0], reverse=True)

		self.buys_cds = ColumnDataSource(data=steppify(self.buys, self.xrange_perc))
		self.sells_cds = ColumnDataSource(data=steppify(self.sells, self.xrange_perc))

		self.price_markers = ColumnDataSource(data=dict(price=[], length=[]))

		current_doc.add_next_tick_callback(partial(call_update_cds, cds=self.buys_cds, data=steppify(self.buys, self.xrange_perc)))
		current_doc.add_next_tick_callback(partial(call_update_cds, cds=self.sells_cds, data=steppify(self.sells, self.xrange_perc)))

		self.my_plot = plot_market_depth(self.buys_cds, self.sells_cds, self.base, self.quote)
		self.my_plot.ray(x='price', y=-10, length=0.01, angle=1.5708, source=self.price_markers, line_color='black')

		current_doc.add_next_tick_callback(partial(call_doc_append, parent=self.my_col, child=self.my_plot))

	def update_orders(self, data):
		event = {"type":"none", "min_price":math.inf, "max_price":-math.inf, "base_vol":0, "quote_vol":0, "steps":0}
		for order in data:
			if (order[0] == "o"):
				price = float(order[2])
				vol = float(order[3])
				if (order[1] == 1):
					self.set_buy(price, vol)
				elif (order[1] == 0):
					self.set_sell(price, vol)
			elif (order[0] == "t"):
				event["steps"] += 1
				event["min_price"] = min(event["min_price"], float(order[3]))
				event["max_price"] = max(event["max_price"], float(order[3]))
				event["quote_vol"] += float(order[4])
				event["base_vol"] += float(order[4])*float(order[3])
				event["type"] = order[2]
				# Format of poloniex trade updates is as follows
				# ["t","11450176",0,"0.00006090","0.47294136",1501361564]
				# trade tradeid  buy quoteprice    quotevol   timestamp
		self.sells.sort(key=lambda x: x[0])
		self.buys.sort(key=lambda x: x[0], reverse=True)
		current_doc.add_next_tick_callback(partial(call_update_cds, cds=self.buys_cds, data=steppify(self.buys, self.xrange_perc)))
		current_doc.add_next_tick_callback(partial(call_update_cds, cds=self.sells_cds, data=steppify(self.sells, self.xrange_perc)))
		
		markp = []			# list of prices to mark
		markl = []			# list of marker lengths. necessary for bokeh's method of drawing.
		markp.append(self.buys[self.find_buy_depth(1)][0])		# mark the 1btc depth on the buy side
		markl.append(-1)
		markp.append(self.sells[self.find_sell_depth(1)][0])	# mark the 1btc depth on the sell side
		markl.append(-1)

		current_doc.add_next_tick_callback(partial(call_update_cds, cds=self.price_markers, data=dict(price=markp, length=markl)))

def call_doc_append(parent, child):
	parent.children.append(child)

def call_tab_append(parent, child):
	parent.tabs.append(child)

def call_update_cds(cds, data):
	cds.data = data

def plot_market_depth(buys, sells, pair_base, pair_quote):
	'''
	Expects buys and sells as ordered columndatasources
	Both lists start at the midpoint and extend towards 0 and infinity respectively
	'''
	minx = buys.data['prices'][0] * 0.98		#default xrange is 2% either side of buy/sell gap
	maxx = sells.data['prices'][0] * 1.02
	plot = figure(lod_threshold=None, x_range=(minx, maxx), plot_width=1600)
	plot.axis.formatter = BasicTickFormatter(use_scientific = False)
	plot.xaxis.axis_label = pair_base
	plot.xaxis.ticker = BasicTicker(desired_num_ticks=11)
	plot.depth('prices', 'amounts', source=buys, fill_color='#00a000', line_alpha=0)
	plot.depth('prices', 'amounts', source=sells, fill_color='#a00000', line_alpha=0)
	return plot

def close_button_click():
	for trade_pair in trade_pairs:
		trade_pair.status = "OFF"
		trade_pair.ws.close()

def steppify(data, price_range=0.5):
	'''
	Takes all buy or sell orders and cumulatively sums them to produce the stepped data needed for the graph.
	'''
	prices, amounts = zip(*data)
	range_min_price, range_max_price = prices[0]*(1-price_range), prices[0]*(1+price_range)
	prices = [n for n in prices if (n < range_max_price and n > range_min_price)]
	amounts = [prices[n]*amounts[n] for n in range(len(prices))]		# convert into base currency
	amounts_cumlulated = [sum(amounts[:n+1]) for n in range(len(amounts))]
	return dict(prices=prices, amounts=amounts_cumlulated)

current_doc = curdoc()
close_button = Button(label='Close websocket')
close_button.on_click(close_button_click)
main_tabs = Tabs()
current_doc.add_root(close_button)
current_doc.add_root(main_tabs)
starttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
trade_pairs = []
trade_pairs.append(Trade_pair("BTC", "STR"))
#trade_pairs.append(Trade_pair("BTC", "BTS"))