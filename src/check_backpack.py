import re
from tinydb import TinyDB, Query
from src.gr_func import _get_medicine_elixir_config,material_table


def get_need_material(medicine_select, medicine_level_select="ALL",material_max_num=16) ->list:
    material = Query()
    m = _get_medicine_elixir_config(medicine_select)
    func1_type = m["func1_type"]
    func1_power = m["func1_power"]
    func2_type = m["func2_type"]
    func2_power = m["func2_power"]
    if medicine_level_select == "ALL":
        a = material_table.search((material.main_func_t == func1_type) | (material.auxi_func_t == func1_type) | (
                    material.main_func_t == func2_type) | (material.auxi_func_t == func2_type))
    else:
        a = material_table.search((material.level == medicine_level_select) & (
                    (material.main_func_t == func1_type) | (material.auxi_func_t == func1_type) | (
                        material.main_func_t == func2_type) | (material.auxi_func_t == func2_type)))

    def get_num(material0):
        global material_second_f
        name = material0["name"]
        if material0["main_func_t"] == func1_type:
            material_second_f = (func2_type,False)
            num = func1_power / material0["main_func_p"]
        elif material0["auxi_func_t"] == func1_type:
            material_second_f = (func2_type,True)
            num = func1_power / material0["auxi_func_p"]
        elif material0["main_func_t"] == func2_type:
            material_second_f = (func1_type,False)
            num = func2_power / material0["main_func_p"]
        elif material0["auxi_func_t"] == func2_type:
            material_second_f = (func1_type,True)
            num = func2_power / material0["auxi_func_p"]
        num = int(num) + 1 if num > int(num) else int(num)
        return (name,num,material_second_f)
    rtn = list(map(get_num, a))
    rtn = list(filter(lambda x:x[1]<=material_max_num, rtn))

    def check_material(material0):
        if material0[1] > material_max_num:
            return False
        material_t = material.main_func_t if material0[2][1] else material.auxi_func_t
        a = material_table.search(material_t == material0[2][0])
        if a == []:
            return False
        return True

    rtn = list(filter(check_material, rtn))
    rtn = list(map(lambda x: (x[0],x[1]), rtn))
    return rtn

grade_str = "一二三四五六七八九"

def sort_yaocai(text,medicine_select,material_num):
    material_need_dict = {}
    if medicine_select != "无":
        material_need_list = get_need_material(medicine_select,material_max_num=material_num)
        for name,num in material_need_list:
            material_need_dict[name[:-4]] = num
        print(material_need_dict)
    regex = re.compile("名字：.+\n品级：.+\n.+\n.+\n拥有数量：\d+")
    yaocai_l = regex.findall(text)
    rtn = []
    for yaocai in yaocai_l:
        yaocai = yaocai.split("\n")
        name = yaocai[0][3:]
        num = int(yaocai[-1][5:])
        grade = grade_str.index(yaocai[1][3])+1

        flag = material_need_dict.get(name)
        if flag is not None:
            if num >= flag:
                flag = "+"
            else:
                num = f"{num}({flag})"
                flag = "-"
        rtn.append((name,grade,num,flag))
    return rtn
