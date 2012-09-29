# Adapted from http://www.elifulkerson.com/projects/rgb-color-gradation.php

import string, math

def interpolate( startcolor, goalcolor, steps ):
    """
    wrapper for interpolate_tuple that accepts colors as html ("#CCCCC" and such)
    """
    start_tuple = make_color_tuple(startcolor)
    goal_tuple = make_color_tuple(goalcolor)

    return interpolate_tuple(start_tuple, goal_tuple, steps)

class LinearColorMap(object):
    def __init__(self, min_val, max_val, colormap, html = True):
        self.colormap = map(self._make_color_tuple, colormap)
        self.ncolors = len(colormap)
        self.min = min_val
        self.max = max_val
        self.range = self.max - self.min
        self.html = html
        self.cache = {}

    def _make_color_tuple(self, color):
        """
        turn something like "#000000" into 0,0,0
        or "#FFFFFF into "255,255,255"
        """
        if len(color) == 4:
            R = 2 * color[1]
            G = 2 * color[2]
            B = 2 * color[3]
        else:
            R = color[1:3]
            G = color[3:5]
            B = color[5:7]

        R = int(R, 16)
        G = int(G, 16)
        B = int(B, 16)

        return R, G, B

    def _interpolate(self, startcolor, goalcolor, start_prop):
        R = startcolor[0]
        G = startcolor[1]
        B = startcolor[2]

        targetR = goalcolor[0]
        targetG = goalcolor[1]
        targetB = goalcolor[2]

        DiffR = targetR - R
        DiffG = targetG - G
        DiffB = targetB - B

        iR = int(R + (DiffR * start_prop))
        iG = int(G + (DiffG * start_prop))
        iB = int(B + (DiffB * start_prop))

        if not self.html:
            return iR, iG, iB

        hR = string.replace(hex(iR), "0x", "")
        hG = string.replace(hex(iG), "0x", "")
        hB = string.replace(hex(iB), "0x", "")

        if len(hR) == 1:
            hR = "0" + hR
        if len(hB) == 1:
            hB = "0" + hB
        if len(hG) == 1:
            hG = "0" + hG

        return string.upper("#"+hR+hG+hB)

    def __call__(self, value):
        if value in self.cache: return self.cache[value]
        colorpos = (self.ncolors-1) * ((float(value) - self.min) / self.range)
        lower = int(math.floor(colorpos))
        upper = int(math.ceil(colorpos))
        lower_prop = colorpos - lower
        result = self._interpolate(self.colormap[lower], self.colormap[upper], lower_prop)
        self.cache[value] = result
        return result

if __name__ == "__main__":
    cmap = LinearColorMap(1, 10, ["#0a0", "#6c0", "#ee0", "#eb4", "#eb9", "#fff"])
    print cmap(1)
    print cmap(3.6)
    print cmap(10)

