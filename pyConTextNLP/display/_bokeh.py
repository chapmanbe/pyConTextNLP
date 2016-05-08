"""This module provides pyConText visualizaiton tools using Bokeh"""

from bokeh.plotting import ColumnDataSource
import bokeh.plotting as bp
from bokeh.models import HoverTool
from collections import OrderedDict
import networkx as nx

def graph2DataSource(g):

    tmp = [(n.getSpan(),
            n.getCategory(),
            n.getPhrase(),
            n.getTagID(),
            n.getLiteral(),
            n.getScope()) for n in g.nodes()]
    span, category, text, ids, literals, scopes = zip(*tmp)

    return ColumnDataSource(data=dict(text=text,
                                      literal=literals,
                                      id=ids,
                                      span=span,
                                      scope=scopes,
                                      category=category))


def graphDocumentBokeh(g, width=600, height=300, title=""):
    """
    Returns a bokeh plotting figure of the pyConTextNLP graph g
    """
    colors = {'target':'blue', 'modifier':'red'}
    TOOLS = "pan, box_zoom, reset, hover, previewsave"

    try:
        pos = nx.graphviz_layout(g)
    except:
        pos = nx.spring_layout(g)
    try:
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        delta = 75
        minx, maxx = int(min(xs)-delta), int(max(xs)+delta)
        miny, maxy = int(min(ys)-delta), int(max(ys)+delta)
        radius = 0.1*(maxx-maxy)
        p = bp.figure(plot_width=width, plot_height=height, title="",
                      x_axis_type=None, y_axis_type=None,
                      x_range=[minx, maxx],
                      y_range=[miny, maxy],
                      min_border=0, outline_line_color=None,
                      tools=TOOLS)
        xpos = [pos[n][0] for n in g.nodes()]
        ypos = [pos[n][1] for n in g.nodes()]
        tcolors = [colors[g.node[n]['category']] for n in g.nodes()]
        text = [n.getPhrase() for n in g.nodes()]
        source = graph2DataSource(g)
        for e in g.edges():
            p.line([pos[e[0]][0], pos[e[1]][0]],
                   [pos[e[0]][1], pos[e[1]][1]],
                   line_cap="round",
                   line_width=3,
                   line_alpha=0.4)
            p.diamond([pos[e[1]][0]], [pos[e[1]][1]],
                       alpha=0.4, size=[10])
        p.text(xpos, ypos,
               text=text, text_color=tcolors,
               angle=0, text_font_size="12pt",
               text_align='center', text_baseline='middle')
        p.circle(xpos, ypos,
                 radius=radius, source=source,
                 fill_color=None, fill_alpha=0.1, line_color=None)
        hover = p.select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("index", "$index"),
            ("id", "@id"),
            ("phrase", "@text"),
            ("literal", "@literal"),
            ("span", "@span"),
            ("scope", "@scope"),
            ("category", "@category"),
            ])
        bp.show(p)
    except Exception as error:
        print(error, ": Cannot render graph with %d nodes and %d edges"%
              (g.number_of_nodes(), g.number_of_edges()))
