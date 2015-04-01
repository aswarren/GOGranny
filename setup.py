#!/usr/bin/env python
from distutils.core import setup
import sys

try:
    import networkx
    version = networkx.__version__.split('.')
    if int(version[0]) == 0 and int(version[1]) < 99:
        print "You need to install networkx >= 0.99 from networkx.lanl.gov"
        sys.exit(1)
except ImportError:
    print "You need to install networkx >= 0.99 (networkx.lanl.gov)"
    sys.exit(1)    

setup(name='GOGranny',
            version='0.0',
            description='A network graph representation of the Gene Ontology based on GOGranny',
            author='Andrew Warren',
            author_email='aswarren@gmail.com',
            url='https://github.com/aswarren/GOGranny',
            packages=['GOGranny', 'GOGranny.Storage', 'GOGranny.XGraphWeighters'],
            long_description = '',
            license='GNU GPL v2',
            )
