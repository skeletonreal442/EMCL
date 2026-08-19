@echo off
chcp 65001 >nul
title EasyMCLauncher v1.1

set "BASE_DIR=C:\EMCL"
set "VERSIONS_DIR=%BASE_DIR%\versions"
set "PROFILES_FILE=%BASE_DIR%\launcher_profiles.json"
set "CONFIG_FILE=%BASE_DIR%\config.txt"

if not exist "%BASE_DIR%" mkdir "%BASE_DIR%"
if not exist "%VERSIONS_DIR%" mkdir "%VERSIONS_DIR%"
if not exist "%BASE_DIR%\mods" mkdir "%BASE_DIR%\mods"
if not exist "%BASE_DIR%\assets" mkdir "%BASE_DIR%\assets"
if not exist "%BASE_DIR%\libraries" mkdir "%BASE_DIR%\libraries"

if not exist "%PROFILES_FILE%" (
    echo {"profiles": {}} > "%PROFILES_FILE%"
)

set "NICKNAME=Player"
set "SELECTED_VERSION="

if exist "%CONFIG_FILE%" (
    for /f "tokens=1,* delims==" %%A in ('type "%CONFIG_FILE%"') do (
        if "%%A"=="NICKNAME" set "NICKNAME=%%B"
        if "%%A"=="SELECTED_VERSION" set "SELECTED_VERSION=%%B"
    )
)

:PRINT_HEADER
cls
echo.
echo  /$$$$$$$$ /$$      /$$  /$$$$$$  /$$      
echo ^| $$_____/^| $$$    /$$$ /$$__  $$^| $$      
echo ^| $$      ^| $$$$  /$$$$^| $$  \__/^| $$      
echo ^| $$$$$   ^| $$ $$/$$ $$^| $$      ^| $$      
echo ^| $$__/   ^| $$  $$$^| $$^| $$      ^| $$      
echo ^| $$      ^| $$\  $ ^| $$^| $$    $$^| $$      
echo ^| $$$$$$$$^| $$ \/  ^| $$^|  $$$$$$/^| $$$$$$$$
echo ^|________/^|__/     ^|__/ \______/^|________/
echo.
exit /b

:SAVE_CONFIG
echo NICKNAME=%NICKNAME%> "%CONFIG_FILE%"
echo SELECTED_VERSION=%SELECTED_VERSION%>> "%CONFIG_FILE%"
exit /b

:MAIN_MENU
call :PRINT_HEADER
echo =========================================================
echo   Директория: %BASE_DIR%
if "%SELECTED_VERSION%"=="" (
    echo   Выбранная версия: НЕ ВЫБРАНА
) else (
    echo   Выбранная версия: %SELECTED_VERSION%
)
echo   Никнейм: %NICKNAME%
echo =========================================================
echo   [1] Открыть папку EMCL
echo   [2] Выбрать версию игры
echo   [3] Изменить никнейм
echo   [4] ЗАПУСТИТЬ ИГРУ
echo =========================================================
echo.

set /p "CHOICE=Выберите действие: "

if "%CHOICE%"=="1" goto OPEN_EMCL
if "%CHOICE%"=="2" goto SELECT_VERSION
if "%CHOICE%"=="3" goto CHANGE_NICK
if "%CHOICE%"=="4" goto LAUNCH_GAME
goto MAIN_MENU

:OPEN_EMCL
call :PRINT_HEADER
start "" "%BASE_DIR%"
echo   [+] Папка открыта: %BASE_DIR%
echo   Возврат в главное меню...
timeout /t 1 >nul
goto MAIN_MENU

:SELECT_VERSION
call :PRINT_HEADER
echo   --- СПИСОК ВЕРСИЙ ---
set "COUNT=0"
for /f "delims=" %%I in ('dir /b /ad "%VERSIONS_DIR%" 2^>nul') do (
    set /a COUNT+=1
    set "VER_!COUNT!=%%I"
    if "%%I"=="%SELECTED_VERSION%" (
        call echo   [!COUNT!] %%I [ВЫБРАНО]
    ) else (
        call echo   [!COUNT!] %%I
    )
)

if %COUNT%==0 (
    echo   [!] В папке '%VERSIONS_DIR%' не найдено версий!
    echo   [E] Назад в главное меню
    pause
    goto MAIN_MENU
)

