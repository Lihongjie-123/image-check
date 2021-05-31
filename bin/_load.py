import os
import sys
import site

# set path
py_dir = os.path.dirname(os.path.realpath(__file__))

parent_dir = os.path.dirname(py_dir)

# print parent_dir
if os.path.isdir(os.path.join(parent_dir, "src")):
    sys.path.append(parent_dir)

libdir = os.path.join(parent_dir, "lib")
# print libdir
if os.path.isdir(libdir):
    old_len = len(sys.path)
    new_sys_path = []
    site.addsitedir(libdir)  # @UndefinedVariable
    for item in sys.path[old_len:]:
        new_sys_path.append(item)
        sys.path.remove(item)
    sys.path[:0] = new_sys_path

# set cwd
os.chdir(parent_dir)
