@echo off
REM Windows 脚本运行包装器
REM 解决 Python 模块导入路径问题

setlocal

REM 获取当前目录
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM 设置 Python 路径
set PYTHONPATH=%PROJECT_ROOT%;%SCRIPT_DIR%;%PYTHONPATH%

echo 脚本目录: %SCRIPT_DIR%
echo 项目根目录: %PROJECT_ROOT%
echo Python 路径已设置

REM 运行传入的 Python 脚本
python %*

endlocal