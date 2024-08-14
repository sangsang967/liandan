from tinydb import TinyDB, Query

db = TinyDB('./db.json')
material_table = db.table('material')
medicine_table = db.table('medicine')



def get_medicines(type="ALL"):
    assert type in ["ALL", "回复状态", "突破概率", "加攻击力"], f"type:{type} 不是有效的类别"
    if type in ["ALL"]:
        a = medicine_table.all()
    else:
        medicine = Query()
        a = medicine_table.search(medicine.type == type)
    return list(map(lambda x: x["name"], a))


def _get_medicine_elixir_config(medicine_select: str):
    medicine = Query()
    return medicine_table.search(medicine.name == medicine_select)[0]

def _get_material_elixir_config(material_select: str):
    medicine = Query()
    return material_table.search(medicine.name == material_select)[0]

def get_first_material(medicine_select, medicine_level_select="ALL",material_max_num=16) ->list:
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
    rtn = list(map(lambda x: f"{x[0]}*{x[1]}", rtn))
    return rtn

def get_second_material(medicine_select, first_material:str, medicine_level_select="ALL",material_max_num=16) ->list:
    m = _get_medicine_elixir_config(medicine_select)
    first_material_name, _ = first_material.split("*")
    first_material = _get_material_elixir_config(first_material_name)
    func1_type = m["func1_type"]
    func1_power = m["func1_power"]
    func2_type = m["func2_type"]
    func2_power = m["func2_power"]

    if first_material["main_func_t"] == func1_type:
        second_material_func_need,second_material_main = (func2_type,func2_power),False
    elif first_material["auxi_func_t"] == func1_type:
        second_material_func_need, second_material_main = (func2_type,func2_power), True
    elif first_material["main_func_t"] == func2_type:
        second_material_func_need, second_material_main = (func1_type,func1_power), False
    elif first_material["auxi_func_t"] == func2_type:
        second_material_func_need, second_material_main = (func1_type,func1_power), True

    material = Query()
    material_t = material.main_func_t if second_material_main else material.auxi_func_t
    if medicine_level_select == "ALL":
        a = material_table.search((material_t == second_material_func_need[0]))
    else:
        a = material_table.search((material.level == medicine_level_select) & (material_t == second_material_func_need[0]))

    def get_num(material0):
        name = material0["name"]
        material0_p = material0["main_func_p"] if second_material_main else material0["auxi_func_p"]
        num = second_material_func_need[1]/material0_p
        num = int(num) + 1 if num > int(num) else int(num)
        return (name,num)

    rtn = list(map(get_num, a))
    rtn = list(filter(lambda x:x[1]<=material_max_num, rtn))
    rtn = list(map(lambda x: f"{x[0]}*{x[1]}", rtn))
    return rtn

def get_possible_material(medicine_select, first_material:str="无", second_material:str="无",material_max_num=100):
    possible_choice = set()
    if first_material == "无":
        for first_material in get_first_material(medicine_select):
            for second_material in get_second_material(medicine_select, first_material):
                possible_choice.add((first_material, second_material))
    elif second_material == "无":
        for second_material in get_second_material(medicine_select,first_material):
            possible_choice.add((first_material, second_material))
    else:
        possible_choice.add((first_material,second_material))

    m = _get_medicine_elixir_config(medicine_select)
    func1_type = m["func1_type"]
    func2_type = m["func2_type"]

    rtn = []
    for first_material,second_material in possible_choice:
        first_material_name,first_material_num = first_material.split("*")
        second_material_name,second_material_num = second_material.split("*")
        first_material = _get_material_elixir_config(first_material_name)
        second_material = _get_material_elixir_config(second_material_name)
        if first_material["main_func_t"] in [func1_type,func2_type]:
            main_temp = first_material["main_temp"] * int(first_material_num)
            main_material = f"{first_material_name}*{first_material_num}"
            auxi_material = f"{second_material_name}*{second_material_num}"
        else:
            main_temp = second_material["main_temp"] * int(second_material_num)
            auxi_material = f"{first_material_name}*{first_material_num}"
            main_material = f"{second_material_name}*{second_material_num}"

        if main_temp==0:
            material_third_list=['恒心草(一品)*1', '红绫草(一品)*1', '五柳根(二品)*1', '天元果(二品)*1', '紫猴花(三品)*1', '九叶芝(三品)*1', '血莲精(四品)*1', '鸡冠草(四品)*1', '地心火芝(五品)*1', '天蝉灵叶(五品)*1', '三叶青芝(六品)*1', '七彩月兰(六品)*1', '地心淬灵乳(七品)*1', '天麻翡石精(七品)*1', '木灵三针花(八品)*1', '鎏鑫天晶草(八品)*1', '离火梧桐芝(九品)*1', '尘磊岩麟果(九品)*1', '宁心草(一品)*1', '凝血草(一品)*1', '流莹草(二品)*1', '蛇涎果(二品)*1', '轻灵草(三品)*1', '龙葵(三品)*1', '菩提花(四品)*1', '乌稠木(四品)*1', '天灵果(五品)*1', '灯心草(五品)*1', '白沉脂(六品)*1', '苦曼藤(六品)*1', '天问花(七品)*1', '渊血冥花(七品)*1', '阴阳黄泉花(八品)*1', '厉魂血珀(八品)*1', '太乙碧莹花(九品)*1', '森檀木(九品)*1', '地黄参(一品)*1', '火精枣(一品)*1', '风灵花(二品)*1', '伏龙参(二品)*1', '枫香脂(三品)*1', '炼魂珠(三品)*1', '石龙芮(四品)*1', '锦地罗(四品)*1', '伴妖草(五品)*1', '剑心竹(五品)*1', '混元果(六品)*1', '皇龙花(六品)*1', '血玉竹(七品)*1', '肠蚀草(七品)*1', '狼桃(八品)*1', '霸王花(八品)*1', '地龙干(九品)*1', '龙须藤(九品)*1']

        else:
            material0 = Query()
            material0 = material0.phar_temp > 0 if main_temp<0 else material0.phar_temp <0
            a = material_table.search(material0)

            def get_num(x):
                name = x["name"]
                phar_temp = x["phar_temp"]
                num = -main_temp/phar_temp
                if not num.is_integer():
                    num = 9999999
                # num = 1 if num==0 else num
                return (name,int(num))

            a = list(map(get_num,a))
            a = list(filter(lambda x:x[1]<=material_max_num, a))
            material_third_list = list(map(lambda x:f'{x[0]}*{x[1]}',a))
        rtn.append((main_material,auxi_material,material_third_list))
    return rtn

def get_basename(text):
    name,num = text.split("*")
    return name[:-4]+num


def init():
    medicine_list = get_medicines()
    return medicine_list
