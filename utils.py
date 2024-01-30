def safe_get_text(obj, name=None, attrs={}, recursive=True, string=None,
             **kwargs):
    r = None
    l = obj.find_all(name, attrs, recursive, string, 1, **kwargs)
    if l:
        r = l[0].text.replace("\r\n", "  ")
    return r


def safe_get_href(obj, name=None, attrs={}, recursive=True, string=None,
             **kwargs):
    r = None
    l = obj.find_all(name, attrs, recursive, string, 1, **kwargs)
    if l:
        r = l[0]["href"].replace("\r\n", "  ")
    return r