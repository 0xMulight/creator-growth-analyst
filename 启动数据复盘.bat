@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"
:menu
cls
echo =============== Creator Growth Analyst ===============
echo 1 分析演示数据（无需登录）
echo 2 分析自己的CSV文件
echo 3 只检查CSV格式
echo 0 退出
set /p choice=请选择: 
if "%choice%"=="1" python -m creator_growth_analyst analyze examples/sample-posts.csv --out reports
if "%choice%"=="2" (
  set /p filepath=请输入CSV文件路径: 
  python -m creator_growth_analyst analyze "!filepath!" --out reports
)
if "%choice%"=="3" (
  set /p filepath=请输入CSV文件路径: 
  python -m creator_growth_analyst validate "!filepath!"
)
if "%choice%"=="0" exit /b
pause
goto menu
