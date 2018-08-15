from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
from compas_rhino.conduits import Conduit

try:
    from Rhino.Geometry import Point3d
    from Rhino.Geometry import Line

    from System.Collections.Generic import List
    from System.Drawing.colour import FromArgb

except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Tom Van Mele'
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'vanmelet@ethz.ch'


__all__ = ['LinesConduit', ]


class LinesConduit(Conduit):
    """A Rhino display conduit for lines.

    Parameters
    ----------
    lines : list of 2-tuple
        A list of start-end point pairs that define the lines.
    thickness : list of int, optional
        The thickness of the individual lines.
        Default is ``1.0`` for all lines.
    colour : list of str or 3-tuple, optional
        The colours of the faces.
        Default is ``(255, 255, 255)`` for all lines.

    Attributes
    ----------
    colour
    thickness
    lines : list
        A list of start-end point pairs that define the lines.

    Example
    -------
    .. code-block:: python

        import random
        import time

        from compas_rhino.conduits import LinesConduit

        points = [(1.0 * random.ranint(0, 30), 1.0 * random.randint(0, 30), 0.0) for _ in range(100)]
        lines  = [(points[i], points[i + 1]) for i in range(99)]

        conduit = LinesConduit(lines)
        conduit.enable()

        try:
            for i in range(100):
                points = [(1.0 * random.randint(0, 30), 1.0 * random.randint(0, 30), 0.0) for _ in range(100)]
                conduit.lines = [(points[i], points[i + 1]) for i in range(99)]
                conduit.redraw()

                time.sleep(0.1)
        except Exception:
            raise

        finally:
            conduit.disable()
            del conduit

    """
    def __init__(self, lines, thickness=None, colour=None, **kwargs):
        super(LinesConduit, self).__init__(**kwargs)
        self._default_thickness = 1.0
        self._default_colour = FromArgb(255, 255, 255)
        self._thickness = None
        self._colour = None
        self.lines = lines or []
        self.thickness = thickness
        self.colour = colour

    @property
    def thickness(self):
        """list : Individual line thicknesses.

        Parameters
        ----------
        thickness : list of int
            The thickness of each line.

        """
        return self._thickness

    @thickness.setter
    def thickness(self, thickness):
        if thickness:
            l = len(self.lines)
            t = len(thickness)
            if t < l:
                thickness += [self._default_thickness for i in range(l - t)]
            elif t > l:
                thickness[:] = thickness[:l]
            self._thickness = thickness

    @property
    def colour(self):
        """list : Individual line colours.

        Parameters
        ----------
        colour : list of str or 3-tuple
            The colour specification of each line in hex or RGB(255) format.

        """
        return self._colours
    
    @colour.setter
    def colour(self, colour):
        if colour:
            colour[:] = [FromArgb(* colour_to_rgb(c)) for c in colour]
            l = len(self.lines)
            c = len(colour)
            if c < l:
                colour += [self._default_colour for i in range(l - c)]
            elif c > l:
                colour[:] = colour[:l]
            self._colour = colour

    def DrawForeground(self, e):
        if self.colour:
            draw = e.Display.DrawLine
            if self.thickness:
                for i, (start, end) in enumerate(self.lines):
                    draw(Point3d(*start), Point3d(*end), self.colour[i], self.thickness[i])
            else:
                for i, (start, end) in enumerate(self.lines):
                    draw(Point3d(*start), Point3d(*end), self.colour[i], self._default_thickness)

        elif self.thickness:
            draw = e.Display.DrawLine
            if self.colour:
                for i, (start, end) in enumerate(self.lines):
                    draw(Point3d(*start), Point3d(*end), self.colour[i], self.thickness[i])
            else:
                for i, (start, end) in enumerate(self.lines):
                    draw(Point3d(*start), Point3d(*end), self._default_colour, self.thickness[i])

        else:
            lines = List[Line](len(self.lines))
            for start, end in self.lines:
                lines.Add(Line(Point3d(*start), Point3d(*end)))
            e.Display.DrawLines(lines, self._default_colour, self._default_thickness)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    from random import randint
    import time

    points = [(1.0 * randint(0, 30), 1.0 * randint(0, 30), 0.0) for _ in range(100)]
    lines  = [(points[i], points[i + 1]) for i in range(99)]

    try:
        conduit = LinesConduit(lines)
        conduit.Enabled = True

        for i in range(100):
            points = [(1.0 * randint(0, 30), 1.0 * randint(0, 30), 0.0) for _ in range(100)]
            conduit.lines = [(points[i], points[i + 1]) for i in range(99)]

            conduit.redraw()

            time.sleep(0.1)

    except Exception as e:
        print(e)

    finally:
        conduit.Enabled = False
        del conduit
