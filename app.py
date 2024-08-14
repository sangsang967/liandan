import gradio as gr
from src.check_backpack import sort_yaocai
from src.gr_func import init,get_medicines,get_first_material,get_second_material,get_possible_material,get_basename

medicine_list_init = init()

def medicine_select_acc_change_b(medicine_select_acc):
    medicine_list = get_medicines(medicine_select_acc)
    return gr.Dropdown.update(choices=["无"]+medicine_list,value=medicine_list[0])

def check_backpack(text,medicine_select,material_num):
    yaocai_list = sort_yaocai(text,medicine_select,material_num)
    rtn = [[] for _ in range(9)]
    for name,grade,num,flag in yaocai_list:
        rtn[grade-1].append((f"{name}*{num}",flag))
    rtn = list(map(lambda x:gr.HighlightedText.update(value=x,visible=len(x)!=0),rtn))
    return rtn[-1],rtn[-2],rtn[-3],rtn[-4],rtn[-5],rtn[-6],rtn[-7],rtn[-8],rtn[-9]

def medicine_select_acc_change(medicine_select_acc):
    medicine_list = get_medicines(medicine_select_acc)
    return gr.Dropdown.update(choices=medicine_list,value=medicine_list[0])

def run_btn_click(medicine_select,material_1_select,material_2_select):
    rtn = medicine_select+"\n"
    possible_material_list = get_possible_material(medicine_select,material_1_select,material_2_select)
    if len(possible_material_list) == 1:
        main_material, auxi_material, material_third_list = possible_material_list[0]
        rtn += f"""###
- **主药**:{main_material}
- **辅药**:{auxi_material}
"""
        peifang = f"配方：主药{get_basename(main_material)}药引{get_basename(material_third_list[0])}辅药{get_basename(auxi_material)}丹炉寒铁铸心炉"
        return rtn,gr.Radio.update(choices=material_third_list,value=material_third_list[0],visible=True),gr.Markdown.update(visible=True,value=peifang),(main_material,auxi_material)
    # else:

    for index,(main_material,auxi_material,material_third_list) in enumerate(possible_material_list):
        rtn += f"""### 选择{index+1}
- **主药**:{main_material}
- **药引**:{",".join(material_third_list)}
- **辅药**:{auxi_material}
"""
    return rtn,gr.Radio.update(visible=False),gr.Markdown.update(visible=False,value=""),(main_material,auxi_material)

def medicine_select_change(medicine_select):
    a = get_first_material(medicine_select)
    return gr.Dropdown.update(choices=["无"]+a,value="无",visible=True),gr.Dropdown.update(visible=True,value="ALL"),gr.Number.update(visible=True,value=16)

def material_1_grade_select_change(medicine_select,material_1_grade_select,material_1_num):
    a = get_first_material(medicine_select,material_1_grade_select,material_1_num)
    return gr.Dropdown.update(choices=["无"]+a, value="无", visible=True)

def material_1_select_change(medicine_select,material_1_select):
    if material_1_select!="无":
        a = get_second_material(medicine_select,material_1_select)
        return gr.Dropdown.update(choices=["无"] + a, value="无", visible=True), gr.Dropdown.update(visible=True,value="ALL"), gr.Number.update(visible=True, value=16)
    else:
        return gr.Dropdown.update(choices=["无"], value="无", visible=False), gr.Dropdown.update(visible=False,value="ALL"), gr.Number.update(visible=False, value=16)


def material_2_grade_select_change(medicine_select,material_1_select,material_2_grade_select,material_2_num):
    a = get_second_material(medicine_select,material_1_select,material_2_grade_select,material_2_num)
    return gr.Dropdown.update(choices=["无"]+a, value="无", visible=True)

def output_Radio_change(output_state,output_Radio):
    main_material, auxi_material = output_state
    return f"配方：主药{get_basename(main_material)}药引{get_basename(output_Radio)}辅药{get_basename(auxi_material)}丹炉寒铁铸心炉"

