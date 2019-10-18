cd %~dp0
conda env export -n kapstone --from-history > kapstone.yml && pip list > kapstone.txt