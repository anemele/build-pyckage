@echo off

setlocal

set output=load-pyckage
set dist=dist
if not exist %dist% mkdir %dist%

go build -ldflags="-s -w" -o %dist%\%output%.exe
