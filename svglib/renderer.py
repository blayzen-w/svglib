import sys

import uuid
from reportlab.graphics.renderPDF import _PDFRenderer, rl_config, STATE_DEFAULTS
from reportlab.graphics.renderbase import renderScaledDrawing, StateTracker
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame


def draw(drawing, canvas, x, y, showBoundary=rl_config._unset_):
    """As it says"""
    R = IllustratorRenderer(drawing=drawing)
    R.draw(renderScaledDrawing(drawing), canvas, x, y, showBoundary=showBoundary)


def drawToFile(d, fn, msg="", showBoundary=rl_config._unset_, autoSize=1, canvasKwds={}):
    """Makes a one-page PDF with just the drawing.

    If autoSize=1, the PDF will be the same size as
    the drawing; if 0, it will place the drawing on
    an A4 page with a title above it - possibly overflowing
    if too big."""
    d = renderScaledDrawing(d)
    for x in ('Name','Size'):
        a = 'initialFont'+x
        canvasKwds[a] = getattr(d,a,canvasKwds.pop(a,STATE_DEFAULTS['font'+x]))
    c = Canvas(fn,**canvasKwds)
    if msg:
        c.setFont(rl_config.defaultGraphicsFontName, 36)
        c.drawString(80, 750, msg)
    c.setTitle(msg)

    if autoSize:
        c.setPageSize((d.width, d.height))
        draw(d, c, 0, 0, showBoundary=showBoundary)
    else:
        #show with a title
        c.setFont(rl_config.defaultGraphicsFontName, 12)
        y = 740
        i = 1
        y = y - d.height
        draw(d, c, 80, y, showBoundary=showBoundary)

    c.showPage()
    c.save()
    if sys.platform=='mac' and not hasattr(fn, "write"):
        try:
            import macfs, macostools
            macfs.FSSpec(fn).SetCreatorType("CARO", "PDF ")
            macostools.touched(fn)
        except:
            pass


class IllustratorRenderer(_PDFRenderer):
    def __init__(self, drawing, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drawing = drawing

    def drawGroup(self, group):
        from svglib.document import Layer
        if isinstance(group, Layer):
            canvas = getattr(self, '_canvas', None)
            elements = []
            for node in group.getContents():
                elements.append(node)

            frame = Frame(0, 0, self._drawing.width, self._drawing.height, id=str(uuid.uuid4()))
            frame.id = 'TestLayer'
            frame.addFromList(elements, canvas)
        else:
            return super().drawGroup(group)

    def draw(self, drawing, canvas, x=0, y=0, showBoundary=rl_config._unset_):
        """This is the top level function, which draws the drawing at the given
        location. The recursive part is handled by drawNode."""
        self._tracker = StateTracker(defaultObj=drawing)
        #stash references for ease of  communication
        if showBoundary is rl_config._unset_: showBoundary=rl_config.showBoundary
        self._canvas = canvas
        canvas.__dict__['_drawing'] = self._drawing = drawing
        drawing._parent = None
        try:
            #bounding box
            if showBoundary: canvas.rect(x, y, drawing.width, drawing.height)
            canvas.saveState()
            self.initState(x,y)  #this is the push()
            self.drawNode(drawing)
            self.pop()
            canvas.restoreState()
        finally:
            #remove any circular references
            try:
                del self._canvas, self._drawing, canvas._drawing, drawing._parent, self._tracker
            except:
                pass
