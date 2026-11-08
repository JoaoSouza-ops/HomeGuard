@echo off
rem Atalhos do HomeGuard (Windows).  Uso: hg.cmd up ^| sim ^| check ^| ps ^| logs [servico] ^| down ^| reset
setlocal
cd /d "%~dp0"
if not exist .env (
  copy /y .env.example .env >nul
  echo [hg] .env criado a partir do .env.example
)
cd infra
set "DC=docker compose --env-file ../.env --profile lab --profile sim"

if "%~1"=="" goto ajuda
if /i "%~1"=="up" goto up
if /i "%~1"=="sim" goto sim
if /i "%~1"=="check" goto check
if /i "%~1"=="ps" goto ps
if /i "%~1"=="logs" goto logs
if /i "%~1"=="down" goto down
if /i "%~1"=="reset" goto reset
goto ajuda

:up
%DC% up --build -d mosquitto backend web caddy
call :urls
goto fim

:sim
%DC% up --build -d
call :urls
echo   Simulador de ESPs ligado: MQTT + Telnet em localhost:2323
goto fim

:check
%DC% run --rm esp-sim python check.py
goto fim

:ps
%DC% ps
goto fim

:logs
%DC% logs -f --tail=100 %~2
goto fim

:down
%DC% down
goto fim

:reset
%DC% down -v
goto fim

:urls
echo.
echo   Dashboard: http://localhost:8080
echo   API docs : http://localhost:8080/api/docs
echo.
exit /b 0

:ajuda
echo Uso: hg.cmd ^<comando^>
echo   up     sobe API + dashboard + broker MQTT
echo   sim    sobe tudo + simulador dos ESPs, para testar sem o hardware
echo   check  testa API, MQTT e Telnet
echo   ps     mostra o estado dos servicos
echo   logs   acompanha os logs, ex.: hg.cmd logs backend
echo   down   para tudo
echo   reset  para tudo e APAGA os dados do banco SQLite

:fim
endlocal