echo   [E] Назад в главное меню
echo.

set /p "VER_CHOICE=Выберите номер версии (или 'e' для возврата): "
if /i "%VER_CHOICE%"=="e" goto MAIN_MENU

set "VALID=0"
for /l %%A in (1,1,%COUNT%) do (
    if "%VER_CHOICE%"=="%%A" (
        set "VALID=1"
        call set "SELECTED_VERSION=%%VER_!VER_CHOICE!%%"
    )
)

if "%VALID%"=="1" (
    call :SAVE_CONFIG
    echo   [+] Выбрана версия: %SELECTED_VERSION%
    timeout /t 2 >nul
    goto MAIN_MENU
) else (
    echo   Некорректный номер.
    timeout /t 2 >nul
    goto SELECT_VERSION
)

:CHANGE_NICK
call :PRINT_HEADER
echo   Текущий ник: %NICKNAME%
echo   [E] Назад в главное меню
echo.
set /p "NEW_NICK=Введите новый ник (или 'e' для отмены): "
if /i "%NEW_NICK%"=="e" goto MAIN_MENU
if not "%NEW_NICK%"=="" set "NICKNAME=%NEW_NICK%"
call :SAVE_CONFIG
echo   [+] Ник изменен на: %NICKNAME%
timeout /t 2 >nul
goto MAIN_MENU

:LAUNCH_GAME
call :PRINT_HEADER
if "%SELECTED_VERSION%"=="" (
    echo   [!] Версия не выбрана! Перейдите в пункт 2 и выберите версию.
    timeout /t 3 >nul
    goto MAIN_MENU
)

echo =========================================================
echo                     КОНСОЛЬ ЛОГОВ                       
echo =========================================================
echo   Подготовка к запуску %SELECTED_VERSION% | Ник: %NICKNAME%
echo   При закрытии игры или этой консоли процесс завершится.
echo.

set "JSON_FILE=%VERSIONS_DIR%\%SELECTED_VERSION%\%SELECTED_VERSION%.json"
set "JAR_FILE=%VERSIONS_DIR%\%SELECTED_VERSION%\%SELECTED_VERSION%.jar"

if not exist "%JSON_FILE%" (
    echo   [Ошибка]: Не найден файл конфигурации версии %JSON_FILE%
    pause
    goto MAIN_MENU
)

for /f "usebackq tokens=*" %%a in (`powershell -Command "[guid]::NewGuid().ToString('N')"`) do set "OFFLINE_UUID=%%a"

powershell -Command "$json = Get-Content '%JSON_FILE%' | ConvertFrom-Json; $cp = @(); foreach($lib in $json.libraries){ if($lib.downloads.artifact){ $p = $lib.downloads.artifact.path -replace '/', '\'; $cp += Join-Path '%BASE_DIR%\libraries' $p } }; $cp += '%JAR_FILE%'; $mainClass = $json.mainClass; $assetIndex = if($json.assetIndex.id){ $json.assetIndex.id } else { $json.assets }; $gameArgs = \"\"; if($json.minecraftArguments){ $gameArgs = $json.minecraftArguments -replace '\$\{auth_player_name\}', '%NICKNAME%' -replace '\$\{version_name\}', '%SELECTED_VERSION%' -replace '\$\{game_directory\}', '%BASE_DIR%' -replace '\$\{assets_root\}', '%BASE_DIR%\assets' -replace '\$\{assets_index_name\}', $assetIndex -replace '\$\{auth_uuid\}', '%OFFLINE_UUID%' -replace '\$\{auth_access_token\}', '0' -replace '\$\{user_type\}', 'legacy' } else { $gameArgs = \"--username %NICKNAME% --version %SELECTED_VERSION% --gameDir %BASE_DIR% --assetsDir %BASE_DIR%\assets --assetIndex $assetIndex --uuid %OFFLINE_UUID% --accessToken 0 --userType legacy\" }; $args = \"-Xmx4G -Xms2G -Djava.library.path=%BASE_DIR%\natives -cp `\"$($cp -join ';')`\" $mainClass $gameArgs\"; Start-Process java -ArgumentList $args -Wait"

goto MAIN_MENU
