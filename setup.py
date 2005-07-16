
from distutils.core import setup, Extension

import sys
if sys.version < '2.2.4':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

import os
home = os.environ.get('HOME', '')

setup(
    name='Syck',
    version='0.55.1',
    package_dir={'': 'lib'},
    packages=['syck'],
    ext_modules=[
        Extension('_syck', ['ext/_syckmodule.c'],
            include_dirs=['../../include', '%s/include' % home, '/usr/local/include'],
            library_dirs=['../../lib', '%s/lib' % home, '/usr/local/include'],
            libraries=['syck'],
        ),
    ],
    description="Python bindings for the Syck YAML parser",
    author="Kirill Simonov",
    author_email="xi@resolvent.net",
    license="BSD",
    url="http://xitology.org/python-syck/",
    download_url="http://xitology.org/*FIXME*",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
)

