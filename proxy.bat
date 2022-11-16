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
if "%2" == "h" goto begin
:loop_start
set /p choice=    请选择：
IF NOT "%choice%"=="" SET choice=%choice:~0,1%
if /i "%choice%"=="S" goto set_start
if /i "%choice%"=="R" goto reset_start
if /i "%choice%"=="Q" goto endd
echo 选择无效，请重新输入
echo.
goto loop_start
::====================================================================================

:set_start
echo.
echo.
echo. 访问 https://github.com/MetaCubeX/Clash.Meta/releases/latest 地址下载最新版clash.meta内核文件
echo. 访问 https://release.dreamacro.workers.dev/latest/ 地址下载最新版clash.premium内核文件
echo.                      下载完记得解压文件至当前目录
echo.     运行界面  https://clash.razord.top 或者  https://yacd.haishan.me/
echo.
echo       ===========================================
echo             选择想要运行的clash内核
echo       ===========================================
echo.
echo             M.clash.meta内核
echo.
echo             P.clash.premium内核
echo.
echo.
echo.
:loop_clash
set /p clashchoice=    请选择：
IF NOT "%clashchoice%"=="" SET clashchoice=%clashchoice:~0,1%
if /i "%clashchoice%"=="M" (
    set "clashName=Clash.Meta-windows-amd64-compatible.exe"
    set "clashconfig=https://raw.gfile.ga/https://raw.githubusercontent.com/xintd/vpn/master/clash.meta"
    goto clash_start
)
if /i "%clashchoice%"=="P" (
    set "clashName=clash-windows-amd64.exe"
    set "clashconfig=https://raw.gfile.ga/https://raw.githubusercontent.com/xintd/vpn/master/clash.premium"
    goto clash_start
)
echo 选择无效，请重新输入
goto loop_clash
:clash_start
if not exist %clashName% (
    echo    %clashName%内核文件不存在,请先下载解压文件
    goto endd
)
echo 下载配置文件
setlocal enabledelayedexpansion
if exist %USERPROFILE%\.config\clash\config.yaml (
    set /p configfile=   "是否使用远程配置文件覆盖本地配置文件,meta内核切换premium必须使用远程配置文件覆盖（Y是，N否(默认)）："
    IF NOT "!configfile!"=="" SET configfile=!configfile:~0,1!
    if /i "!configfile!"=="Y" goto existYes
    goto existNo
) else (
    md "%USERPROFILE%\.config\clash"
)
:existYes
:: 使用powershell附带的curl命令
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f
powershell curl -o "%USERPROFILE%\.config\clash\config.yaml" "%clashconfig%"
:existNo
for /f "tokens=1,2,* " %%i in ('REG QUERY "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable ^| find /i "ProxyEnable"') do (set /A ProxyEnableValue=%%k)
if NOT %ProxyEnableValue% equ 0 goto clash
echo 关闭自动检测设置
REM reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v DefaultConnectionSettings /t REG_BINARY /d 46000000030000000100 /f

echo 正在设置代理服务器……
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "127.0.0.1:51168" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;172.32.*;192.168.*;<local>" /f

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
for /f "delims=" %%i in ('dir /b *clash*.exe') do taskkill /f /im %%i
mshta vbscript:createobject("wscript.shell").run("%~nx0 :: h",0)(window.close)&&exit
:begin
for /f "delims=" %%i in ('dir /b %clashName%') do %%i
goto endd
::====================================================================================

:reset_start
for /f "delims=" %%i in ('dir /b *clash*.exe') do taskkill /f /im %%i
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
echo *****设置成功！代理服务器设置已经清空
echo.
goto endd
::====================================================================================

:endd
taskkill /f /im conhost.exe
taskkill /f /im cmd.exe
pause