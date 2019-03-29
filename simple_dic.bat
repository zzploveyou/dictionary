@echo off

:begin
cls
set input=
set /p input=input word:
python simple_dic.py -d database/dic.db -w %input%
pause
echo.
goto begin
