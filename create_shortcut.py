"""Create desktop shortcut for L线 with custom icon."""
import os, subprocess

appdir = os.path.dirname(os.path.abspath(__file__))
desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
shortcut_path = os.path.join(desktop, 'L线.lnk')
launch_vbs = os.path.join(appdir, 'launch.vbs')
icon_ico = os.path.join(appdir, 'icon.ico')

ps_script = f'''
$s = (New-Object -ComObject WScript.Shell).CreateShortcut("{shortcut_path}")
$s.TargetPath = "wscript.exe"
$s.Arguments = "{launch_vbs}"
$s.WorkingDirectory = "{appdir}"
'''

if os.path.exists(icon_ico):
    ps_script += f'$s.IconLocation = "{icon_ico},0"\n'

ps_script += '''
$s.Save()
Write-Host "Desktop shortcut created!"
'''

tmp_ps = os.path.join(appdir, '_tmp.ps1')
with open(tmp_ps, 'w', encoding='utf-8-sig') as f:
    f.write(ps_script)

subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', tmp_ps])
os.remove(tmp_ps)
print(f'Shortcut: {shortcut_path}')
