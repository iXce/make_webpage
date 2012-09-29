import os
import simplejson
import gzip
from PIL import Image

from color_interpolation import LinearColorMap

def flatten_singletons(l):
    first = l[0]
    if isinstance(first, list) and len(first) == 1:
        return [v[0] for v in l]
    else:
        return [flatten_singletons(v) for v in l]

def sanitize_plot(item, params):
    item["xdata"] = flatten_singletons(item["xdata"])
    item["ydata"] = flatten_singletons(item["ydata"])
    return item

def colorize_heatmap(heatmap, min_val, max_val, colormap):
    cmap = LinearColorMap(min_val, max_val, colormap, False)
    w = len(heatmap[0])
    h = len(heatmap)
    im = Image.new("RGB", (w, h))
    pixels = im.load()
    for x in range(w):
        for y in range(h):
            pixels[x, y] = cmap(heatmap[y][x])
    return im

DEFAULT_COLORMAP = ["#0a0", "#6c0", "#ee0", "#eb4", "#eb9", "#fff"]

def process_heatmap(item, params):
    data = item["data"]
    item["height"] = len(data)
    item["width"] = len(data[0])
    # FIXME : temp hack
    item["width"] = min(item["width"], 400)
    item["height"] = 0
    item["min"] = min([min(k) for k in data])
    item["max"] = max([max(k) for k in data])
    colormap = item["colormap"] if "colormap" in item else DEFAULT_COLORMAP
    img = colorize_heatmap(data, item["min"], item["max"], colormap)
    heatmap_json = "%08d.json" % process_heatmap.heatmap_id
    process_heatmap.heatmap_id += 1
    # Save image
    imgpath = os.path.join(params["target_dir"], "imgs", "json")
    if not os.path.exists(imgpath): os.makedirs(imgpath)
    img.save(os.path.join(imgpath, heatmap_json + ".png"), "PNG")
    item["imgurl"] = os.path.join("imgs", "json", heatmap_json + ".png")
    # Save JSON
    jsonpath = os.path.join(params["target_dir"], "json")
    if not os.path.exists(jsonpath): os.makedirs(jsonpath)
    json = simplejson.dumps(data)
    json = json.replace(" ", "")
    open(os.path.join(jsonpath, heatmap_json), "w").write(json)
    gzip.open(os.path.join(jsonpath, heatmap_json + ".gz"), "w").write(json.replace(" ", ""))
    del item["data"]
    # FIXME: dirty hack for gzipped jsons
    if params["WEB_ROOT"] in params["target_dir"]:
        item["url"] = os.path.join("static", "php", "servejson.php?json=" + heatmap_json)
    else:
        item["url"] = os.path.join("json", heatmap_json)
    return item
process_heatmap.heatmap_id = 1

item_processors = {"heatmap": process_heatmap,
                   "plot": sanitize_plot}
