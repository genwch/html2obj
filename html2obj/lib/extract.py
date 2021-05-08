from abc import ABC
from .html2obj import *
import re


class extract(ABC):
    def __init__(self):
        pass

    def extract(self, conf, showexec: bool = False) -> list:
        def __extr(conf, obj: list = []):
            rtn = []
            obj = [conf] if obj == [] else obj
            for o in obj:
                c = self.conv_conf(conf, o)
                rtn += self.extract_data(c)
            return rtn
        import timeit
        conf = conf if isinstance(conf, list) else [conf]
        obj = []
        for i, c in enumerate(conf):
            starttime = timeit.default_timer()
            obj = __extr(c, obj)
            if showexec:
                print(
                    f"{i}:\tcnt: {len(obj)}\ttime - {timeit.default_timer() - starttime}")
        return obj

    def extract_data(self, conf: str):
        obj = html2obj(url=conf.get("url"))
        items = obj.get_xpath(xpath=conf.get("items"))
        data = []
        for i in items:
            dt = {}
            skip = False
            for k, v in conf.get("data", {}).items():
                val = None
                if isinstance(v, dict):
                    for tk, tv in v.items():
                        if tk == "_act":
                            continue
                        elif tk == "get":
                            val = i
                        elif tk == "fix":
                            val = v
                            tv = tk
                        else:
                            val = i.get(tk, {})
                        if val != None:
                            val = val.get(tv, None)
                else:
                    val = i.get(v, None)
                if val != None:
                    act = conf.get("data", {}).get(k, {}).get("_act", [])
                    for a in act:
                        for tk, tv in a.items():
                            if tk == "re":
                                fm = tv
                                to = ""
                                if isinstance(tv, dict):
                                    for fm, to in tv.items():
                                        break
                                # print(val, fm)
                                val = re.sub(fm, to, val)
                            elif tk == "split":
                                sp = " "
                                cnt = 0
                                if isinstance(tv, dict):
                                    for sp, cnt in tv.items():
                                        break
                                # print(val, sp, cnt)
                                val = val.split(sp)[cnt]
                            elif tk == "check":
                                for fn, rst in tv.items():
                                    break
                                if fn == "type":
                                    if rst == "int":
                                        try:
                                            tmp = int(val)
                                        except:
                                            skip = True
                                elif fn == "notin":
                                    skip = (val in rst)
                            elif tk == "conv_json":
                                import json
                                val = json.loads(val)
                            elif tk == "pfx":
                                val = f"{tv}{val}"
                    dt.update({k: val})
            if not(skip) and dt != {}:
                data.append(dt)
        return data

    def conv_conf(self, conf: dict, org_conf: dict = {}) -> dict:
        def __nestget(conf: dict, key: str, default: str = "") -> str:
            rtn = None
            for k, v in conf.items():
                if k == key:
                    rtn = conf.get(k, default)
                    break
                else:
                    if isinstance(v, dict):
                        rtn = __nestget(v, key, default)
                        if rtn != None:
                            break
            return rtn

        org_conf = conf if org_conf == {} else org_conf
        rtn = conf.copy()
        for k, v in conf.items():
            if isinstance(v, dict):
                v = self.conv_conf(v, org_conf)
            elif isinstance(v, list):
                v = [self.conv_conf(o, org_conf) for o in v]
            elif isinstance(v, str):
                if v != None:
                    key = v.split("}}")[:-1]
                    # print(v, key)
                    for ttk in key:
                        tttk = ttk.split("{{", 1)
                        if len(tttk) == 1:
                            continue
                        tttk = tttk[1]
                        v = re.sub("{{%s}}" % (tttk), __nestget(
                            org_conf, tttk, ""), v)
            rtn.update({k: v})
        return rtn