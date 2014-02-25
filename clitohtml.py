#!/usr/bin/env python

from optparse import OptionParser
import sys, os

from jsontohtml import WebpageMaker

if __name__ == "__main__":
    parser = OptionParser(usage = "usage: %prog [options] target.html")
    parser.add_option("-t", "--title", dest = "title", default  = "",
                      help = "set page title to TITLE", metavar = "TITLE")
    parser.add_option("-d", "--description", dest = "description", default = "",
                      help = "set page description to DESC", metavar = "DESC")
    parser.add_option("-c", "--copy-images", action = "store_true",
                      dest = "copy_images", default = False,
                      help = "copy images to target folder")
    parser.add_option("--paged", type = "int", dest = "paged", default = 0)
    parser.add_option("--header-lines", type = "int", dest = "header_lines", default = 0)

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    target = args[0]
    target = os.path.abspath(target)
    if os.path.splitext(target)[1] == "":
        target_dir = target
        target = os.path.join(target, "index.html")
    else:
        target_dir = os.path.dirname(target)
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    params = {"target_dir": target_dir,
              "target": target,
              "title": options.title,
              "description": options.description,
              "copy_images": options.copy_images,
              "packed": False,
              "paged": options.paged,
              "header_lines": options.header_lines,
              "sortable": False,
              "header": None}
    items = []
    for line in sys.stdin:
        items.append(line.strip().split())
    maker = WebpageMaker({"items": items, "params": params})
    maker.make()
