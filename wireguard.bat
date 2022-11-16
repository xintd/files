@ECHO OFF &PUSHD %~DP0 &TITLE →      启动wireguard
rem  判断是否管理员运行
net.exe session 1>NUL 2>NUL && (
    goto as_admin
) || (
    goto not_admin
)
:not_admin
rem   以下命令可令bat以管理员方式运行
%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c ""%~s0"" ::","","runas",1)(window.close)&&exit
:as_admin
if  not %date:~8,2% equ 01 goto exit
echo       ------
echo       ------
echo       ------
echo       ------
echo       ------
echo       ------下载国内外分流脚本
powershell (new-object Net.WebClient).DownloadFile('https://raw.gfile.ga/https://github.com/lmc999/auto-add-routes/raw/master/zip/wireguard.zip','wireguard.zip')
powershell Expand-Archive wireguard.zip .
powershell rm -r -force 'wireguard.zip'
echo       ------
echo       ------
echo       ------脚本替换旧的
taskkill /f /im overture-windows-amd64.exe
powershell rm -r -force 'C:\Program Files\WireGuard\bat'
powershell mv wireguard 'C:\Program Files\WireGuard\bat'
echo       ------
echo       ------
echo       ------重新启动wireguard
cd C:\Program Files\WireGuard
taskkill /f /im wireguard.exe
wireguard.exe
:exit
pause