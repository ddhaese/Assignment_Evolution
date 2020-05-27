REM This batch file extracts the data needed to reconstruct timelines of all
REM repos in current directory
REM repo. Usage: $ githist

@ECHO OFF
CLS
ECHO Git History version 0.1
ECHO %DATE%
ECHO Setting character set...
CHCP 65001
ECHO Deleting export file...
DEL githist.raw

FOR /D %%i IN (*) DO CALL :GitHistRepo "%%i"

ECHO Parsing raw results ...
python githist.py -i githist.raw -o githist.tsv >> githist.log

EXIT /B %ERRORLEVEL% 

:GitHistRepo
CD %~1
ECHO Processing repo %~1 ...
ECHO Processing repo %~1 ... >> ../githist.raw
git pull
git --no-pager log --numstat --stat-count=500 --full-history --reverse >> ../githist.raw
CD ..

EXIT /B 0