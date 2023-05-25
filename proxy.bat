@ECHO OFF &PUSHD %~DP0 &TITLE →      设置系统代理

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
if "%2" == "h" goto begin
echo       ===========================================
echo             请选择要进行的操作，然后按回车
echo       ===========================================
echo.
echo             S.设置系统代理
echo.
echo             R.恢复系统代理
echo.
echo             Q.退出
echo.
echo.
echo.
:loop_start
set /p choice=    请选择：
IF NOT "%choice%"=="" SET choice=%choice:~0,1%
if /i "%choice%"=="S" goto set_proxy
if /i "%choice%"=="R" goto reset_proxy
if /i "%choice%"=="Q" goto endd
echo 选择无效，请重新输入
echo.
goto loop_start
::====================================================================================

:set_proxy
echo.
echo.
echo.
echo       ===========================================
echo             选择想要运行的代理软件
echo       ===========================================
echo.
echo             M.clash.meta
echo.
rem echo             P.clash.premium
echo.
echo             W.WireGuard
echo.
echo.
echo.
:loop_clash
set /p clashchoice=    请选择：
IF NOT "%clashchoice%"=="" SET clashchoice=%clashchoice:~0,1%
if /i "%clashchoice%"=="M" (
    set "exeName=Clash.Meta-windows-amd64-compatible.exe"
    set "clashconfig=https://raw.gfile.ga/https://raw.githubusercontent.com/xintd/files/main/clash.meta"
    set "exeURL=https://github.com/MetaCubeX/Clash.Meta/releases/latest"
    goto clash_start
)
if /i "%clashchoice%"=="m" (
    set "exeName=clash-windows-amd64.exe"
    set "clashconfig=https://raw.gfile.ga/https://raw.githubusercontent.com/xintd/files/main/clash.premium"
    set "exeURL=https://release.dreamacro.workers.dev/latest/"
    goto clash_start
)
if /i "%clashchoice%"=="W" (
    set exeName="C:\Program Files\WireGuard\wireguard.exe"
    goto wireguard_start
)
echo 选择无效，请重新输入
goto loop_clash
::====================================================================================

:clash_start
if exist %exeName% goto clashBegin
echo.
echo.      %exeName%文件不存在,请先下载文件
echo.      访问%exeURL%地址下载最新文件
echo.      下载完记得解压文件至当前目录
echo.      运行界面  https://clash.razord.top 或者  https://yacd.haishan.me/
echo.
pause
goto clash_start
:clashBegin
echo 下载配置文件
setlocal enabledelayedexpansion
if exist %USERPROFILE%\.config\clash\config.yaml (
rem    set /p configfile=   "是否使用远程配置文件覆盖本地配置文件,meta内核切换premium必须使用远程配置文件覆盖（Y是，N否(默认)）："
    set /p configfile=   "是否使用远程配置文件覆盖本地配置文件（Y是，N否(默认)）："
    IF NOT "!configfile!"=="" SET configfile=!configfile:~0,1!
    if /i "!configfile!"=="Y" goto existYes
    goto existNo
) else (
    md "%USERPROFILE%\.config\clash"
)
:existYes
:: 使用powershell附带的curl命令
REM  reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f
powershell curl -o "%USERPROFILE%\.config\clash\config.yaml" "%clashconfig%"
:existNo
for /f "tokens=1,2,* " %%i in ('REG QUERY "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable ^| find /i "ProxyEnable"') do (set /A ProxyEnableValue=%%k)
if NOT %ProxyEnableValue% equ 0 goto clash
echo 关闭自动检测设置
REM reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v DefaultConnectionSettings /t REG_BINARY /d 46000000030000000100 /f

echo 正在设置代理服务器……
REM reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f
REM reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "127.0.0.1:8689" /f
REM reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;172.32.*;192.168.*;<local>" /f

