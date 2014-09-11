#!/usr/bin/env python

from distutils.core import setup
import os

packages = []
package_data_files = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('siptrackweb'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    else:
        pkg = os.path.sep.join(dirpath.split(os.path.sep)[1:])
        filenames = [os.path.join(pkg, filename) for filename in filenames]
        package_data_files += filenames

setup(name = 'siptrackweb',
        version = '1.0.4',
        description = 'Siptrack IP/Device Manager Web Frontend',
        author = 'Simon Ekstrand',
        author_email = 'simon@theoak.se',
        url = 'http://siptrack.theoak.se/',
        license = 'BSD',
        package_dir = {'siptrackweb': 'siptrackweb'},
        packages = packages,
        package_data = {'siptrackweb': package_data_files},
        )

