import sys

import os
from reportlab import rl_config

from reportlab.graphics.shapes import Drawing, _extraKW

from svglib.renderer import drawToFile


class IllustratorDrawing(Drawing):
    def save(self, verbose=None, fnRoot=None, outDir=None, title='', **kw):
        if not outDir: outDir = '.'
        fnroot = os.path.normpath(os.path.join(outDir, fnRoot))

        if fnroot.endswith('.pdf'):
            filename = fnroot
        else:
            filename = fnroot + '.pdf'

        drawToFile(self, filename, title,
                             showBoundary=getattr(self, 'showBorder', rl_config.showBoundary),
                             **_extraKW(self, '_renderPDF_', **kw))

        if sys.platform == 'mac':
            import macfs, macostools
            macfs.FSSpec(filename).SetCreatorType("CARO", "PDF ")
            macostools.touched(filename)

    def resized(self,kind='fit',lpad=0,rpad=0,bpad=0,tpad=0):
        '''return a base class drawing which ensures all the contents fits'''
        C = self.getContents()
        oW = self.width
        oH = self.height
        drawing = IllustratorDrawing(oW,oH,*C)
        xL,yL,xH,yH = drawing.getBounds()
        if kind=='fit' or (kind=='expand' and (xL<lpad or xH>oW-rpad or yL<bpad or yH>oH-tpad)):
            drawing.width = xH-xL+lpad+rpad
            drawing.height = yH-yL+tpad+bpad
            drawing.transform = (1,0,0,1,lpad-xL,bpad-yL)
        elif kind=='fitx' or (kind=='expandx' and (xL<lpad or xH>oW-rpad)):
            drawing.width = xH-xL+lpad+rpad
            drawing.transform = (1,0,0,1,lpad-xL,0)
        elif kind=='fity' or (kind=='expandy' and (yL<bpad or yH>oH-tpad)):
            drawing.height = yH-yL+tpad+bpad
            drawing.transform = (1,0,0,1,0,bpad-yL)
        return drawing


class Layer(Drawing):
    pass
