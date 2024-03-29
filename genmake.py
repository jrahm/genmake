#!/usr/bin/python

# This is a script that generates a makefile.
# This script should be run and piped to the

# There are some configuration options below

import sys

SOURCE_DIR='src'
INCLUDE_PATHS=['include']

CPP_SUFFIX='.cpp'
EXTRA_CFLAGS=''
LD_FLAGS=''

DEFAULT_CPP_COMPILER='g++'
DEFAULT_LDD='g++'

BINARY_NAME='lke'

DEFAULT_TGT='x86_64'
DEFAULT_ENV='debug'

MESSAGE="""The Lords, Kings, Emperors makefile

This file has been generated by """+ sys.argv[0] +"""

DO NOT COMMIT THIS MAKEFILE"""

# The header to the make file
max_line_len = max([len(i) for i in MESSAGE.splitlines()])
print("#" * max_line_len)
print("# " + "# ".join(MESSAGE.splitlines(True)))
print("#" * max_line_len)
print('')

print('BINARY_NAME=' + BINARY_NAME)
print('TGT?=' + DEFAULT_TGT)
print('ENV?=' + DEFAULT_ENV)
print('')

# conditionally include all the makefiles
print('-include mk/$(TGT).tgtcommon.mk')
print('-include mk/$(ENV).envcommon.mk')
print('-include mk/$(TGT)/$(ENV).mk')

# some of the variables to be assigned
# after the inclusion of the taget and
# environment include paths
print('')
print('CXX?=' + DEFAULT_CPP_COMPILER)
print('INCLUDES= -I ' + "-I".join(INCLUDE_PATHS))
print('CFLAGS:=$(CFLAGS) $(INCLUDES) ' + EXTRA_CFLAGS)
print('LD?=' + DEFAULT_LDD)
print('LDFLAGS:=$(LDFLAGS) -lstdc++')

print('hack:=$(shell mkdir -p _$(TGT)_obs)')


print('')
print('default: link')
print('')

# end of configuration options

import os
import re

# the pattern of included paths
PATTERN = re.compile('#include\\s+[<"]\\s*((\\w|.)*)\\s*[>"]\\s+')

source_files=[]

for (root, _, files) in os.walk(SOURCE_DIR):
    for f in files:
        if f.endswith(CPP_SUFFIX):
            source_files.append(os.path.join(root, f))

# now all the source files have been added

def to_object_files(source_file):
    temp = source_file.replace('/', '_').replace('\\', '_')
    return os.path.join('_$(TGT)_obs', temp[:-4] + '.o')

# [(source_file, object_file)]
source_object_files=[(x, to_object_files(x)) for x in source_files]

def dependency_to_full_path(filename, dirname):
    # try to convert an include file to a full path
    # so it can be included in the dependency tree of
    # a file.
    for incl in INCLUDE_PATHS + [dirname]:
        rincl = os.path.join(incl, filename)
        if os.path.isfile(rincl):
            return rincl
    return None

def get_dependencies(f):
    # return all the dependencies of a
    # source file.
    ret = set()
    fd = open(f, 'r')
    for line in fd.readlines():
        match = PATTERN.match(line)
        if match:
            filename = match.group(1)
            dirname = os.path.dirname(f)
            newdep = dependency_to_full_path(filename, dirname)
            if newdep != None:
                ret.add(newdep)
                ret.update(get_dependencies(newdep))
    return ret

for (source, obj) in source_object_files:
    rule = obj + ': ' + source + " " + " ".join(get_dependencies(source))
    recipie = '$(CXX) $(CFLAGS) -o %s -c %s' % (obj, source)

    # print out the rules and the recepies
    print(rule)
    print('\t'+recipie)
    print('')

obj_files=" ".join([o for (_, o) in source_object_files])
print('link: ' + " ".join([o for (_, o) in source_object_files]))
print('\t$(CXX) $(LDFLAGS) -o _$(TGT)_obs/$(BINARY_NAME) ' + obj_files);
print('\tln -sf _$(TGT)_obs/$(BINARY_NAME) $(BINARY_NAME).$(TGT)')

print('')
print('clean:')
print('\trm -rf _$(TGT)_obs')
print('')
print('cleanall:')
print('\trm -rf _*_obs')
print('')
print('genmake:')
print('\t./genmake.py > Makefile')