rem “对于本地地址不使用代理服务器”这个勾，不会勾选上
::reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "11.*;68.*;10.*;" /f
rem “对于本地地址不使用代理服务器”这个勾，会勾选上 ,  值加了<local>
::reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "11.*;68.*;10.*;<local>" /f
echo.
echo *****设置成功！代理服务器设置完毕
echo.
::后台启动clash
rem if "%1" == "h" goto begin
:clash
for /f "delims=" %%i in ('dir /b *clash*.exe') do taskkill /f /im %%i>nul 2>nul 1>nul
mshta vbscript:createobject("wscript.shell").run("%~nx0 :: h %exeName%",0)(window.close)&&exit
:begin
%3
goto endd
::====================================================================================

:reset_proxy
for /f "delims=" %%i in ('dir /b *clash*.exe') do taskkill /f /im %%i>nul 2>nul 1>nul
for /f "tokens=1,2,* " %%i in ('REG QUERY "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable ^| find /i "ProxyEnable"') do (set /A ProxyEnableValue=%%k)
if %ProxyEnableValue% equ 0 goto end
echo 设置自动检测配置
REM reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v DefaultConnectionSettings /t REG_BINARY /d 46000000020000000900 /f

echo 正在清空代理服务器设置……
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "" /f

:end
echo.
echo *****设置成功！代理已经恢复
echo.
goto endd
::====================================================================================

:wireguard_start
if exist %exeName% goto wireguard_begin
echo.
echo.
echo. 访问 https://download.wireguard.com/windows-client/ 地址下载最新wireguard客户端安装
echo.
echo.
echo.
pause
if not exist %exeName% goto wireguard_start
:wireguard_begin
rem 判断是否开启Wireguard的Pre/Post命令支持，只能通过修改注册表的方式开启
REG QUERY HKLM\Software\WireGuard /v DangerousScriptExecution>nul 2>nul&&goto downloadBatFiles
reg add HKLM\Software\WireGuard /v DangerousScriptExecution /t REG_DWORD /d 1 /f
powershell (new-object Net.WebClient).DownloadFile('https://raw.gfile.ga/https://raw.githubusercontent.com/xintd/files/main/zero-profile.conf','C:\Program Files\WireGuard\zero-profile.conf')
:downloadBatFiles
if not exist "C:\Program Files\WireGuard\bat\config.yml" goto batfiles
set monthday=%date:~0,4%%date:~5,2%01
for %%i in ("C:\Program Files\WireGuard\bat\config.yml") do set fdate=%%~ti
set filedate=%fdate:~0,4%%fdate:~5,2%%fdate:~8,2%
if %filedate% geq %monthday% goto WireGuard
:batfiles
echo       ------https://github.com/lmc999/auto-add-routes
echo       ------下载国内外分流脚本
powershell (new-object Net.WebClient).DownloadFile('https://raw.gfile.ga/https://github.com/lmc999/auto-add-routes/raw/master/zip/wireguard.zip','wireguard.zip')
powershell Expand-Archive wireguard.zip .
powershell rm -r -force 'wireguard.zip'
echo       ------
echo       ------使用最新脚本
taskkill /f /im overture-windows-amd64.exe>nul 2>nul 1>nul
powershell rm -r -force 'C:\Program Files\WireGuard\bat'
powershell mv wireguard 'C:\Program Files\WireGuard\bat'
:WireGuard
echo       ------
echo       ------启动wireguard
%exeName%
::====================================================================================

:endd
REM get cmd pid
set TempFile=%TEMP%\sthUnique.tmp
wmic process where (Name="wmic.exe" AND CommandLine LIKE "%%%TIME%%%") get ParentProcessId /value | find "ParentProcessId" >%TempFile%
set /P _string=<%TempFile%
set pid=%_string:~16%
taskkill /f /FI "USERNAME eq %username%" /FI "PID ne %pid%" /im cmd.exe>nul 2>nul 1>nul
pause
exit