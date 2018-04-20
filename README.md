# Bokeh-Market-Depth-Graph
Using Python and Bokeh to live plot a cryptocurrency market depth graph from the Poloniex exchange.

Demonstrates:

• Opening a websocket to the Poloniex API and interpretting JSON data feed

• Running a Bokeh server connection to live update a plot in a browser window

• Custom Bokeh glyph code to draw a stepped market depth graph

Warning: possible lag on Firefox due to Bokeh issue

Run using:
`bokeh serve --show bokeh-market-depth-graph`
