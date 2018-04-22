# Bokeh-Market-Depth-Graph
Using Python and Bokeh to live plot a cryptocurrency market depth graph from the Poloniex exchange.
The 1btc depth on the each side is marked by lines.
The slider at the top changes how much of the data market depth is shown in the plot - lower means less data to update.
Multiple tabs of different currency pairs can be added and switched between.

Demonstrates:

• Opening a websocket to the Poloniex API and interpretting JSON data feed

• Running a Bokeh server connection to live update a plot in a browser window

• Custom Bokeh glyph code to draw a stepped market depth graph

Warning: possible lag on Firefox due to Bokeh issue

Run using:
`bokeh serve --show .\bokeh-market-depth-graph\`

When closing, first press the 'Close Websocket' button on the viewing page, the close the page.