with gr.Blocks() as demo:
    with gr.Tab("丹药配方"):
        gr.Markdown("选择你要炼制的丹药")
        with gr.Row():
            with gr.Column():
                with gr.Accordion("丹药限制",open=False):
                    medicine_select_acc = gr.Radio(["ALL","回复状态", "突破概率", "加攻击力"],value="ALL",show_label=False)
                medicine_select = gr.Dropdown(choices=medicine_list_init,value=medicine_list_init[0],label="丹药选择")

                with gr.Row():
                    material_1_grade_select = gr.Dropdown(choices=["ALL"]+[f"{i}品药材" for i in "一二三四五六七八九"],value="ALL",visible=False,label="药材等级")
                    material_1_num = gr.Number(value=16,label="最大数量",visible=False)
                    material_1_select = gr.Dropdown(visible=False,label="第一个药材")

                with gr.Row():
                    material_2_grade_select = gr.Dropdown(choices=["ALL"]+[f"{i}品药材" for i in "一二三四五六七八九"],value="ALL",visible=False,label="药材等级")
                    material_2_num = gr.Number(value=16,label="最大数量",visible=False)
                    material_2_select = gr.Dropdown(visible=False,label="第二个药材")

                run_btn = gr.Button("Run")
            with gr.Column():
                output_mk = gr.Markdown("输出结果")
                with gr.Blocks():
                    output_Radio = gr.Radio(visible=False,label="药引")
                    output_state = gr.State((None,None))
                    output_end = gr.Markdown(visible=False)

    with gr.Tab("背包查询"):
        gr.Markdown("复制全部药材到左边文本框")
        with gr.Row():
            with gr.Column():
                with gr.Accordion("丹药限制", open=False):
                    medicine_select_acc_b = gr.Radio(["ALL", "回复状态", "突破概率", "加攻击力"], value="ALL",
                                                     show_label=False)
                    with gr.Row():
                        medicine_select_b = gr.Dropdown(choices=["无"] + medicine_list_init, value="无",
                                                        label="丹药选择")
                        material_num_b = gr.Number(value=16, label="最大数量")
                inp_b = gr.Text(label="药材", lines=10)
                run_btn_b = gr.Button("run")
            with gr.Column():
                gr.Markdown("标注颜色的为炼制丹药需要材料，绿色为数量满足，黄色为缺少")
                out_l = [
                    gr.HighlightedText(label=f"{i}品药材", visible=False).style(color_map={"-": "yellow", "+": "green"})
                    for i in "九八七六五四三二一"]

    medicine_select_acc.change(fn=medicine_select_acc_change, inputs=[medicine_select_acc], outputs=[medicine_select])
    medicine_select.change(fn=medicine_select_change,inputs=[medicine_select],outputs=[material_1_select,material_1_grade_select,material_1_num])

    material_1_grade_select.change(fn=material_1_grade_select_change,inputs=[medicine_select,material_1_grade_select,material_1_num],outputs=[material_1_select])
    material_1_num.change(fn=material_1_grade_select_change,inputs=[medicine_select,material_1_grade_select,material_1_num],outputs=[material_1_select])

    material_1_select.change(fn=material_1_select_change,inputs=[medicine_select,material_1_select],outputs=[material_2_select,material_2_grade_select,material_2_num])

    material_2_grade_select.change(fn=material_2_grade_select_change,inputs=[medicine_select, material_1_select, material_2_grade_select, material_2_num],outputs=[material_2_select])
    material_2_num.change(fn=material_2_grade_select_change,inputs=[medicine_select, material_1_select, material_2_grade_select, material_2_num],outputs=[material_2_select])

    run_btn.click(fn=run_btn_click,inputs=[medicine_select,material_1_select,material_2_select],outputs=[output_mk,output_Radio,output_end,output_state])

    output_Radio.change(fn=output_Radio_change,inputs=[output_state,output_Radio],outputs=[output_end])

    # 背包
    medicine_select_acc_b.change(fn=medicine_select_acc_change_b, inputs=[medicine_select_acc_b],
                                 outputs=[medicine_select_b])

    run_btn_b.click(fn=check_backpack, inputs=[inp_b, medicine_select_b, material_num_b], outputs=out_l)

demo.launch()
