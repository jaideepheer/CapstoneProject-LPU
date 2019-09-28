@echo off
cd %~dp0

rem mkdir .\ENVIRONMENT\etc\conda\activate.d\
rem mkdir .\ENVIRONMENT\etc\conda\deactivate.d\
rem echo (start "" "%%~dp0%%..\..\..\..\on_activate.bat")  > ENVIRONMENT\etc\conda\activate.d\env_vars.bat
rem echo (start "" "%%~dp0%%..\..\..\..\on_deactivate.bat")  > ENVIRONMENT\etc\conda\deactivate.d\env_vars.bat

echo Importing Environment from kapstone.yml
conda env create --name=kapstone --file kapstone.yml
echo Environment import completed.

conda activate kapstone
ipython kernel install --user --name=kapstone-kernel
echo IPython Kernel 'kapstone-kernel' for Jupyter Notebooks installed.

echo Environment setup done. Running post-setup script.
python post-setup.py
echo All done. Environment ready for use.