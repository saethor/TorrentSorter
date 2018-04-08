import os
import shutil

if not os.path.isdir('debug'):
    os.makedirs('debug')
cwd = os.getcwd()

extensions = ['avi', 'mp4', 'mov', 'mpg', 'mkv', 'm4v', 'wmv']
for path, dirs, files in os.walk('downloads'):
    curr_path = os.path.join(cwd, path)
    for f in files:
        if f.split('.')[-1] in extensions:
            if os.path.exists(os.path.join('debug', f)):
                continue
            try:
                shutil.copy(os.path.join(curr_path, f), 'debug')
            except FileNotFoundError:
                continue
        
