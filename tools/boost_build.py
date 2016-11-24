# Copyright (c) 2016, Gunhoon Lee (gunhoon@gmail.com)
# All rights reserved.

import os
import sys
import shutil
import subprocess
from optparse import OptionParser


# Set the boost version to be installed.
boost_version = '1.62.0'


# Helper funtions
def run(cmd, path):
  """ Run a command. """
  sys.stdout.write('--- Running "%s" in "%s"...\n' % (cmd, path))
  args = cmd.split()
  return subprocess.check_call(args, cwd=path, shell=(sys.platform == 'win32'))


##
# Program entry point.
##

# Can not be loaded as a module.
if __name__ != "__main__":
  sys.stderr.write('*** ERROR: This file can not be loaded as a module!')
  sys.exit()


# Determine the platform.
if sys.platform.startswith('linux'):
  platform = 'linux'
elif sys.platform == 'win32':
  platform = 'windows'
else:
  sys.stderr.write('*** ERROR: Unsupported platform(%s)...' % sys.platform)
  sys.exit()


# Parse command-line options
disc = """
This script builds and installs the Boost C++ libraries.
"""

parser = OptionParser(description=disc)
parser.add_option('--debug-build',
                  action='store_true', dest='debug_build', default=False,
                  help='Perform not release build, but debug build.')
(options, args) = parser.parse_args()

if options.debug_build:
  build_type = 'debug'
else:
  build_type = 'release'

sys.stdout.write('--- build type : %s\n\n' % build_type)


# Set base directories
tools_dir = os.path.dirname(__file__)
root_dir = os.path.join(tools_dir, os.pardir)
boost_dir = os.path.join(root_dir, 'boost_' + boost_version.replace('.', '_'))

sys.stdout.write('--- tools directory : "%s"\n' % os.path.abspath(tools_dir))
sys.stdout.write('--- root directory  : "%s"\n' % os.path.abspath(root_dir))
sys.stdout.write('--- boost directory : "%s"\n\n' % os.path.abspath(boost_dir))


# Check that the boost directory exists.
if not os.path.isdir(boost_dir):
  sys.stderr.write('*** ERROR: "%s" directory does not exist...' % boost_dir)
  sys.exit()


# Set install directory ("/usr/local" on Linux, "{root_dir}/install" on Windows)
if platform == 'linux':
  install_root_path = os.path.abspath('/usr/local')
elif platform == 'windows':
  install_root_path = os.path.join(root_dir, 'install')

install_library_path = os.path.join(install_root_path, 'lib', 'boost')
install_include_path = os.path.join(install_root_path, 'include')

sys.stdout.write('--- installing root path : "%s"\n' % install_root_path)
sys.stdout.write('--- installing library path : "%s"\n' % install_library_path)
sys.stdout.write('--- installing include path : "%s"\n' % install_include_path)


# Delete the pre-installed library directory
if os.path.isdir(install_library_path):
  sys.stdout.write('--- Delete the pre-installed library directory...\n')
  shutil.rmtree(install_library_path)

# Delete the pre-installed include directory
if os.path.isdir(os.path.join(install_include_path, 'boost')):
  sys.stdout.write('--- Delete the pre-installed include directory...\n')
  shutil.rmtree(os.path.join(install_include_path, 'boost'))


# Prepare Boost for building.
if platform == 'linux':
  shell_cmd = './bootstrap.sh'
elif platform == 'windows':
  shell_cmd = 'bootstrap.bat'

run(shell_cmd, boost_dir)


# Build and install Boost
if platform == 'linux':
  shell_cmd = 'sudo ./b2'
elif platform == 'windows':
  shell_cmd = 'b2'

shell_cmd = '%s --prefix=%s --libdir=%s --includedir=%s' \
    % (shell_cmd, install_root_path, install_library_path, install_include_path)
shell_cmd = '%s variant=%s link=shared threading=multi install' \
    % (shell_cmd, build_type)

run(shell_cmd, boost_dir)

sys.stdout.write('--- Installed root path : "%s"\n' % install_root_path)
sys.stdout.write('--- Installed library path : "%s"\n' % install_library_path)
sys.stdout.write('--- Installed include path : "%s"\n' % install_include_path)


# On Windows, installed include directory is as follows.
# {install_root_path}/include/boost-1_62/boost
# Delete "boost-1_62" and change the directory structure as below.
# {install_root_path}/include/boost
if platform == 'windows':
  temp_inc_dir = 'boost-%s' % boost_version[0:4].replace('.', '_')
  temp_src_dir = os.path.join(install_include_path, temp_inc_dir, 'boost')
  temp_dst_dir = os.path.join(install_include_path, 'boost')
  if os.path.isdir(temp_src_dir):
    shutil.move(temp_src_dir, temp_dst_dir)
    shutil.rmtree(os.path.join(install_include_path, temp_inc_dir))

sys.stdout.write('--- Boost build and installation are completed...\n')
