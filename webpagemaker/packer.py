from arrange import RectanglePacker
import sys


def get_packable_items(items):
    packable_items = []
    for item in items:
        if isinstance(item, list):
            packable_items += get_packable_items(item)
        elif isinstance(item, dict) and "width" in item and "height" in item:
            packable_items.append(item)
    return packable_items


def pack_items(items, params):
    if "pack_width" in params:
        pack_width = params["pack_width"]
    else:
        pack_width = 100000
    if "pack_height" in params:
        pack_height = params["pack_height"]
    else:
        pack_height = 100000
    packable_items = get_packable_items(items)
    packer = RectanglePacker(pack_width, pack_height)
    packed_items = []
    failures = 0
    for item in packable_items:
        point = packer.pack(int(item["width"]), int(item["height"]))
        if not point:
            failures += 1
        else:
            item["point"] = point
            packed_items.append(item)
    if failures > 0:
        print >> sys.stderr, "Warning: could not pack %d items" % failures
    return packed_items
