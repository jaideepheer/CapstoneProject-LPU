@echo off
cd %~dp0deployment

if exist OK_DO_NOT_DELETE (
    activate kapstone
    echo Starting Jupyter lab...
    cd ../Code/
    jupyter lab --config='../deployment/jupyter/jupyter_notebook_config.py'
    cd ..
) else (
    echo Setting up environment...
    start "Setup kapstone environment" install.bat && echo Delete this file to re-install environment. >OK_DO_NOT_DELETE
    echo "Please run this script whenever you want to start the Jupyter lab."
)