import os
import shutil
import subprocess

desktop = r"C:\Users\brred\Desktop"
backend = r"c:\Users\brred\Desktop\AI_Assistant\App\backend"
bot_script = os.path.join(backend, "UPSC_ESE_Bot.py")
bat_src = os.path.join(backend, "Start_UPSC_ESE_Bot.bat")
bat_dst = os.path.join(desktop, "Start_UPSC_ESE_Bot.bat")
lnk_path = os.path.join(desktop, "UPSC ESE Local Hub.lnk")

# 1. Copy updated .bat file
shutil.copyfile(bat_src, bat_dst)

# 2. Create real Windows .lnk shortcut pointing to signed C:\Python313\pythonw.exe
ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{lnk_path}')
$Shortcut.TargetPath = 'C:\\Python313\\pythonw.exe'
$Shortcut.Arguments = '"{bot_script}"'
$Shortcut.WorkingDirectory = '{backend}'
$Shortcut.Description = 'UPSC ESE (Mechanical Engineering) Local AI Hub'
$Shortcut.Save()
"""
subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)

# 3. Launch the bot window right now
subprocess.Popen([r"C:\Python313\pythonw.exe", bot_script], cwd=backend)
print("Shortcut created and UPSC ESE Bot launched!")
