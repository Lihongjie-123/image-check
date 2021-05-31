#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    create zip 安装包
"""
from __future__ import print_function

import logging
import os.path
import shutil
import stat
import sys

current_file_dir = os.path.dirname(__file__)
py_strip_dirs = open(os.path.join(current_file_dir,
                                  "strip_py.list")).readlines()


def _copytree(src, dst, ignore=None):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()
    try:
        os.makedirs(dst)
    except Exception:
        pass
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                shutil.copytree(srcname, dstname, ignore=ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise (shutil.Error, errors)


def _zip_file(target_dir):
    root_dir = os.path.dirname(target_dir)
    os.chdir(root_dir)
    shutil.make_archive(os.path.basename(target_dir), format="gztar",
                        root_dir=root_dir,
                        base_dir=os.path.basename(target_dir))


def _strip_py(py_dir):
    for base, _, files in os.walk(py_dir):
        for name in files:
            if name.endswith('.py'):
                path = os.path.join(base, name)
                logging.debug("Deleting %s", path)
                os.unlink(path)


def chmod_sh_files(src_dir):
    for root, subs, files in os.walk(src_dir):
        for sh in files:
            if sh.endswith(".sh"):
                os.chmod(os.path.join(root, sh), stat.S_IXUSR | stat.S_IRUSR)


def main():
    # src_dir = sys.argv[1]
    site_pacakge_dir = sys.argv[2]
    target_dir = sys.argv[3]

    top_dir = sys.argv[4]

    shutil.rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir)

    # 从top dircopy，linux bin目录里面包含了python的脚本
    for src_dir in ("bin", "etc", "logs", "var", "test_data"):
        _copytree(os.path.join(top_dir, src_dir),
                  os.path.join(target_dir, src_dir))
    shutil.copy2(os.path.join(top_dir, "VERSION"),
                 os.path.join(target_dir, "VERSION"))
    shutil.copy2(os.path.join(top_dir, "README.txt"),
                 os.path.join(target_dir, "README.txt"))

    target_lib_dir = os.path.join(target_dir, "lib")
    _copytree(site_pacakge_dir, target_lib_dir)

    for py_dir in py_strip_dirs:
        _strip_py(os.path.join(target_lib_dir, py_dir))
    # set src/**/*.sh executable permission
    chmod_sh_files(target_dir)
    _zip_file(target_dir)

    print("")
    print("output dir %s" % target_dir)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception("main except")
        sys.exit(1)
