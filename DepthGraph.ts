// Replace all instances of DepthGraph and DepthGraphView with glyph name if u copy this
// Timothy Meier modified this from the patch.ts file

import {XYGlyph, XYGlyphView} from "models/glyphs/xy_glyph"
import {LineMixinVector, FillMixinVector} from "core/property_mixins"
import {Context2d} from "core/util/canvas"

export class DepthGraphView extends XYGlyphView {
  model: DepthGraph

  _render(ctx: Context2d, indices, {sx, sy}) {
    var maxi = indices.length-1
    var sy0 = 0
    if (this._y[0] != 0 && this._y[1] != 0) {
      sy0 = sy[1]-(sy[0]-sy[1])*(this._y[1]/(this._y[0]-this._y[1]))
    }
    var endx = 0
    if (this._x[0] < this._x[1]) {
      endx = ctx.canvas.width
    }
    if (this.visuals.fill.doit) {
      this.visuals.fill.set_value(ctx);
      for (const i of indices) {
        if (i === 0) {
          ctx.beginPath();
          ctx.moveTo(sx[i], sy[i]);
          if (i != maxi){
            ctx.lineTo(sx[i+1], sy[i]);
          }
          continue;
        } else if (isNaN(sx[i] + sy[i])) {
          ctx.closePath();
          ctx.fill();
          ctx.beginPath();
          continue;
        } else {
          ctx.lineTo(sx[i], sy[i]);
          if (i != maxi){
            ctx.lineTo(sx[i+1], sy[i]);
          } else {
            ctx.lineTo(endx, sy[i]);
          }
        }
      }
      ctx.lineTo(endx, sy0);
      ctx.lineTo(sx[0], sy0);
      ctx.lineTo(sx[0], sy[0]);
      ctx.closePath();
      ctx.fill();
    }

    if (this.visuals.line.doit) {
      this.visuals.line.set_value(ctx);
      for (const i of indices) {
        if (i === 0) {
          ctx.beginPath();
          ctx.moveTo(sx[i], sy[i]);
          if (i != maxi){
            ctx.lineTo(sx[i+1], sy[i]);
          }
          continue;
        } else if (isNaN(sx[i] + sy[i])) {
          ctx.closePath();
          ctx.stroke();
          ctx.beginPath();
          continue;
        } else {
          ctx.lineTo(sx[i], sy[i]);
          if (i != maxi){
            ctx.lineTo(sx[i+1], sy[i]);
          } else {
            ctx.lineTo(endx, sy[i]);
          }
        }
      }
      ctx.lineTo(endx, sy0);
      ctx.lineTo(sx[0], sy0);
      ctx.lineTo(sx[0], sy[0]);

      ctx.closePath();
      return ctx.stroke();
    }
  }

  draw_legend_for_index(ctx: Context2d, x0, x1, y0, y1, index) {
    return this._generic_area_legend(ctx, x0, x1, y0, y1, index);
  }
}

export namespace DepthGraph {
  export interface Mixins extends LineMixinVector, FillMixinVector {}

  export interface Attrs extends XYGlyph.Attrs, Mixins {}

  export interface Opts extends XYGlyph.Opts {}
}

export interface DepthGraph extends DepthGraph.Attrs {}

export class DepthGraph extends XYGlyph {

  constructor(attrs?: Partial<DepthGraph.Attrs>, opts?: DepthGraph.Opts) {
    super(attrs, opts)
  }

  static initClass() {
    this.prototype.type = 'DepthGraph';
    this.prototype.default_view = DepthGraphView;

    this.mixins(['line', 'fill']);
  }
}
DepthGraph.initClass();