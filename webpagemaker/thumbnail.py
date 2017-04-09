from PIL import Image
import os


def adjust_thumb_size(item, params):
    if params["thumbwidth"]:
        if not params["thumbheight"]:
            item["height"] = float(item["height"]) / item["width"] * params["thumbwidth"]
            item["width"] = params["thumbwidth"]
        else:
            item["width"] = params["thumbwidth"]
            item["height"] = params["thumbheight"]
    else:
        item["width"] = float(item["width"]) / item["height"] * params["thumbheight"]
        item["height"] = params["thumbheight"]


def _get_exif_orientation(im):
    if hasattr(im, "_getexif"):
        exif = im._getexif()
        if exif:
            orientation_key = 274  # cf ExifTags
            if orientation_key in exif:
                orientation = exif[orientation_key]
                return orientation
    return None


def get_image_size(filename):
    with Image.open(filename) as im:
        width, height = im.size
        if _get_exif_orientation(im) in {6, 8}:
            width, height = height, width
        return width, height


def load_and_rotate(filename):
    im = Image.open(filename)
    orientation = _get_exif_orientation(im)
    rotate_values = {3: 180, 6: 270, 8: 90}
    if orientation in rotate_values:
        im = im.rotate(rotate_values[orientation], expand=True)
    return im


def make_thumbnail(item, orig_path=None):
    actual_path = orig_path or item["rawpath"]
    dirname, basename = os.path.split(item["url"])
    new_name = os.path.join(dirname, "thumbnail_%d_%d_%s" % (item["width"], item["height"], basename))
    dirname, basename = os.path.split(item["rawpath"])
    new_path = os.path.join(dirname, "thumbnail_%d_%d_%s" % (item["width"], item["height"], basename))
    if not os.path.exists(new_path) or (os.path.getmtime(actual_path) > os.path.getmtime(new_path)):
        image = load_and_rotate(actual_path)
        image.thumbnail((int(item["width"]), int(item["height"])))
        image.save(new_path)
    return new_name
