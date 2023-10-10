from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import difflib

def volume_judgement(text, score_line = 0.5):
    text = text.lower()
    increase_keywords = ["增大音量", "调高音量", "提高音量", "调大声音", "加大声音", "响一点", "声音大一些", "音量大一些", "声音调大", "增加音量", "大声一点", "更响一些", "加大音量", "增加声音", "变大声音", "音量增加", "调高一点", "往大调", "turn up the volume", "increase the volume", "raise the volume"]
    decrease_keywords = ["减小音量", "调低音量", "降低音量", "调小声音", "减小声音", "声音小一些", "音量小一些", "声音调小", "降低音量", "小声一点", "声音变小", "音量减小", "调低一点", "往小调", "turn down the volume", "decrease the volume", "lower the volume"]
    volume_adjustment = ["调节音量到", "将音量调到", "设置音量为", "调整音量到", "把声音调到", "将音量设置为", "调整声音到", "把音量调到", "将声音调到", "把音量设置为", "调整音量为", "把声音调为", "将音量调为", "adjust the volume to", "set the volume to", "change the volume to", "adjust the sound to", "turn the volume to"]
    
    for keyword in increase_keywords:
        tmp_score = difflib.SequenceMatcher(None, text , keyword).ratio()
        if tmp_score > score_line:
            return -1
    for keyword in decrease_keywords:
        tmp_score = difflib.SequenceMatcher(None, text , keyword).ratio()
        if tmp_score > score_line:
            return -2
    for keyword in volume_adjustment:
        tmp_score = difflib.SequenceMatcher(None, text , keyword).ratio()
        if tmp_score > score_line:
            volume_string = ''
            flag = 0
            for t in text:
                if '0' <= t <= '9':
                    flag = 1
                    volume_string += t
                elif flag:      # 遇到非数字结束搜索
                    break
            volume = int(volume_string)
            return min(volume, 100)
    return -3


trans = {0: -65.25, 1: -56.99, 2: -51.67, 3: -47.74, 4: -44.62, 5: -42.03, 6: -39.82, 7: -37.89, 8: -36.17,
            9: -34.63, 10: -33.24, 11: -31.96, 12: -30.78, 13: -29.68, 14: -28.66, 15: -27.7, 16: -26.8, 17: -25.95, 18: -25.15, 19: -24.38,
            20: -23.65, 21: -22.96, 22: -22.3, 23: -21.66, 24: -21.05, 25: -20.46, 26: -19.9, 27: -19.35, 28: -18.82, 29: -18.32,
            30: -17.82, 31: -17.35, 32: -16.88, 33: -16.44, 34: -16.0, 35: -15.58, 36: -15.16, 37: -14.76, 38: -14.37, 39: -13.99,
            40: -13.62, 41: -13.26, 42: -12.9, 43: -12.56, 44: -12.22, 45: -11.89, 46: -11.56, 47: -11.24, 48: -10.93, 49: -10.63,
            50: -10.33, 51: -10.04, 52: -9.75, 53: -9.47, 54: -9.19, 55: -8.92, 56: -8.65, 57: -8.39, 58: -8.13, 59: -7.88,
            60: -7.63, 61: -7.38, 62: -7.14, 63: -6.9, 64: -6.67, 65: -6.44, 66: -6.21, 67: -5.99, 68: -5.76, 69: -5.55, 70: -5.33,
            71: -5.12, 72: -4.91, 73: -4.71, 74: -4.5, 75: -4.3, 76: -4.11, 77: -3.91, 78: -3.72, 79: -3.53, 80: -3.34,
            81: -3.15, 82: -2.97, 83: -2.79, 84: -2.61, 85: -2.43, 86: -2.26, 87: -2.09, 88: -1.91, 89: -1.75,
            90: -1.58, 91: -1.41, 92: -1.25, 93: -1.09, 94: -0.93, 95: -0.77, 96: -0.61, 97: -0.46, 98: -0.3, 99: -0.15, 100: 0.0}
def vol_transfer(volume): #整数转浮点数
    l, r = 0, 100
    while l + 1 < r:
        mid = l + (r - l) // 2
        vmid = trans[mid]
        if vmid > volume:
            r = mid
        elif vmid < volume:
            l = mid
        else:
            return mid
    if abs(trans[l] - volume) < abs(trans[r] - volume):
        return l
    return r

def volume_control(vis):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    vol_range = volume.GetVolumeRange()
    x = volume_judgement(vis)
    vol_now = volume.GetMasterVolumeLevel() # 获取当前的音量值
    print(vol_now)
    present_vol = vol_transfer(vol_now)
    print('当前音量:',present_vol)
    print(x)
    if x == -1:
        if present_vol <= 80:
            volume.SetMasterVolumeLevel(trans[present_vol + 20], None)
            return "音量已调节到" + str(present_vol + 20)
        else: 
            volume.SetMasterVolumeLevel(0.0, None)
            return "音量已满!"
    elif x == -2:
        if present_vol >= 20:
            volume.SetMasterVolumeLevel(trans[present_vol - 20], None)
            return "音量已调节到" + str(present_vol - 20)
        else: 
            volume.SetMasterVolumeLevel(-65.25, None)
            return "已经静音!"
    elif x == -3:
        return '音量调节失败'
    else:
        volume.SetMasterVolumeLevel(trans[x], None)
        return "音量已调节到" + str(x)
