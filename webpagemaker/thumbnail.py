from PIL import Image
import os

def make_thumbnail(item, orig_path=None):
    actual_path = orig_path or item["rawpath"]
    dirname, basename = os.path.split(item["url"])
    new_name = os.path.join(dirname, "thumbnail_%d_%d_%s" % (item["width"], item["height"], basename))
    dirname, basename = os.path.split(item["rawpath"])
    new_path = os.path.join(dirname, "thumbnail_%d_%d_%s" % (item["width"], item["height"], basename))
    if not os.path.exists(new_path) or (os.path.getmtime(actual_path) > os.path.getmtime(new_path)):
        image = Image.open(actual_path)
        image.thumbnail((int(item["width"]), int(item["height"])))
        image.save(new_path)
    return new_name
