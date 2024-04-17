#!/bin/bash

cd D:\Document\Polytechnique Montreal\2-Hiver2024\INF6102\INF6102-ProjetEternity2

conda activate Inf6102ProjetEternity2

python .\main.py --agent=advanced --infile=.\instances\eternity_B.txt

python .\launchAllInstances.py
