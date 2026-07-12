# 创建桌面快捷方式（带图标）
# 运行此脚本会创建一个带图标的桌面快捷方式

$WshShell = New-Object -comObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $Desktop "取证AI平台.lnk"
$TargetPath = Join-Path $PSScriptRoot "start.bat"

# 创建快捷方式
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "取证AI平台 - 基于大模型的自动化取证系统"
$Shortcut.WindowStyle = 1  # 正常窗口

# 尝试设置图标（如果有ico文件）
$IconPath = Join-Path $PSScriptRoot "icon.ico"
if (Test-Path $IconPath) {
    $Shortcut.IconLocation = $IconPath
} else {
    # 使用系统默认图标
    $Shortcut.IconLocation = "shell32.dll,117"
}

$Shortcut.Save()

Write-Host "✅ 桌面快捷方式已创建: $ShortcutPath"
Write-Host ""
Write-Host "如需自定义图标，请将 icon.ico 文件放到项目目录，然后重新运行此脚本"
Write-Host ""
pause
