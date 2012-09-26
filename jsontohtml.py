#!/usr/bin/env python

import sys, os
import shutil

import simplejson
from jinja2 import Template, Environment, FileSystemLoader

DEBUG = False
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

def process_image(item, copy, target_dir):
    if type(item) in (str,unicode) and os.path.exists(item):
        if copy:
            new_name = item.replace(os.sep, "_")
            new_path = os.path.join(target_dir, "imgs", new_name)
            if not DEBUG: shutil.copy(item, new_path)
            # FIXME: add heuristic to get a better type (e.g. handle videos)
            return {"type": "image", "url": os.path.join("imgs", new_name)}
        else:
            return {"type": "image", "url": item.replace(target_dir, "")}
    elif isinstance(item, dict) and "image" in item:
        item["image"] = process_image(item["image"], copy, target_dir)
        return item
    elif isinstance(item, list):
        return process_images(item, copy, target_dir)
    else:
        return item

def process_images(items, copy, target_dir):
    """Replace any valid path found in the tree by {type:image,url:valid_url}
dict, and possibly copy the file to the target directory"""
    for i in xrange(len(items)):
        items[i] = process_image(items[i], copy, target_dir)
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
    return item, [subpage] + extra_subpages
make_subpage.cur_suffix = 1

def find_subpages(items, basename, level = 0):
    subpages = []
    for i in xrange(len(items)):
        item = items[i]
        if isinstance(item, dict) and "subpage" in item:
            item["subpage"], extra_subpages = make_subpage(item["subpage"], level, basename)
            subpages.extend(extra_subpages)
        elif isinstance(item, list):
            if level > 0 and level % 2 == 0: # level is even, we have a subpage
                item, extra_subpages = make_subpage(item, level, basename)
                subpages.extend(extra_subpages)
            else: # level is odd, not a subpage, just recurse
                item, extra_subpages = find_subpages(item, level + 1)
                subpages.extend(extra_subpages)
        items[i] = item
    return items, subpages

def make_page(page, params):
    print >> sys.stderr, "Rendering", page.path,
    env = Environment(loader = FileSystemLoader(os.path.join(THIS_DIR, "templates")),
                      trim_blocks = True)
    template = env.get_template('webpage.html')
    target_path = os.path.join(params['target_dir'], page.path)
    open(target_path, "w").write(template.render({"params": params, "items": page}))
    print >> sys.stderr, target_path.replace(WEB_ROOT, WEB_URL)

def processitems(items, params):
    items = process_images(items, params['copy_images'], params['target_dir'])
    basename = os.path.basename(params['target'])
    mainpage, subpages = find_subpages(items, basename)
    mainpage = L(mainpage)
    mainpage.path = basename
    pages = [mainpage] + subpages
    for page in pages:
        make_page(page, params)

def make_webpage(data):
    params = data['params']
    target_dir = params['target_dir']
    prepare_output(target_dir)
    params['copy_images'] = bool(params['copy_images'])
    processitems(data['items'], params)

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
