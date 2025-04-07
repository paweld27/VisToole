#####################################################
#                                                   #
#   Shapes - AsTeR - tech@asterlab.pl               #
#   Paweł Dorobek                                   #
#                                                   #
#   ver. 0.900      - 01.2024                       #
#                                                   #
#   python     - 3.8.10                             #
#   matplotlib - 7.7.4                              #
#                                                   #
#####################################################

"""
Only individual 'get_position' and  'set_position' methods are added
tailored to the needs of the MoveXY class in the VisToole module.
If they are not to be moved, original patches can be used.
"""

from matplotlib.artist import Artist
import matplotlib.patches as patches
from matplotlib.transforms import Affine2D
import numpy as np


class PointPatch:

    def get_position(self):
        return self.center

    def set_position(self, xy):
        self.set_center(xy)

    def jump_to_data(self):
        w = self.get_width()
        h = self.get_height()
        x, y = self.get_position()
        xw, yh = self.axes.transLimits.inverted().transform((x+w, y+h))        
        x, y = self.axes.transLimits.inverted().transform((x, y))
        self.set_width(xw-x)
        self.set_height(yh-y)
        self.set_position((x, y))

    def jump_to_axes(self):
        w = self.get_width()
        h = self.get_height()
        x, y = self.get_position()
        xw, yh = self.axes.transLimits.transform((x+w, y+h))
        x, y = self.axes.transLimits.transform((x, y))
        self.set_width(xw-x)
        self.set_height(yh-y) 
        self.set_position((x, y))


class Annulus(patches.Annulus, PointPatch):
    def __init__(self, xy, r, width, angle=0, **kwargs):
        super().__init__(xy, r, width, angle=angle, **kwargs)

        self.jumper = True  # can jump between domains

    def jump_to_data(self):
        w = self.get_width()
        r1, r2 = self.get_radii()
        x, y = self.get_position()
        r1, r2 = self.axes.transLimits.inverted().transform((x+r1, y+r2))
        x, y = self.axes.transLimits.inverted().transform((x, y))
        r1 -= x
        r2 -= y
        self.set_radii((r1, r2))
        self.set_position((x, y))

    def jump_to_axes(self):
        w = self.get_width()
        r1, r2 = self.get_radii()
        x, y = self.get_position()
        r1, r2 = self.axes.transLimits.transform((x+r1, y+r2))
        x, y = self.axes.transLimits.transform((x, y))
        r1 -= x
        r2 -= y
        self.set_radii((r1, r2))
        self.set_position((x, y))
 

class Ellipse(patches.Ellipse, PointPatch):
    def __init__(self, xy, width, height, angle=0, **kwargs):
        super().__init__(xy, width, height, angle=angle, **kwargs)

        self.jumper = True  # can jump between domains


class Circle(patches.Circle, PointPatch):
    def __init__(self, xy, radius, **kwargs):
        super().__init__(xy, radius=radius, **kwargs)

        self.jumper = True  # can jump between domains


class Wedge(patches.Wedge, PointPatch):
    def __init__(self, center, r, theta1, theta2, *, width=None, **kwargs):
        super().__init__(center, r, theta1, theta2, width=width, **kwargs)

        self._angle = 0 # degree

    def set_angle(self, angle):

        self.set_theta1(self.theta1+angle-self._angle)
        self.set_theta2(self.theta2+angle-self._angle)
        
        self._angle = angle


    def get_angle(self):
        """Return the angle of the ellipse."""
        return self._angle

    angle = property(get_angle, set_angle)

        

class Rectangle(patches.Rectangle, PointPatch):
    def __init__(self, xy, width, height, angle=0, *,
                 rotation_point='xy', **kwargs):
        super().__init__(xy, width, height, angle,
                         rotation_point=rotation_point, **kwargs)

        self.jumper = True  # can jump between domains
    
    def get_position(self):
        return self.get_xy()
    
    def set_position(self, xy):
        self.set_xy(xy)

        
