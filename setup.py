
NAME = 'PySyck'
VERSION = '0.61.2'
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
URL = "http://pyyaml.org/wiki/PySyck"
DOWNLOAD_URL = "http://pyyaml.org/download/pysyck/%s-%s.tar.gz" % (NAME, VERSION)
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Markup",
]

from distutils.core import setup, Extension

from distutils import log
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError, CompileError, LinkError

import os

CHECK_SYCK = """
#include <syck.h>
#include <stdio.h>
int main(void) {
    syck_free_parser(syck_new_parser());
    syck_free_emitter(syck_new_emitter());
    puts(SYCK_VERSION);
    return 0;
}
"""
CHECK_SYCK_PROG = './_check_syck'

class PySyckBuildExt(build_ext):

    def build_extensions(self):
        if not self.force:
            self.check_syck()
        build_ext.build_extensions(self)

    def _clean(self, *filenames):
        for filename in filenames:
            try:
                os.remove(filename)
            except OSError:
                pass

    def check_syck(self):
        prog = CHECK_SYCK_PROG
        src = prog + '.c'
        file(src, 'w').write(CHECK_SYCK)
        [obj] = self.compiler.object_filenames([src])
        log.info("checking for syck.h")
        try:
            self.compiler.compile([src])
        except CompileError:
            self._clean(src, obj)
            raise CompileError, "syck.h is not found, " \
                    "try to uncomment the include_dirs parameter in setup.cfg"
        log.info("checking for libsyck.a")
        try:
            self.compiler.link_executable([obj], prog, libraries=['syck'])
        except LinkError:
            self._clean(src, obj, prog)
            raise LinkError, "libsyck.a is not found, " \
                    "try to uncomment the library_dirs parameter in setup.cfg"
        if self.compiler.exe_extension:
            prog += self.compiler.exe_extension
        log.info("checking syck version")
        pipe = os.popen(prog, 'r')
        data = pipe.read().strip()
        pipe.close()
        version = float(data)
        log.info("syck version: %s" % version)
        if version < 0.55:
            self._clean(src, obj, prog)
            raise CCompilerError, "syck 0.55 or higher is required"
        self._clean(src, obj, prog)
            

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
#            include_dirs=[],   # do not uncomment this, edit setup.cfg instead.
#            library_dirs=[],   # do not uncomment this, edit setup.cfg instead.
            libraries=['syck'],
        ),
    ],
    cmdclass={
        'build_ext': PySyckBuildExt,
    },
)

