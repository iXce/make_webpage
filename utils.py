import mimetypes, os

def get_mimetype(fname):
    mimetype, _ = mimetypes.guess_type(fname)
    if not mimetype and os.path.splitext(fname)[1] == "webm":
        mimetype ="video/webm"
    return mimetype

def get_file_type_by_mime(fname):
    mimetype = get_mimetype(fname)
    if not mimetype:
        return None
    category = mimetype.split("/")[0]
    if category in ("image", "video"):
        return category
    else:
        return None

def get_file_type_by_ext(fname):
    ext = os.path.splitext(fname)[1]
    if ext in ("webm",):
        return "video"
    else:
        return "file"

def get_file_type(fname):
    ftype = get_file_type_by_mime(fname)
    if not ftype:
        return get_file_type_by_ext(fname)
    else:
        return ftype
