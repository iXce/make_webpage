#!/usr/bin/env python

import sys, os
from webpagemaker import WebpageMaker

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, "Usage: %s JSONFILE" % sys.argv[0]
        sys.exit(2)
    jsonfile = sys.argv[1]
    if not os.path.exists(jsonfile):
        print >> sys.stderr, "Missing json : %s" % jsonfile
        sys.exit(1)
    try:
        import ujson as json
    except ImportError:
        import json
    jsondata = json.load(open(jsonfile))
    maker = WebpageMaker(jsondata, packing = {'packed': True, 'pack_width': 842})
    maker.make()
