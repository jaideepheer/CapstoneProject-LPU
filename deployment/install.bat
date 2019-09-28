@echo off
cd %~dp0

rem mkdir .\ENVIRONMENT\etc\conda\activate.d\
rem mkdir .\ENVIRONMENT\etc\conda\deactivate.d\
rem echo (start "" "%%~dp0%%..\..\..\..\on_activate.bat")  > ENVIRONMENT\etc\conda\activate.d\env_vars.bat
rem echo (start "" "%%~dp0%%..\..\..\..\on_deactivate.bat")  > ENVIRONMENT\etc\conda\deactivate.d\env_vars.bat

conda env create --name=kapstone --file kapstone.yml

conda activate kapstone
ipython kernel install --user --name=kapstone-kernel

conda install swig

pip install cmake
pip install dlib
pip install pocketsphinx

echo Environment setup done.