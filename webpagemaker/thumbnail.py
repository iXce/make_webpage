from PIL import Image
import os

def make_thumbnail(item):
    dirname, basename = os.path.split(item["url"])
    new_name = os.path.join(dirname, "thumbnail_%d_%d_%s" % (item["width"], item["height"], basename))
    dirname, basename = os.path.split(item["rawpath"])
    new_path = os.path.join(dirname, "thumbnail_%d_%d_%s" % (item["width"], item["height"], basename))
    image = Image.open(item["rawpath"])
    image.thumbnail((item["width"], item["height"]))
    image.save(new_path)
    return new_name
