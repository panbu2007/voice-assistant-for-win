import difflib
import wmi
import screen_brightness_control as sbc
import re

def extract_numbers(text):
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]

def light_judgement(text, score_line = 0.5):
    text = text.lower()
    increase_keywords = ["调高","增大","更亮","太暗了","亮点","brighter","more","too dark"]
    decrease_keywords = ["调低","减小","更暗","太亮了","暗点","darker","less","too dark"]
    volume_adjustment = ["亮度调节", "亮度到", "亮度设置", "亮度调整", "把亮度","调节为","adjust to", "set to", "change to", "turn to"]
    
    for keyword in increase_keywords:
        tmp_score = difflib.SequenceMatcher(None, text , keyword).ratio()
        print(tmp_score,"1")
        if tmp_score > score_line:
            return -1
    for keyword in decrease_keywords:
        tmp_score = difflib.SequenceMatcher(None, text , keyword).ratio()
        print(tmp_score,"2")
        if tmp_score > score_line:
            return -2
    for keyword in volume_adjustment:
        tmp_score = difflib.SequenceMatcher(None, text , keyword).ratio()
        print(tmp_score,"3")
        if tmp_score > score_line:
            number = extract_numbers(text)
            print("number=",number[0])
            try:
                if 0 <= int(number[0]) <= 100:
                    return number[0]
            except ValueError:
                print("ERROR:该亮度不存在！")
                pass
    return -3

def brightness_control(vis):
    c = wmi.WMI(namespace='wmi')
    methods = c.WmiMonitorBrightnessMethods()[0]
    current_brightness = sbc.get_brightness()
    present_brightness = current_brightness[0]
    print("当前亮度",present_brightness)
    
    x = light_judgement(vis)

    if x == -1:
        if present_brightness <= 80:
            methods.WmiSetBrightness(present_brightness + 20,0)
            print("亮度已调节到",present_brightness + 20)
        else: 
            methods.WmiSetBrightness(100,0)
            print("已经最亮了，注意合理用眼!")
    elif x == -2:
        if present_brightness >= 20:
            methods.WmiSetBrightness(present_brightness - 20 ,0)
            print("亮度已调节到",present_brightness - 20)
        else: 
            methods.WmiSetBrightness(0,0)
            print("看不见了!")
    elif x == -3:
        return
    else:
        methods.WmiSetBrightness(x,0)
        print("亮度已调节到",x)