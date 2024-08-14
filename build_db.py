from src.utils import load_json
from tinydb import TinyDB
import os

db_path = './db.json'
if os.path.exists(db_path):
    print("del db")
    os.remove(db_path)
db = TinyDB(db_path)

material = db.table('material')
for id,data in load_json("./data/药材.json").items():
    name = data["name"]
    level = data["level"]
    material.insert({'name': f"{name}({level[:2]})", 'level': level,
               'main_temp': data["主药"]["h_a_c"]["type"]*data["主药"]["h_a_c"]["power"],
               'main_func_t': data["主药"]["type"],
               'main_func_p': data["主药"]["power"],
               'phar_temp': data["药引"]["h_a_c"]["type"]*data["药引"]["h_a_c"]["power"],
               'auxi_func_t': data["辅药"]["type"],
               'auxi_func_p': data["主药"]["power"],
               })


medicine = db.table('medicine')
for id,data in load_json("./data/炼丹丹药.json").items():
    name = data["name"]
    desc = data["desc"]

    if "点修为" in desc:
        type = "增加修为"
    elif "概率提升" in desc:
        type = "突破概率"
    elif "点攻击力" in desc:
        type = "加攻击力"
    else:
        print(desc)
        type = "???"

    if type == "突破概率":
        state_f = data["境界"][0:3]
        t = desc.split("，")[1]
        state_t = t[2:5]
        name = name + f"({state_f}->{state_t})"
    elif type == "增加修为":
        num = desc[7:-4]
        name = name + f"(修{num})"
    elif type == "加攻击力":
        num = desc[9:-5]
        name = name + f"(攻{num})"

    elixir_config = data["elixir_config"]
    l0 = []
    for key,i in elixir_config.items():
        l0.append((int(key),i))
    medicine.insert(
        {
            "name":name,
            "type":type,
            "func1_type":l0[0][0],
            "func1_power":l0[0][1],
            "func2_type": l0[1][0],
            "func2_power": l0[1][1]
        }
    )