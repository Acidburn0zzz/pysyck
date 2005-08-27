
NAME = 'PySyck'
VERSION = '0.55.1'
DESCRIPTION = "Python bindings for the Syck YAML parser and emitter"
LONG_DESCRIPTION = """\
YAML is a data serialization format designed for human readability
and interaction with scripting languages. Syck is an extension for
reading and writing YAML in scripting languages. PySyck is aimed to
update the current Python bindings for Syck."""
AUTHOR = "Kirill Simonov"
AUTHOR_EMAIL = 'xi@resolvent.net'
LICENSE = "BSD"
PLATFORMS = "Any"
URL = "http://xitology.org/pysyck/"
DOWNLOAD_URL = URL + "%s-%s.tar.gz" % (NAME, VERSION)
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Markup",
]

from distutils.core import setup, Extension

import sys
if sys.version < '2.2.4':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

import os
home = os.environ.get('HOME', '')

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    platforms=PLATFORMS,
    url=URL,
    download_url=DOWNLOAD_URL,
    classifiers=CLASSIFIERS,

    package_dir={'': 'lib'},
    packages=['syck'],
    ext_modules=[
        Extension('_syck', ['ext/_syckmodule.c'],
            include_dirs=['../../include', '%s/include' % home, '/usr/local/include'],
            library_dirs=['../../lib', '%s/lib' % home, '/usr/local/include'],
            libraries=['syck'],
        ),
    ],
)

