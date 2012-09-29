import sys, os
import shutil

from jinja2 import Template, Environment, FileSystemLoader

from jinjafilters import inc_filter
from getimageinfo import getImageInfo
from utils import get_file_type, get_mimetype
from items import item_processors

DEBUG = False
THIS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # One level up
WEB_ROOT = "/meleze/data0/public_html"
WEB_URL = "http://www-roc.inria.fr/cluster-willow"

class Page(object):
    items = None
    parent = None
    path = ""
    title = ""
    description = ""

    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    def _get_breadcrumbs(self):
        if self.parent:
            return self.parent.breadcrumbs + [self]
        else:
            return [self]
    breadcrumbs = property(_get_breadcrumbs)

class WebpageMaker(object):
    params = None
    items = None
    item_types = {}
    cur_subpage_suffix = 1

    def __init__(self, data):
        params = data['params']
        params['target'] = os.path.expanduser(params['target'])
        params['target_dir'] = os.path.normpath(os.path.expanduser(params['target_dir']))
        params['target_url'] = params['target'].replace(WEB_ROOT, WEB_URL)
        params['copy_images'] = bool(params['copy_images'])
        self.params = params
        self.items = data['items']

    def prepare_output(self):
        """Copy static stuff (bootstrap, stylesheet, javascript)"""
        target_dir = self.params["target_dir"]
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
        static_dir = os.path.join(target_dir, "static")
        if DEBUG or not os.path.isdir(static_dir):
            if DEBUG and os.path.exists(static_dir): shutil.rmtree(static_dir)
            shutil.copytree(os.path.join(THIS_DIR, "static"), static_dir)

    def process_item(self, item):
        if isinstance(item, dict) and "subpage" in item:
            item["subpage"] = self.process_item(item["subpage"])
        if type(item) in (str,unicode) and os.path.exists(item):
            newitem = {"type": get_file_type(item), "mime": get_mimetype(item)}
            if newitem["type"] == "image":
                content_type, width, height = getImageInfo(open(item).read())
                if content_type and width and height:
                    newitem["width"] = width
                    newitem["height"] = height
            if self.params["copy_images"]:
                new_name = item.replace(os.sep, "_")
                new_path = os.path.join(self.params["target_dir"], "imgs", new_name)
                if not DEBUG: shutil.copy(item, new_path)
                newitem["url"] = os.path.join("imgs", new_name)
            else:
                newitem["url"] = item.replace(self.params["target_dir"], "")
            return newitem
        elif isinstance(item, dict) and "type" in item:
            if item["type"] in ("image", "video"):
                processed = self.process_item(item["url"])
                if isinstance(processed, dict):
                    item.update(processed)
                else:
                    item["url"] = processed
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
            if isinstance(items[i], dict) and "type" in items[i]:
                self.item_types[items[i]["type"]] = True
        return items

    def make_subpage(self, item, level, basename, parent):
        suffix = self.cur_subpage_suffix
        self.cur_subpage_suffix += 1
        subpage = Page("%s.%08d.html" % (basename, suffix), parent)
        subpage.items, extra_subpages = self.find_subpages(item, basename, level + 1, subpage)
        item = {"type": "subpage", "url": subpage.path}
        return item, subpage, extra_subpages

    def find_subpages(self, items, basename, level, parent):
        subpages = []
        for i in xrange(len(items)):
            item = items[i]
            if isinstance(item, dict) and "subpage" in item:
                item["subpage"], subpage, extra_subpages = self.make_subpage(item["subpage"], level, basename, parent)
                if "subpage_title" in item: subpage.title = item["subpage_title"]
                if "subpage_description" in item: subpage.description = item["subpage_description"]
                subpages.extend([subpage] + extra_subpages)
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
        template = env.get_template('webpage.html')
        target_path = os.path.join(self.params['target_dir'], page.path)
        context = {"params": self.params, "page": page, "types": self.item_types}
        open(target_path, "w").write(template.render(context))
        print >> sys.stderr, target_path.replace(WEB_ROOT, WEB_URL)

    def preprocess(self):
        items = self.process_items(self.items)
        basename = os.path.basename(self.params['target'])
        mainpage = Page(basename, None)
        mainpage.items, subpages = self.find_subpages(items, basename, 0, mainpage)
        mainpage.title = self.params["title"]
        mainpage.description = self.params["description"]
        pages = [mainpage] + subpages
        return pages

    def make(self):
        self.prepare_output()
        self.pages = self.preprocess()
        for page in self.pages:
            self.make_page(page)
