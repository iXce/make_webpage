#!/usr/bin/env python

import sys, os
import shutil

import simplejson
import mimetypes
from jinja2 import Template, Environment, FileSystemLoader
from jinjafilters import inc_filter
from getimageinfo import getImageInfo

DEBUG = True
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_ROOT = "/meleze/data0/public_html"
WEB_URL = "http://www-roc.inria.fr/cluster-willow"

def prepare_output(target_dir):
    """Copy static stuff (bootstrap, stylesheet, javascript)"""
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    static_dir = os.path.join(target_dir, "static")
    if DEBUG or not os.path.isdir(static_dir):
        if DEBUG: shutil.rmtree(static_dir)
        shutil.copytree(os.path.join(THIS_DIR, "static"), static_dir)

def get_mimetype(fname):
    mimetype, _ = mimetypes.guess_type(fname)
    if not mimetype and os.path.splitext(fname)[1] == "webm":
        mimetype ="video/webm"
    return mimetype

def get_file_type_by_mime(fname):
    mimetype = get_mimetype(fname)
    if not mimetype:
        return None
    category = mimetype.split("/")[0]
    if category in ("image", "video"):
        return category
    else:
        return None

def get_file_type_by_ext(fname):
    ext = os.path.splitext(fname)[1]
    if ext in ("webm",):
        return "video"
    else:
        return "file"

def get_file_type(fname):
    ftype = get_file_type_by_mime(fname)
    if not ftype:
        return get_file_type_by_ext(fname)
    else:
        return ftype

def flatten_singletons(l):
    first = l[0]
    if isinstance(first, list) and len(first) == 1:
        return [v[0] for v in l]
    else:
        return [flatten_singletons(v) for v in l]

def sanitize_plot(item):
    item["xdata"] = flatten_singletons(item["xdata"])
    item["ydata"] = flatten_singletons(item["ydata"])
    return item

def process_item(item, copy, target_dir):
    if isinstance(item, dict) and "subpage" in item:
        item["subpage"] = process_item(item["subpage"], copy, target_dir)
    if type(item) in (str,unicode) and os.path.exists(item):
        newitem = {"type": get_file_type(item), "mime": get_mimetype(item)}
        if newitem["type"] == "image":
            content_type, width, height = getImageInfo(open(item).read())
            if content_type and width and height:
                newitem["width"] = width
                newitem["height"] = height
        if copy:
            new_name = item.replace(os.sep, "_")
            new_path = os.path.join(target_dir, "imgs", new_name)
            if not DEBUG: shutil.copy(item, new_path)
            newitem["url"] = os.path.join("imgs", new_name)
        else:
            newitem["url"] = item.replace(target_dir, "")
        return newitem
    elif isinstance(item, dict) and "image" in item:
        item["image"] = process_item(item["image"], copy, target_dir)
        return item
    elif isinstance(item, dict) and "type" in item and item["type"] == "plot":
        return sanitize_plot(item)
    elif isinstance(item, list):
        return process_items(item, copy, target_dir)
    else:
        return item

ALL_TYPES = {}

def process_items(items, copy, target_dir):
    """Replace any valid path found in the tree by {type:image,url:valid_url}
dict, and possibly copy the file to the target directory"""
    for i in xrange(len(items)):
        items[i] = process_item(items[i], copy, target_dir)
        if isinstance(items[i], dict) and "type" in items[i]:
            ALL_TYPES[items[i]["type"]] = True
    return items

class L(list):
    pass

def make_subpage(item, level, basename):
    suffix = make_subpage.cur_suffix
    make_subpage.cur_suffix += 1
    subpage, extra_subpages = find_subpages(item, basename, level + 1)
    subpage = L(subpage)
    subpage.path = "%s.%08d.html" % (basename, suffix)
    item = {"type": "subpage", "url": subpage.path}
    return item, subpage, extra_subpages
make_subpage.cur_suffix = 1

def find_subpages(items, basename, level = 0):
    subpages = []
    for i in xrange(len(items)):
        item = items[i]
        if isinstance(item, dict) and "subpage" in item:
            item["subpage"], subpage, extra_subpages = make_subpage(item["subpage"], level, basename)
            if "subpage_title" in item: subpage.title = item["subpage_title"]
            if "subpage_description" in item: subpage.description = item["subpage_description"]
            subpages.extend([subpage] + extra_subpages)
        elif isinstance(item, list):
            if level > 0 and level % 2 == 0: # level is even, we have a subpage
                item, subpage, extra_subpages = make_subpage(item, level, basename)
                subpages.extend([subpage] + extra_subpages)
            else: # level is odd, not a subpage, just recurse
                item, extra_subpages = find_subpages(item, basename, level + 1)
                subpages.extend(extra_subpages)
        items[i] = item
    return items, subpages

def make_page(page, params):
    print >> sys.stderr, "Rendering", page.path,
    env = Environment(loader = FileSystemLoader(os.path.join(THIS_DIR, "templates")),
                      extensions = ['jinja2.ext.with_', 'jinja2.ext.do'],
                      trim_blocks = True)
    env.filters['inc'] = inc_filter
    template = env.get_template('webpage.html')
    target_path = os.path.join(params['target_dir'], page.path)
    context = {"params": params, "page": page, "types": ALL_TYPES}
    open(target_path, "w").write(template.render(context))
    print >> sys.stderr, target_path.replace(WEB_ROOT, WEB_URL)

def preprocess(items, params):
    items = process_items(items, params['copy_images'], params['target_dir'])
    basename = os.path.basename(params['target'])
    mainpage, subpages = find_subpages(items, basename)
    mainpage = L(mainpage)
    mainpage.path = basename
    mainpage.title = params["title"]
    mainpage.description = params["description"]
    pages = [mainpage] + subpages
    return pages

def make_webpage(data):
    params = data['params']
    target_dir = params['target_dir']
    params['target_url'] = params['target'].replace(WEB_ROOT, WEB_URL)
    prepare_output(target_dir)
    params['copy_images'] = bool(params['copy_images'])
    pages = preprocess(data['items'], params)
    for page in pages:
        make_page(page, params)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, "Usage: %s JSONFILE" % sys.argv[0]
        sys.exit(2)
    jsonfile = sys.argv[1]
    if not os.path.exists(jsonfile):
        print >> sys.stderr, "Missing json : %s" % jsonfile
        sys.exit(1)
    jsondata = simplejson.load(open(jsonfile))
    make_webpage(jsondata)
