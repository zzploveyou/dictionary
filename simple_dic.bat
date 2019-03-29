@echo off

color 0B

:begin
cls
set input=
set /p input=input:
if defined input (
  python simple_dic.py -d database/dic.db -w %input%
  pause
  echo.
  goto begin
) else exit
