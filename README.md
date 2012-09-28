make_webpage
============

A python-based toolbox for easily generating pretty webpages in MATLAB.

Currently supported objects
===========================
- Images, as either MATLAB matrices or on-disk paths
- Videos, as on-disk paths
- Text
- Heatmaps
- Comment fields (interactive)
- Line plots
- Subpages

Planned features
================
- Stacked items (several items on top of each other, with one label per item,
  switching between items is done through a combobox or a list of buttons)

How to define objects
=====================

Images & videos
---------------
Either just a path (or possibly just a matrix for images), or make a struct
with .type = 'image' (or 'video') and .url = 'on_disk_path_to_image'

Comments
--------
Just a struct with .type = 'comment'

Plots
-----
Struct with .type = 'plot', .xdata = 1d or 2d matrix of values (2d if multiple
plots), same for .ydata

Heatmap
-------
Struct with .type = 'heatmap', .data = yourdatamatrix. Produces a nice colored
heatmap with value-at-cursor-position tooltips.

Subpages
--------
Just put a cell into a 2d cell (putting a cell into a 1d cell will lead to a 2d
table page), which will make a "Subpage" link in the current page, or put your
subpage cell as a .subpage field of another object, on which the link to the
subpage will be added. If you use the latter, you can also specify the
.subpage_title and .subpage_description fields.

Dependencies (shipped in this package)
======================================
- Jinja2 for templating bits http://jinja.pocoo.org/
- Simplejson for python json handling https://github.com/simplejson/simplejson
- JSONlab for MATLAB json handling http://iso2mesh.sourceforge.net/cgi-bin/index.cgi?jsonlab
- Twitter Bootstrap for layout goodness http://twitter.github.com/bootstrap/
- jQuery for javascript handling http://jquery.com/
- Raphael/gRaphael for plots http://raphaeljs.com/ and http://g.raphaeljs.com/
- JAIL for lazy loading http://www.sebastianoarmelibattana.com/projects/jail