class Polygon(patches.Polygon):
    def __init__(self, xy, closed=True, angle=0, **kwargs):
        super().__init__(xy, closed=closed, **kwargs)

        self.jumper = True  # can jump between domains
        
        # dxy it's a numpy array of distances between
        # vertex_0 and every other vertex
        self.dxy = self.get_xy() - self.get_xy()[0]
        self._angle = 0
    
    def get_position(self):
        return self.get_xy()[0].tolist()
    
    def set_position(self, xy):
        self.set_xy(self.dxy + xy)

    def jump_to_data(self):
        xy = self.get_xy()
        for i in range(len(xy)):
            xy[i] = self.axes.transLimits.inverted().transform(xy[i])
        self.set_xy(xy)
        self.dxy = self.get_xy() - self.get_xy()[0]
    
    def jump_to_axes(self):
        xy = self.get_xy()
        for i in range(len(xy)):
            xy[i] = self.axes.transLimits.transform(xy[i])
        self.set_xy(xy)
        self.dxy = self.get_xy() - self.get_xy()[0]

    def set_angle(self, angle):

        p0 = self.get_position()
        self.set_xy(Affine2D().rotate_deg(angle-self._angle) \
                              .transform(self.dxy) + p0)
        
        self.dxy = self.get_xy() - self.get_xy()[0]
        self._angle = angle


    def get_angle(self):
        """Return the angle of the ellipse."""
        return self._angle

    angle = property(get_angle, set_angle)


    
class FancyArrow(patches.FancyArrow, Polygon):
    
    def __init__(self, x, y, dx, dy, width=0.001, grab='middle', **kwargs):
        super().__init__(x, y, dx, dy, width=width, length_includes_head=True,
                         head_length=3*width,
                         **kwargs)

        self.jumper = True  # can jump between domains
        if grab not in ['head', 'middle', 'tail']:
            grab = 'middle'
        self.grab = grab
        
        
    def set_grab(self, xy):   # dist = pik - first_grab
        dist_head = np.hypot(self.get_xy()[0][0]-xy[0], self.get_xy()[0][1]-xy[1])
        dist_tail = np.hypot(self._x-xy[0], self._y-xy[1])
        head_tail = np.hypot(self._dx, self._dy)
        self.grab = 'middle'
        if head_tail > 0.0:
            to_head = dist_head / head_tail
            to_tail = dist_tail / head_tail
            if to_head < 0.3:
                self.grab = 'head'
            elif to_tail < 0.3:
                self.grab = 'tail'

        self._make_verts()
        self.set_xy(self.verts)
        self.dxy = self.get_xy() - self.get_xy()[0]


    def get_position(self):

        if self.grab == 'tail':
            return [self._x, self._y]
        else:    
            return self.get_xy()[0].tolist()
        
    def set_position(self, xy):

        if self.grab == 'tail':
            self._x = xy[0]
            self._y = xy[1]
            self._dx = self.get_xy()[0][0] - self._x
            self._dy = self.get_xy()[0][1] - self._y
            
            self._make_verts()
            self.set_xy(self.verts)
            self.dxy = self.get_xy() - self.get_xy()[0]

        elif self.grab == 'middle':
            self.set_xy(self.dxy + xy)
            # begin coords
            self._x = self.get_xy()[0][0] - self._dx
            self._y = self.get_xy()[0][1] - self._dy

        elif self.grab == 'head':
            self._dx = xy[0] - self._x
            self._dy = xy[1] - self._y
            
            self._make_verts()
            self.set_xy(self.verts)
            self.dxy = self.get_xy() - self.get_xy()[0]

    def _update_param(self):
        xy = self.get_xy()
        self._width = np.hypot(xy[3][0]-xy[4][0], xy[3][1]-xy[4][1])      # stsrt
        self._head_width = np.hypot(xy[1][0]-xy[6][0], xy[1][1]-xy[6][1])
        
        x0 = (xy[1][0]+xy[6][0])/2.0
        y0 = (xy[1][1]+xy[6][1])/2.0
        self._head_length = np.hypot(xy[0][0]-x0, xy[0][1]-y0)

        self._dx = self.get_xy()[0][0] - self._x
        self._dy = self.get_xy()[0][1] - self._y
        self._make_verts()
        
     
    def jump_to_data(self):
        super().jump_to_data()
        self._x, self._y = self.axes.transLimits.inverted().transform([self._x, self._y])
        self._update_param()
       
    def jump_to_axes(self):
        super().jump_to_axes()
        self._x, self._y = self.axes.transLimits.transform([self._x, self._y])
        self._update_param()



        
