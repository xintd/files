@ECHO OFF &PUSHD %~DP0 &TITLE ��      ����ϵͳ����

rem  �ж��Ƿ����Ա����
net.exe session 1>NUL 2>NUL && (
    goto as_admin
) || (
    goto not_admin
)
:not_admin
rem   �����������bat�Թ���Ա��ʽ����
%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c ""%~s0"" ::","","runas",1)(window.close)&&exit
:as_admin
echo       ===========================================
echo             ��ѡ��Ҫ���еĲ�����Ȼ�󰴻س�
echo       ===========================================
echo.
echo             S.����ϵͳ����
echo.
echo             R.�ָ�ϵͳ����
echo.
echo             Q.�˳�
echo.
echo.
echo.
if "%2" == "h" goto begin
:loop_start
set /p choice=    ��ѡ��
IF NOT "%choice%"=="" SET choice=%choice:~0,1%
if /i "%choice%"=="S" goto set_start
if /i "%choice%"=="R" goto reset_start
if /i "%choice%"=="Q" goto endd
echo ѡ����Ч������������
echo.
goto loop_start
::====================================================================================

:set_start
echo.
echo.
echo. ���� https://github.com/MetaCubeX/Clash.Meta/releases/latest ��ַ�������°�clash.meta�ں��ļ�
echo. ���� https://release.dreamacro.workers.dev/latest/ ��ַ�������°�clash.premium�ں��ļ�
echo.                      ������ǵý�ѹ�ļ�����ǰĿ¼
echo.     ���н���  https://clash.razord.top ����  https://yacd.haishan.me/
echo.
echo       ===========================================
echo             ѡ����Ҫ���е�clash�ں�
echo       ===========================================
echo.
echo             M.clash.meta�ں�
echo.
echo             P.clash.premium�ں�
echo.
echo.
echo.
:loop_clash
set /p clashchoice=    ��ѡ��
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
echo ѡ����Ч������������
goto loop_clash
:clash_start
if not exist %clashName% (
    echo    %clashName%�ں��ļ�������,�������ؽ�ѹ�ļ�
    goto endd
)
echo ���������ļ�
setlocal enabledelayedexpansion
if exist %USERPROFILE%\.config\clash\config.yaml (
    set /p configfile=   "�Ƿ�ʹ��Զ�������ļ����Ǳ��������ļ�,meta�ں��л�premium����ʹ��Զ�������ļ����ǣ�Y�ǣ�N��(Ĭ��)����"
    IF NOT "!configfile!"=="" SET configfile=!configfile:~0,1!
    if /i "!configfile!"=="Y" goto existYes
    goto existNo
) else (
    md "%USERPROFILE%\.config\clash"
)
:existYes
:: ʹ��powershell������curl����
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f
powershell curl -o "%USERPROFILE%\.config\clash\config.yaml" "%clashconfig%"
:existNo
for /f "tokens=1,2,* " %%i in ('REG QUERY "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable ^| find /i "ProxyEnable"') do (set /A ProxyEnableValue=%%k)
if NOT %ProxyEnableValue% equ 0 goto clash
echo �ر��Զ��������
REM reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v DefaultConnectionSettings /t REG_BINARY /d 46000000030000000100 /f

echo �������ô������������
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "127.0.0.1:51168" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;172.32.*;192.168.*;<local>" /f

rem �����ڱ��ص�ַ��ʹ�ô��������������������Ṵѡ��
::reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "11.*;68.*;10.*;" /f
rem �����ڱ��ص�ַ��ʹ�ô������������������Ṵѡ�� ,  ֵ����<local>
::reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "11.*;68.*;10.*;<local>" /f
echo.
echo *****���óɹ�������������������
echo.
::��̨����clash
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
echo �����Զ��������
REM reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v DefaultConnectionSettings /t REG_BINARY /d 46000000020000000900 /f

echo ������մ�����������á���
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "" /f
:end
echo.
echo *****���óɹ�����������������Ѿ����
echo.
goto endd
::====================================================================================

:endd
taskkill /f /im conhost.exe
taskkill /f /im cmd.exe
pause