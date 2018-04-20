from bokeh.core.properties import Include, NumberSpec
from bokeh.core.property_mixins import ScalarFillProps, ScalarLineProps
from bokeh.models.glyphs import XYGlyph

class DepthGraph(XYGlyph):
	''' Render a single patch.
	The ``Patch`` glyph is different from most other glyphs in that the vector
	of values only produces one glyph on the Plot.
	'''

	__implementation__ = "DepthGraph.ts"

	# a canonical order for positional args that can be used for any
	# functions derived from this class
	_args = ('x', 'y')

	x = NumberSpec(help="""
	The x-coordinates for the points of the patch.
	.. note::
		A patch may comprise multiple polygons. In this case the
		x-coordinates for each polygon should be separated by NaN
		values in the sequence.
	""")

	y = NumberSpec(help="""
	The y-coordinates for the points of the patch.
	.. note::
		A patch may comprise multiple polygons. In this case the
		y-coordinates for each polygon should be separated by NaN
		values in the sequence.
	""")

	line_props = Include(ScalarLineProps, use_prefix=False, help="""
	The %s values for the patch.
	""")

	fill_props = Include(ScalarFillProps, use_prefix=False, help="""
	The %s values for the patch.
	""")