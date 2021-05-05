from abc import ABC

class formathtml(ABC):
    unique_tag: tuple = ("html", "head", "body")
    selfend_tag: tuple = ("br", "img", "meta", "link", "input")
    valid_tag: tuple = ("path", "a", "abbr", "acronym", "address", "applet", "area", "article", "aside", "audio", "b", "base", "basefont", "bdi", "bdo", "big", "blockquote", "body", "br", "button", "canvas", "caption", "center", "cite", "code", "col", "colgroup", "data", "datalist", "dd", "del", "details", "dfn", "dialog", "dir", "div", "dl", "dt", "em", "embed", "fieldset", "figcaption", "figure", "font", "footer", "form", "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hr", "html", "i", "iframe", "img", "input", "ins",
                        "kbd", "label", "legend", "li", "link", "main", "map", "mark", "meta", "meter", "nav", "noframes", "noscript", "object", "ol", "optgroup", "option", "output", "p", "param", "picture", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "script", "section", "select", "small", "source", "span", "strike", "strong", "style", "sub", "summary", "sup", "svg", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track", "tt", "u", "ul", "var", "video", "wbr")
    cols: tuple = ("_tag", "_attr", "_text", "_child")
    rmhtml: tuple = ("&emsp;", "&nbsp;")

    def __init__(self, url: str = None):
        if url != None:
            html = self.get_content(url=url)
            if html != None:
                self.set(html=html)
        pass

    def get_content(self, url: str) -> str:
        import requests
        req = requests.get(url)
        if req.status_code == 200:
            return req.text
        return None

    def set(self, html: str) -> list:
        def __getattr(attr: str) -> dict:
            import re
            rtn = {}
            vals = []
            joinb4 = False
            for a in attr.split(" "):
                if joinb4:
                    vals.append(a)
                    if len(a)>1 and a.strip()[-1] == "\"":
                        val = " ".join(vals)
                        val = re.sub("^\"", "", val)
                        val = re.sub("\"$", "", val)
                        rtn.update({key: val})
                        vals = []
                        joinb4 = False
                else:
                    keys = a.split("=", 1)
                    key = keys[0]
                    if len(keys) == 1:
                        rtn.update({key: True})
                    else:
                        val = keys[1].strip()
                        if len(val)>1 and val[-1] == "\"" and val not in (" ", "\""):
                            val = re.sub("^\"", "", val)
                            val = re.sub("\"$", "", val)
                            rtn.update({key: val})
                        else:
                            vals.append(val)
                            joinb4 = True
            return rtn

        def __2list(html: str) -> list:
            import re
            rtn = []
            for o in html.split("<"):
                cont = o.split(">", 1)
                tags = cont[0].split(" ", 1)
                tag = tags[0].strip()
                obj = {}
                if tag == "":
                    continue
                if tag[0] == "!":
                    continue
                end = (tag[0] == "/")
                tag = re.sub("^/", "", tag)
                if tag not in self.valid_tag:
                    rtn[len(
                        rtn)-1].update({"_text": "{}{}{}".format(rtn[len(rtn)-1].get("_text", ""), "<", o)})
                    continue
                selfend = (tag in self.selfend_tag)
                # if tag=="link":
                #     print(selfend)
                obj.update({"_tag": tag})
                if len(tags) > 1:
                    attr = tags[1].strip()
                    if attr != "":
                        selfend = ((attr[-1] == "/")
                                   or (tag in self.selfend_tag))
                    attr = re.sub("/$", "", attr).strip()
                    if attr != "":
                        obj.update({"_attr": __getattr(attr)})
                if len(cont) > 1:
                    text = cont[1].strip()
                    for l in self.rmhtml:
                        text = re.sub(l, "", text)
                    if text != "":
                        obj.update({"_text": text})
                obj.update({"_end": end})
                obj.update({"_idx": len(rtn)})
                rtn.append(obj)
                if selfend:
                    tmp = obj.copy()
                    tmp.update({"_end": True})
                    tmp.update({"_idx": len(rtn)})
                    rtn.append({k: v for k, v in tmp.items()
                               if k in ("_tag", "_end", "_idx")})
            return rtn

        def __set_end(obj: list) -> list:
            rmlst = []
            for t in self.unique_tag:
                st = [r for r in obj if r.get("_tag") == t]
                end = [r for r in obj if r.get("_tag") == t and r.get("_end")]
                if end == []:
                    obj.append({"_tag": t, "_end": True})
            rtn = obj.copy()
            for t in self.unique_tag:
                lst = [r for r in rtn if r.get("_tag") == t]
                if len(lst) > 2:
                    lst = lst[1:]
                    lst = lst[:-1]
                    rmlst += [r.get("_idx") for r in lst]
            rtn = []
            for r in obj:
                if r.get("_idx") not in rmlst:
                    r.update({"_idx": len(rtn)})
                    rtn.append(r)
            for i, o in enumerate(rtn):
                if o.get("_end"):
                    continue
                tag = o.get("_tag")
                idx = o.get("_idx")
                cnt = 1
                for r in rtn:
                    if r.get("_tag") == tag and r.get("_idx") > idx:
                        if r.get("_end"):
                            cnt -= 1
                        else:
                            cnt += 1
                        if cnt == 0:
                            rtn[i].update({"_eidx": r.get("_idx")})
                            text = r.get("_text", "").strip()
                            if text != "":
                                rtn[i].update({"_text": text})
                            break
            return rtn

        def __set_level(obj: list) -> list:
            level = 0
            rtn = obj.copy()
            for i, o in enumerate(rtn):
                rtn[i].update({"_level": level})
                if i != 0:
                    if o.get("_end"):
                        level -= 1
                    else:
                        level += 1
                        rtn[i].update({"_level": level})
            return rtn

        rtn = __2list(html=html)
        rtn = __set_end(obj=rtn)

        rtn = __set_level(obj=rtn)
        self.obj = rtn
        return rtn
        pass

