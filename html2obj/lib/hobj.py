from abc import ABC

class hobj(ABC):
    cols: tuple = ("_attr", "_text", "_i")

    def __init__(self, rec: dict):
        for k, v in rec.items():
            if k == "_tag":
                self.__setattr__("_name", v)
            elif k in self.cols:
                self.__setattr__(k, v)
            else:
                continue
        pass

    def get(self, name: str, default=None):
        return self.getattr(name=name, default=default)

    def getattr(self, name: str, default=None):
        try:
            rtn = self.__getattribute__(name)
        except:
            rtn = default
        return rtn

    def append(self, name, val, forcelist: bool = True):
        if val == None:
            return
        vals = self.getattr(name, [])
        if not(isinstance(vals, list)):
            vals = [vals]
        # if name !="_elem":
        #     val.__setattr__("_i",len(vals)+1)
        vals.append(val)
        if forcelist:
            vals = list(set(vals))
        if vals != []:
            if not(forcelist):
                if len(vals) == 1:
                    vals = vals[0]
            self.__setattr__(name, vals)

    def concat(self, name, val):
        vals = self.getattr(name, "")
        if isinstance(val, list):
            vals += " ".join(val)
        else:
            vals += " "+val
        if vals != "":
            self.__setattr__(name, vals.strip())

    def addchild(self, child):
        ctag = child._name
        self.append(name="_elem", val=ctag)
        self.append(name=ctag, val=child, forcelist=False)
        if ctag=="script":
            return
        try:
            self.concat(name="_text", val=child._text)
        except:
            pass

    def __repr__(self):
        return str(self.__dict__)

