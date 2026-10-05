@echo off
cd /d "%~dp0"
py forest_invasion.py --source "..\web\public\feed" --max 42 --interval 1.6
