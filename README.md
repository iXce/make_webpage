make_webpage
============

A python-based toolbox for easily generating pretty webpages in MATLAB.

Currently supported objects
===========================
- Images, as either MATLAB matrices or on-disk paths
- Videos, as on-disk paths
- Text
- Comment fields
- Line plots
- Subpages

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
Struct with .type = 'plot', .xdata = 1d or 2d matrix of values (2d if multiple plots),
same for .ydata

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
