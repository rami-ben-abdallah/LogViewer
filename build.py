# build.py - Single command to build everything
import os
import subprocess
import sys

def collect_python_files(src_dir):
    python_files = []
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs]
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, src_dir)
                module_path = rel_path.replace('.py', '').replace(os.path.sep, '.')

                if module_path.endswith('.__init__'):
                    module_path = module_path[:-9]
                if module_path:
                    python_files.append(f'src.{module_path}')
    print(f"Found {len(python_files)} Python modules")                
    return python_files

def build_executable():   
    python_files = collect_python_files('src')
    
    pyInstallerCommand = [
        'pyinstaller',
        '--onefile',
        '--noconsole',
        '--name', 'LogViewer',
        '--icon', 'assets/icon.png',
        '--add-data', f'assets{os.pathsep}assets',
        '--add-data', f'src{os.pathsep}src',
        '--paths', 'src',
        '--clean',  # Clean build cache
    ]
    
    # Add all modules as hidden imports
    for module in python_files:
        pyInstallerCommand.extend(['--hidden-import', module])
    
    # Add the entry point
    pyInstallerCommand.append('src/__init__.py')
    
    print("Running:", ' '.join(pyInstallerCommand))
    result = subprocess.run(pyInstallerCommand)
    return result.returncode

if __name__ == '__main__':  
    exit_code = build_executable()
    sys.exit(exit_code)