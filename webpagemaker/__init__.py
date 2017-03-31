# coding: utf-8

import sys, os
import shutil
import math
import datetime
import codecs

from jinja2 import Template, Environment, FileSystemLoader

from jinjafilters import inc_filter
from thumbnail import make_thumbnail
from getimageinfo import getImageInfo
from utils import get_file_type, get_mimetype
from items import item_processors

DEBUG = False
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class Page(object):
    items = None
    parent = None
    path = ""
    title = ""
    description = ""
    sortable = False
    header = None

    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    def _get_breadcrumbs(self):
        if self.parent:
            return self.parent.breadcrumbs + [self]
        else:
            return [self]
    breadcrumbs = property(_get_breadcrumbs)
    
def register_type(func):
    def wrapped(self, *a):
        item = func(self, *a)
        if isinstance(item, dict) and "type" in item:
            self.item_types[item["type"]] = True
        return item
    return wrapped

class WebpageMaker(object):
    params = None
    items = None
    item_types = {}
    cur_subpage_suffix = 1

    def __init__(self, data, packing = None):
        params = data['params']
        target = os.path.expanduser(params['target'])
        target = os.path.abspath(target)
        if os.path.splitext(target)[1] == "":
            target_dir = target
            target = os.path.join(target, "index.html")
        else:
            target_dir = os.path.dirname(target)
        params['target'] = target
        params['target_dir'] = target_dir
        params['WEB_ROOT'] = params.get('WEB_ROOT', None)
        params['WEB_URL'] = params.get('WEB_URL', None)
        params['target_url'] = params['target']
        if params['WEB_ROOT'] is not None and params['WEB_URL'] is not None:
            params['target_url'] = params['target_url'].replace(params['WEB_ROOT'], params['WEB_URL'])
        params['copy_images'] = bool(params.get('copy_images', False))
        params['sortable'] = bool(params.get('sortable', False))
        params['packed'] = bool(params.get('packed', False))
        params['paged'] = params.get('paged', False)
        params['title'] = params.get('title', '')
        params['description'] = params.get('description', '')
        if packing:
            params.update(packing)
        self.params = params
        self.items = data['items']

    def prepare_output(self):
        """Copy static stuff (bootstrap, stylesheet, javascript)"""
        target_dir = self.params["target_dir"]
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
        img_dir = os.path.join(self.params["target_dir"], "imgs")
        if not os.path.isdir(img_dir):
            os.makedirs(img_dir)
        static_dir = os.path.join(target_dir, "static")
        if DEBUG or not os.path.isdir(static_dir):
            if DEBUG and os.path.exists(static_dir): shutil.rmtree(static_dir)
            shutil.copytree(os.path.join(THIS_DIR, "static"), static_dir)
        if 'extraimages' in self.params:
            extra_images = self.params['extraimages']
            extra_images_dir = os.path.join(img_dir, "extras")
            if not os.path.isdir(extra_images_dir):
                os.makedirs(extra_images_dir)
            for img in extra_images:
                new_name = os.path.basename(img)
                new_path = os.path.join(self.params["target_dir"], "imgs", "extras", new_name)
                if not DEBUG and (not os.path.exists(new_path) or (os.path.getmtime(img) > os.path.getmtime(new_path))): shutil.copy(img, new_path)

    @register_type
    def process_item(self, item, orig_item = None):
        if isinstance(item, dict) and "subpage" in item:
            item["subpage"] = self.process_item(item["subpage"])
        if type(item) in (str,unicode) and os.path.exists(item) and not os.path.isdir(item):
            if not orig_item: orig_item = {}
            newitem = {"type": get_file_type(item), "mime": get_mimetype(item)}
            if "width" in orig_item: newitem["width"] = orig_item["width"]
            if "height" in orig_item: newitem["height"] = orig_item["height"]
            if newitem["type"] == "image" and ("width" not in newitem or "height" not in newitem):
                content_type, width, height = getImageInfo(open(item).read())
                if content_type and width and height:
                    try:
                        if "width" not in newitem and "height" not in newitem:
                            newitem["width"] = width
                            newitem["height"] = height
                        elif "width" not in newitem:
                            newitem["width"] = width * newitem["height"] / height
                        else:
                            newitem["height"] = height * newitem["width"] / width
                    except TypeError:
                        pass
            newitem["rawpath"] = item
            if self.params['WEB_ROOT'] and self.params['WEB_URL'] and self.params["WEB_ROOT"] in item:
                newitem["url"] = item.replace(self.params["WEB_ROOT"],
                                              self.params["WEB_URL"])
            elif self.params["copy_images"]:
                new_name = item.replace(os.sep, "_")
                new_path = os.path.join(self.params["target_dir"], "imgs", new_name)
                if not DEBUG and (not os.path.exists(new_path) or (os.path.getmtime(item) > os.path.getmtime(new_path))): shutil.copy(item, new_path)
                newitem["rawpath"] = new_path
                newitem["url"] = os.path.join("imgs", new_name)
            else:
                newitem["url"] = item.replace(self.params["target_dir"], "")
            return newitem
        elif isinstance(item, dict) and "type" in item:
            if item["type"] in ("image", "video", "thumbnail"):
                processed = self.process_item(item["url"], item)
                if isinstance(processed, dict):
                    item.update(processed)
                else:
                    item["url"] = processed
                if ("popup" in item or item["type"] == "thumbnail") and "rawpath" in item:
                    item["url"] = make_thumbnail(item)
                    if item["type"] != "thumbnail":
                        item["fullurl"] = item["url"]
                        item["type"] = "imagegallery" if item["popup"] == "gallery" else "imagepopup"
                    else:
                        item["type"] = "image"
                return item
            elif item["type"] == "stack":
                item["stack"] = self.process_items(item["stack"])
                return item
            elif item["type"] in item_processors:
                return item_processors[item["type"]](item, self.params)
            else:
                return item
        elif isinstance(item, list):
            return self.process_items(item)
        else:
            return item

    def process_items(self, items):
        """Replace any valid path found in the tree by {type:image,url:valid_url}
dict, and possibly copy the file to the target directory"""
        for i in xrange(len(items)):
            items[i] = self.process_item(items[i])
        return items

    def make_subpage(self, item, level, basename, parent):
        suffix = self.cur_subpage_suffix
        self.cur_subpage_suffix += 1
        subpage = Page("%s.%08d.html" % (basename, suffix), parent)
        subpage.items, extra_subpages = self.find_subpages(item, basename, level + 1, subpage)
        item = {"type": "subpage", "url": subpage.path}
        return item, subpage, extra_subpages

    def find_subpages(self, items, basename, level, parent):
        if not isinstance(items, list): items = [items]
        subpages = []
        for i in xrange(len(items)):
            item = items[i]
            if isinstance(item, dict) and "subpage" in item:
                item["subpage"], subpage, extra_subpages = self.make_subpage(item["subpage"], 0, basename, parent)
                if "subpage_title" in item: subpage.title = item["subpage_title"]
                if "subpage_description" in item: subpage.description = item["subpage_description"]
                if "subpage_header" in item: subpage.header = item["subpage_header"]
                subpage.sortable = "subpage_sortable" in item and bool(item["subpage_sortable"])
                subpages.extend([subpage] + extra_subpages)
            elif isinstance(item, dict) and "type" in item and item["type"] == "stack":
                item["stack"], extra_subpages = self.find_subpages(item["stack"], basename, level, parent)
                subpages.extend(extra_subpages)
            elif isinstance(item, list):
                if level > 0 and level % 2 == 0: # level is even, we have a subpage
                    item, subpage, extra_subpages = self.make_subpage(item, level, basename, parent)
                    subpages.extend([subpage] + extra_subpages)
                else: # level is odd, not a subpage, just recurse
                    item, extra_subpages = self.find_subpages(item, basename, level + 1, parent)
                    subpages.extend(extra_subpages)
            items[i] = item
        return items, subpages

    def make_page(self, page):
        print >> sys.stderr, "Rendering", page.path,
        env = Environment(loader = FileSystemLoader(os.path.join(THIS_DIR, "templates")),
                          extensions = ['jinja2.ext.with_', 'jinja2.ext.do'],
                          trim_blocks = True)
        env.filters['inc'] = inc_filter
        if self.params['packed']:
            template = env.get_template('webpage_packed.html')
        else:
            template = env.get_template('webpage.html')
        target_path = os.path.join(self.params['target_dir'], page.path)
        context = {"params": self.params, "page": page, "types": self.item_types, "currentdate": datetime.datetime.now()}
        codecs.open(target_path, "w", "utf-8").write(template.render(context))
        if self.params['WEB_ROOT'] and self.params['WEB_URL']:
            target_path = target_path.replace(self.params['WEB_ROOT'], self.params['WEB_URL'])
        print >> sys.stderr, target_path
        return target_path

    def preprocess(self):
        items = self.process_item(self.items)
        basename = os.path.basename(self.params['target'])
        mainpage = Page(basename, None)
        mainpage.items, extra_pages = self.find_subpages(items, basename, 0, mainpage)
        mainpage.title = self.params["title"]
        mainpage.description = self.params["description"]
        mainpage.sortable = self.params["sortable"]
        mainpage.header = self.params["header"] if "header" in self.params else None
        if self.params['paged']:
            n_per_page = self.params['paged']
            n_header_lines = self.params['header_lines'] if 'header_lines' in self.params else 0
            items = mainpage.items
            n_lines = len(items)
            if n_lines > n_per_page + n_header_lines:
                header = items[0:n_header_lines]
                n_pages = int(math.ceil(float(n_lines - n_header_lines) / n_per_page))
                paged_format = "%s.paged%08d.html"
                for i in range(n_pages):
                    start = n_header_lines+i*n_per_page
                    page_items = header + items[start:(start+n_per_page)]
                    prev_paged = paged_format % (basename, i-1) if i > 1 else (basename if i == 1 else None)
                    next_paged = paged_format % (basename, i+1) if (i+1) < n_pages else None
                    links = []
                    if prev_paged: links.append("<a href=\"%s\">&lt;&lt;</a>" % prev_paged)
                    if n_pages > 10:
                        page_range = [0] + range(max(1, i - 4), min(i + 4, n_pages - 1)) + [n_pages - 1]
                    else:
                        page_range = range(n_pages)
                    for k_i, k in enumerate(page_range):
                        k_paged = paged_format % (basename, k) if k > 0 else basename
                        if k_i > 0 and page_range[k_i - 1] != k - 1:
                            links.append("<span>&hellip;</span>")
                        if k == i:
                            links.append("<strong>[%d]</strong>" % (k + 1,))
                        else:
                            links.append("<a href=\"%s\">%d</a>" % (k_paged, k + 1))
                    if next_paged: links.append("<a href=\"%s\">&gt;&gt;</a>" % next_paged)
                    page_items.append("<span class=\"paged_links\">%s</span>" % "".join(links))
                    if i == 0:
                        mainpage.items = page_items
                    else:
                        pagedpage = Page(paged_format % (basename, i), None)
                        pagedpage.items = page_items
                        pagedpage.title = self.params["title"]
                        pagedpage.description = self.params["description"]
                        pagedpage.sortable = self.params["sortable"]
                        extra_pages.append(pagedpage)
        pages = [mainpage] + extra_pages
        if self.params['packed']:
            from packer import pack_items
            for page in pages:
                page.items = pack_items(page.items, self.params)
        return pages

    def make(self):
        self.prepare_output()
        self.pages = self.preprocess()
        urls = []
        for page in self.pages:
            url = self.make_page(page)
            urls.append(url)
        return urls
