import json
from typing import Optional,List,Dict

class Dict2Obj(dict):
    def __getattr__(self, key):
        if key not in self:
            return None
        else:
            value = self[key]
            if isinstance(value,dict):
                value = Dict2Obj(value)
            return value

def load_json(file_path:str) ->Dict2Obj:
    with open(file_path,"r",encoding="utf-8")as f:
        return Dict2Obj(json.loads(f.read()))


other_data = load_json("./data/other.json")


