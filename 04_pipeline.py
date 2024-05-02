import os

os.chdir('.')
os.system('python 01_compile_data.py')
os.system('python 02_find_best_lines.py')
os.system('python 03_evaluate_trip.py')
