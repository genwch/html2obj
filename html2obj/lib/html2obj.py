from abc import ABC
from .formathtml import *
from .hobj import *

class html2obj(ABC):
    fullxpath: list = []
    _obj: list = []

    def __init__(self, url: str = None):
        self.set_url(url=url)
        pass

    def set_url(self, url: str):
        if url != None:
            fh = formathtml(url)
            obj = self._obj = fh.obj
            self.build_fullxpath(obj=obj)
            self.set(obj=obj)
        return self._obj

    def getattr(self, name: str, default=None):
        try:
            rtn = self.__getattribute__(name)
        except:
            rtn = default
        return rtn

    def set(self, obj: list = [], level: int = 0, idx: tuple = ()) -> list:

        def __getobj(obj: list, level: int, idx: tuple) -> list:
            if idx == ():
                fidx = 0
                eidx = len(obj)-1
            else:
                fidx = idx[0]
                eidx = idx[1]
            return [o for o in obj if o.get("_level") == level and not(o.get("_end")) and o.get("_idx") >= fidx and o.get("_idx") <= eidx]
        obj = self._obj if obj == [] else obj
        rtn = []
        for r in __getobj(obj=obj, level=level, idx=idx):
            o = hobj(r)
            fidx = r.get("_idx")
            eidx = r.get("_eidx", None)
            if eidx != None:
                for c in self.set(obj=obj, level=level+1, idx=(fidx, eidx)):
                    o.addchild(c)
            rtn.append(o)
        for r in rtn:
            self.__setattr__(r._name, r)
            break
        return rtn

    def build_fullxpath(self, obj: list = []) -> list:
        obj = self._obj if obj == [] else obj
        cols = ("_tag", "_attr", "_xpath")
        rtn = []
        for o in obj:
            if o.get("_attr", {}) == {}:
                continue
            idx = o.get("_idx")
            level = o.get("_level")
            xpath = ["{}[*]".format(t.get("_tag")) for t in obj if t.get("_idx")
                     < idx and t.get("_eidx", -1) > idx and t.get("_level") < level]
            if xpath == []:
                continue
            o.update({"_xpath": "/".join(xpath)})
            rtn.append({k: v for k, v in o.items() if k in cols})
        self.fullxpath = rtn
        return rtn

    def get_xpath(self, xpath: str, obj=None)-> list:
        def __splitxp(xpath: str):
            import re
            txp=xpath.split("[", 1)
            xp=txp[0]
            idx="*"
            opt=[]
            attr=""
            attrval=""
            if len(txp)>1:
                opt=txp[1].split("]")[0].split("=", 1)
                if len(opt)==1:
                    idx=opt[0]
                else:
                    attr=opt[0]
                    attr=re.sub("^@", "", attr)
                    attrval=opt[1]
                    for l in ("^\"", "\"$", "^'", "'$"):
                        attrval=re.sub(l, "", attrval).strip()
            return xp, idx, attr, attrval

        def __get_obj(xp: str, obj: list, isfull: bool):
            rtn=[]
            xp, idx, attr, attrval = __splitxp(xp)
            if xp=="":
                return obj, isfull
            if isfull:
                if xp not in ("", "*"):
                    for o in obj:
                        t=o.getattr(xp, [])
                        if isinstance(t, list):
                            rtn+=t
                        else:
                            rtn.append(t)
                    if attr!="":
                        obj=rtn.copy()
                        rtn=[]
                        for o in obj:
                            for k, v in o.getattr("_attr", {}).items():
                                if k==attr and (attrval in v.split(" ") or attrval==v):
                                    rtn.append(o)
                    else:
                        if idx!="*":
                            idx=int(idx)-1
                            # print("get idx", xp, idx, len(rtn))
                            try:
                                rtn=[rtn[idx]]
                            except:
                                print("! not found")
            else:
                for o in self.fullxpath:
                    if xp!="*":
                        if xp!=o.get("_tag", ""):
                            continue
                    for k, v in o.get("_attr", {}).items():
                        if k==attr and attrval in v.split(" "):
                            xpath="/{}/{}[@{}=\"{}\"]".format(o.get("_xpath", ""), xp, k, v)
                            rtn+=self.get_xpath(xpath)
            # print(xp, idx, attr, attrval, len(rtn))
            return rtn, True
        xpath=xpath.split("/")[1:]
        rtn=[self] if obj==None else obj.copy()
        isfull=True
        for i, xp in enumerate(xpath):
            if i==0 and xp=="":
                isfull=False
            rtn, isfull=__get_obj(xp, rtn, isfull)
            # print(i, xp, len(rtn))
            if rtn==[]:
                break
        return rtn

    def oget_xpath(self, xpath: str, obj=None) -> list:
        def is_integer(n):
            try:
                float(n)
            except ValueError:
                return False
            else:
                return float(n).is_integer()

        def __getxpath(xpath: str):
            import re
            xpath = xpath.split("[", 1)
            idx = 0
            attr = {}
            if len(xpath) == 1:
                xpath = xpath[0]
                return xpath, idx, attr
            opt = re.sub("]$", "", xpath[1]).strip()
            xpath = xpath[0]
            if xpath == "":
                return None, idx, attr
            if is_integer(opt):
                idx = int(opt)
            elif opt == "*":
                idx = -1
            else:
                attrs = opt.split("=", 1)
                key=attrs[0]
                key = re.sub("^@", "", key)
                tattr = attrs[1]
                for l in ("^\"", "\"$", "^'", "'$"):
                    tattr = re.sub(l, "", tattr)
                if len(attrs) > 1:
                    attr.update({key: tattr})
            return xpath, idx, attr

        def __getobj(obj, xp: str, attr: dict, fullpath: bool):
            nxp = ""
            rtn = None
            if attr!={}:
                for p in self.fullxpath:
                    nopt = ""
                    if xp != "*":
                        if xp != p.get("_tag"):
                            continue
                    attrs = p.get("_attr", {})
                    for k, v in attr.items():
                        aval=attrs.get(k, None)
                        if aval != None and v in aval.split(" "):
                            nxp = "/{}/{}[@{}]".format(p.get("_xpath"),
                                                    p.get("_tag"), f"{k}='{v}'")
                            if not(fullpath):
                                rtn = self.get_xpath(xpath=nxp)
                            else:
                                rtn = obj.getattr(p.get("_tag"), None)
                                # rtn = [o.getattr(p.get("_tag"), None) for o in obj]
            elif xp == "":
                pass
            else:
                rtn = [o.getattr(xp, None) for o in obj]
            return rtn

        rtn = []
        xpath = xpath.split("/")[1:]
        isfullpath = True

        obj = self if obj == None else obj
        for i, xp in enumerate(xpath):
            xp, idx, attr = __getxpath(xp)
            if i == 0 and xp == "":
                isfullpath = False
            if xp == "":
                continue
            obj = __getobj(obj, xp, attr, fullpath=isfullpath)
            if obj == None or obj == []:
                break
            if not(isinstance(obj, list)):
                obj=[obj]
            if i == len(xpath)-1:
                # print([o.get("_name") for o in obj])
                rtn = [o for o in obj]
            else:
                if idx == 0:
                    obj = obj
                elif idx>0:
                    obj = obj[idx-1]
                else:
                    txp = "/".join(xpath[i:])
                    rtn=[]
                    for o in obj:
                        tmp=self.get_xpath(xpath=txp, obj=o)
                        rtn+=tmp
                    break
                    # return rtn
                    # return [self.get_xpath(xpath=txp, obj=o)[0] for o in obj]
        return rtn

    def __str__(self):
        return str(self.__dict__)

