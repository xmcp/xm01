from cx_Freeze import setup,Executable
import sys
import os, shutil
os.chdir(os.path.split(sys.argv[0])[0])
if len(sys.argv)==1:
    sys.argv.append('build')

setup(name='xm01',
    version='1.0',
    description='xmcp',
    executables=[
        Executable("proc.py", compress=True, targetName='xm01.exe'),
        Executable("visualize.pyw", compress=True, targetName='vm01.exe', base='win32gui'),
    ],
    options={'build_exe':{
        'optimize':2,
        'includes':'jinja2.ext'
    }})

shutil.rmtree('build/exe.win32-3.4/tcl/tzdata')
shutil.rmtree('build/exe.win32-3.4/tcl/msgs')
shutil.rmtree('build/exe.win32-3.4/tcl/encoding')
shutil.rmtree('build/exe.win32-3.4/tk/demos')
shutil.rmtree('build/exe.win32-3.4/tk/images')
shutil.rmtree('build/exe.win32-3.4/tk/msgs')