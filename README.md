make_webpage
============

A python-based toolbox for easily generating pretty webpages in MATLAB.

Quick start
===========

MATLAB
------
    make_webpage(pagecell, '/path/to/output/directory/andmaybefilealso.html', params);
with pagecell a 1-d or 2-d cell holdings objects as defined below, and
params being a struct, which accept the following parameters:
  params.copy_images: 0 or 1 depending on if you want the script to copy the images
                      to a subdir of your webpage.
  params.title: the page title
  params.description: the page description
  params.paged: the number of items per page (do not specify it if you want a
                single page)
  params.header_lines: the number of lines from the top of the cell to
                       replicate for each page produced by automatic pagination

CLI
---
    cat fileslist | ./clitohtml.py /path/to/output/directory/andmaybefilealso.html
The fileslist file is a text file which is parsed as a table : lines are rows,
and space/tab separated chunks are columns. The clitohtml.py script takes some
options, such as -c which enables the copy of images to the target directory.

Currently supported objects
===========================
- Images, as either MATLAB matrices or on-disk paths
- Thumbnails & lightbox popups for images, or as galleries
- Videos, as on-disk paths
- Text
- Heatmaps
- Comment fields (interactive)
- Line plots
- Subpages
- Stacks
- Tables

Other features
==============
- Subpages (again)
- Automatic pagination

Planned features
================
- ???

How to define objects
=====================

Text
----
Either just a standard MATLAB string or a struct with `.type = 'text'` an
`.text = 'yourstring'`

Images & videos
---------------
Either just a path (or possibly just a matrix for images), or make a struct
with `.type = 'image'` (or `'video'`) and `.url = 'on_disk_path_to_image'`

If you want to display a matrix in your code as an image and want to specify
additional parameters make a struct with `.type = 'image'` and use the `.data`
field instead of the `.url` one. The image will be saved to disk with
reasonable settings and everything else will be transparent.

Currently only .mp4 and .webm video should correctly work. Might require some
browser-specific tricks.

You can specify the width and height at which the image or video should be
displayed by using the `.width` and `.height` fields. If you only specify one
of them, the toolbox will try to preserve the original aspect ratio.

Image thumbnails & lightbox popups
----------------------------------
Set the `.popup` field to something (1 is good enough) to have the image being
displayed as a thumbnail (which will be produced at the size specified by
`.width`/`.height` (same as for images/videos)) and a lightbox with the full
resolution image come up when you click on it.

Galleries
---------
As for thumbnails and lightbox popus, set the `.popup` field to `'gallery'`.
You can specify a title to display through the `.title` field. All images will
be displayed in a single gallery per page, which can be browsed by left/right
arrows or visual buttons.

Comments
--------
Just a struct with `.type = 'comment'`. Note that this service is using an
external server running a tiny Django app which serves these comments, server
which might go AWOL at any time with your comments.

Plots
-----
Struct with `.type = 'plot'`, `.xdata =` 1d or 2d matrix of values (2d if
multiple plots), same for `.ydata`

XKCD-like plots
---------------
Struct with `.type = 'xkcdplot'`, `.xdata =` 1d or 2d matrix of values (2d if
multiple plots), same for `.ydata`. You can specify `.minx`, `.maxx`, `.miny`, `.maxy`,
`.xlabel`, `.ylabel`, `.title` fields (min/max* handle the axis limits, the
other are the axis labels and plot title). You can also specify curves colors
through `.colors =` a cell array of colors (one per curve).

Heatmap
-------
Struct with `.type = 'heatmap'`, `.data = yourdatamatrix`. Produces a nice
colored heatmap with value-at-cursor-position tooltips. You can specify a
custom colormap by putting a cell of strings in `.colormap` field. The default
colormap is not the usual rainbow colormap, but rather one from [1].

Subpages
--------
Just put a cell into a 2d cell (putting a cell into a 1d cell will lead to a 2d
table page), which will make a "Subpage" link in the current page, or put your
subpage cell as a `.subpage` field of another object, on which the link to the
subpage will be added. If you use the latter, you can also specify the
`.subpage_title` and `.subpage_description` fields. If you want to make a text
link, make your item as before plus with `.type = 'text'` and `.text =
'the-link-text'` (as for a simple text object).

