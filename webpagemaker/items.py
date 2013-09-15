import os
import simplejson
import gzip
import collections
from PIL import Image

from color_interpolation import LinearColorMap

def flatten_singletons(l):
    first = l[0]
    if not isinstance(first, collections.Iterable):
        return [v for v in l]
    elif len(first) == 1:
        return [v[0] for v in l]
    else:
        return [flatten_singletons(v) for v in l]

def sanitize_plot(item, params):
    xdata = flatten_singletons(item["xdata"])
    ydata = flatten_singletons(item["ydata"])
    if not isinstance(ydata[0], collections.Iterable):
        ydata = [ydata]
    if not isinstance(xdata[0], collections.Iterable):
        xdata = [xdata] * len(ydata)
    if len(xdata) != len(ydata):
        raise ValueError, "xdata and ydata must have the same number of " \
                          "values lists or xdata be a single values list"
    if "labels" in item and len(ydata) != len(item["labels"]):
        raise ValueError, "you must either provide a label for each ydata " \
                          "values list or no label at all"
    if "colors" in item and len(ydata) > len(item["colors"]):
        raise ValueError, "you must either provide a color for at least "\
                          "each ydata values list or no color at all"
    allseries = zip(xdata, ydata)
    data = []
    for k, (xdata, ydata) in enumerate(allseries):
        entry = {"values": [{"x": xdata[i], "y": ydata[i]}
                            for i in range(len(xdata))]
                }
        entry["key"] = item["labels"][k] if "labels" in item else "Set %d" % k
        if "colors" in item:
            entry["color"] = item["colors"][k]
        data.append(entry)
    item["data"] = simplejson.dumps(data)
    item["tdattrs"] = "class = \"plotholder\" " + item["attrs"] if "attrs" in item else ""
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

COLORMAPS = {
    "divergent": ["#3b4cc0","#445acc","#4d68d7","#5775e1","#6282ea","#6c8ef1","#779af7","#82a5fb","#8db0fe","#98b9ff","#a3c2ff","#aec9fd","#b8d0f9","#c2d5f4","#ccd9ee","#d5dbe6","#dddddd","#e5d8d1","#ecd3c5","#f1ccb9","#f5c4ad","#f7bba0","#f7b194","#f7a687","#f49a7b","#f18d6f","#ec7f63","#e57058","#de604d","#d55042","#cb3e38","#c0282f","#b40426"],
    "greenyellow": ["#0a0", "#6c0", "#ee0", "#eb4", "#eb9", "#fff"],
}
DEFAULT_COLORMAP = COLORMAPS["divergent"]

def process_heatmap(item, params):
    data = item["data"]
    item["height"] = len(data)
    item["width"] = len(data[0])
    # FIXME : temp hack
    #item["width"] = min(item["width"], 400)
    #item["height"] = 0
    if not "min" in item:
        item["min"] = min([min(k) for k in data])
    if not "max" in item:
        item["max"] = max([max(k) for k in data])
    colormap = item["colormap"] if "colormap" in item else DEFAULT_COLORMAP
    if type(colormap) in (str, unicode):
        if colormap in COLORMAPS: colormap = COLORMAPS[colormap]
        else: colormap = DEFAULT_COLORMAP
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

class XKCDCurve(list):
    def __init__(self, l):
        l2 = self._prune(l)
        l2 = self._smooth(l2)
        l2 = self._shorten(l2)
        super(XKCDCurve, self).__init__(l2)

    def _prune(self, l):
        l2 = [l[0]]
        for i in range(1, len(l)):
            if l2[-1]["x"] == l[i]["x"] and l2[-1]["y"] == l[i]["y"]:
                continue
            else:
                l2.append(l[i])
        return l2

    def _shorten(self, l, max_count = 200):
        if len(l) <= max_count: return l
        else: return l[::len(l)/max_count]

    def _smooth(self, l):
        l2 = [l[0]] + l[:-1]
        l3 = l[1:] + [l[-1]]
        return map(lambda x,y,z: {"x": y["x"], "y": (float(x["y"])+float(y["y"])+float(z["y"]))/3}, l, l2, l3)

XKCDCOLORS = ["steelblue", "red", '#bcbd22', '#c5b0d5', '#ff9896', '#dbdb8d', '#98df8a', '#7f7f7f', '#d62728', '#2ca02c', '#f7b6d2', '#c7c7c7', '#9edae', '#17becf', '#9467bd', '#ff7f0e', '#e377c2', '#8c564b', '#1f77b4', '#ffbb78', '#c49c94', '#aec7e8', "#6BAED6"]

def process_xkcdplot(item, params):
    # Sanitize plot
    item = sanitize_plot(item, params)
    # Now prepare curves
    if type(item["ydata"][0]) == list:
        item["curves"] = [XKCDCurve([{"x": item["xdata"][l][i], "y": item["ydata"][l][i]}
                                     for i in range(0, len(item["ydata"][l]))])
                                    for l in range(len(item["ydata"]))]
    else:
        item["curves"] = XKCDCurve([{"x": item["xdata"][i], "y": item["ydata"][i]}
                                    for i in range(len(item["ydata"]))])
    minxs = []
    maxxs = []
    minys = []
    maxys = []
    for curve in item["curves"]:
        minxs.append(min((p["x"] for p in curve)))
        maxxs.append(max((p["x"] for p in curve)))
        minys.append(min((p["y"] for p in curve)))
        maxys.append(max((p["y"] for p in curve)))
    if "minx" not in item: item["minx"] = min(minxs)
    if "maxx" not in item: item["maxx"] = max(maxxs)
    if "miny" not in item: item["miny"] = min(minys)
    if "maxy" not in item: item["maxy"] = max(maxys)
    if "colors" in item:
        for i in range(min(len(item["colors"]), len(item["curves"]))):
            item["curves"][i].color = item["colors"][i]
    else:
        for i in range(min(len(XKCDCOLORS), len(item["curves"]))):
            item["curves"][i].color = XKCDCOLORS[i]
    if not "xlabel" in item: item["xlabel"] = ""
    if not "ylabel" in item: item["ylabel"] = ""
    if not "title" in item: item["title"] = ""
    return item

item_processors = {"heatmap": process_heatmap,
                   "plot": sanitize_plot,
                   "xkcdplot": process_xkcdplot}
