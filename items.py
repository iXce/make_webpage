import os
import simplejson
import gzip

def flatten_singletons(l):
    first = l[0]
    if isinstance(first, list) and len(first) == 1:
        return [v[0] for v in l]
    else:
        return [flatten_singletons(v) for v in l]

def sanitize_plot(item):
    item["xdata"] = flatten_singletons(item["xdata"])
    item["ydata"] = flatten_singletons(item["ydata"])
    return item

def process_heatmap(item, target_dir):
    data = item["data"]
    item["height"] = len(data)
    item["width"] = len(data[0])
    # FIXME : temp hack
    item["width"] = min(item["width"], 400)
    item["height"] = 0
    item["min"] = min([min(k) for k in data])
    item["max"] = max([max(k) for k in data])
    # Precompute image ?
    heatmap_json = "%08d.json" % process_heatmap.heatmap_id
    process_heatmap.heatmap_id += 1
    jsonpath = os.path.join(target_dir, "json")
    if not os.path.exists(jsonpath):
        os.makedirs(jsonpath)
    json = simplejson.dumps(data)
    json = json.replace(" ", "")
    open(os.path.join(jsonpath, heatmap_json), "w").write(json)
    gzip.open(os.path.join(jsonpath, heatmap_json + ".gz"), "w").write(json.replace(" ", ""))
    del item["data"]
    # FIXME: dirty hack for gzipped jsons
    #item["url"] = os.path.join("json", heatmap_json)
    item["url"] = os.path.join("static", "php", "servejson.php?json=" + heatmap_json)
    return item
process_heatmap.heatmap_id = 1