Stacks
------
A stack of items on top of each other, with a set of tabs to switch between
items. Define it as a struct with `.type = 'stack'`, `.stack =` cellofitems and
`.labels =` cellofstrings

Tables
------
A simple table. Define it as a struct with `.type = 'table'`, `.header =`
cellofitems, `.rows =` cellofcellofitems. Tables are really minipages instead
pages.

Pagination
==========
See the `params.paged` and `params.header_lines` parameters described at the
top of the page. The same parameters are also accepted through `--paged` and
`--header_lines` CLI options.

How to add a new object type
============================
There are two parts : the python layer and the templating layer.
If you do not need any pre-processing and can render your item with just HTML,
CSS and JavaScript, skip the python part.

Python part
-----------
webpagemaker/item.py defines the dictionnary item_processors. To add
preprocessing to your item type, just add an extra "itemtype":
your_item_processor mapping to this dictionnary, where your_item_processor is
your preprocessing function, which will have to take two parameters, the item
and the global software parameters (including thing like the target directory,
so that you can save extra static files to this place), and returns the
processed item. Items are handled as directories in Python, and Matlab matrices
as nested lists (i.e. for 2d matrices you'll have a list of list).  Please look
at the plot and heatmap processors if you're still wondering what you can do.

### Serving JSON files ###
As JSON is the standard for exchanging data with JavaSript, and as it is a very
convenient format for storing things such as matrices, I added a small PHP
script to serve gzipped json files if the browser supports it. That means that
you can output json files in params["target_dir"]/json plus their gzipped
version (with an extra .gz extension), and use
static/php/servejson.php?json=YOURFILE.json as your json file URL.

Please note that if you have more control on your webserver than I do, you can
achieve just the same thing without any PHP by using the Apache (or equivalent)
DEFLATE module and add application/json to the supported mime types that can be
compressed. The only difference is that in my script case, compression is
already done while Apache module would have to compress on the fly.

Template part
-------------
make_webpage uses the powerful, Django-inspired, Jinja2 templating engine for
rendering webpages. This way logic and data processing is almost completely
decoupled from layout/presentation.

### HTML
Handling a new item type is just a matter of extendif the if/else switch in
templates/item_type_switch.html, possibly adding a new template as
templates/item_YOURTYPE.html.

### JavaScript
If you need to add some javascript, you can put static javascript files in
static/js/ and reference them at the bottom of templates/webpage.html. To
include it only if there is one item of the given type, you can use a {% if
types.YOURTYPE %}{% endif block %}, and to include item-specific JS code,
extend templates/script_type_switch.html as for HTML sources.

#### Identifying HTML items in JavaScript code
A common issue with this architecture is that you (mostly) cannot directly
place item-specific JS code next to the HTML code, because static js libraries
are loaded at the end of the page (for better user experience). Thus we have to
iterate twice over the items set, and had to implement some workaround to be
able to reference specific HTML tags from dynamically generated JS code.

Each item is given an ID at the template level, which you can access through
the {{ itemid }} variable. You can thus give your HTML tag an ID such as
id="plotholder{{ itemid }}" and later reference this tag, for instance by using
a jQuery selector such as $("#plotholder{{ itemid }}").

### CSS
Simply add your item CSS to static/css/wswebpage.css, or you can add your own
custom CSS stylesheet and include it just as a static javascript file (with
{% if types.YOURTYPE %}, etc)

Dependencies (shipped in this package)
======================================
- Jinja2 for templating bits http://jinja.pocoo.org/
- Simplejson for python json handling https://github.com/simplejson/simplejson
- JSONlab for MATLAB json handling http://iso2mesh.sourceforge.net/cgi-bin/index.cgi?jsonlab
- Twitter Bootstrap for layout goodness http://twitter.github.com/bootstrap/
- jQuery for javascript handling http://jquery.com/
- Raphael/gRaphael for plots http://raphaeljs.com/ and http://g.raphaeljs.com/
- JAIL for lazy loading http://www.sebastianoarmelibattana.com/projects/jail
- d3.js for visualizations http://d3js.org/
- Magnific Popup for lightboxes http://dimsemenov.com/plugins/magnific-popup/

References
==========
[1] "Diverging Color Maps for Scientific Visualization." Kenneth Moreland. In
    Proceedings of the 5th International Symposium on Visual Computing. December
    2009.
