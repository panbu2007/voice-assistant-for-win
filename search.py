import winreg
import os
def search_app_name():
    sub_key = [r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths', r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall', r'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall']
    
    software_name = []
    software_path = []
    for i in sub_key:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, i, 0, winreg.KEY_READ)
        for j in range(0, winreg.QueryInfoKey(key)[0]-1):
            try:
                key_name = winreg.EnumKey(key, j)
                key_path = i + '\\' + key_name
                each_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
                DisplayName, REG_SZ = winreg.QueryValueEx(each_key, 'DisplayName')
                DisplayPath = winreg.QueryValueEx(each_key, "DisplayIcon")[0].split(',')[0].strip().strip('"').strip()
                name = DisplayPath.split('\\')[-1]

                if 'exe' in name and (not 'uni' in name.lower() or 'unity' in name.lower()):
                        software_path.append(DisplayPath)
                        software_name.append(DisplayName)
                else:
                    path = DisplayPath[:DisplayPath.index(name)]
                    for dir in os.listdir(path):
                        if key_name.lower() + '.exe' == dir.lower():
                            software_path.append(path + dir)
                            software_name.append(DisplayName)
            except WindowsError:
                pass
    return software_name, software_path

