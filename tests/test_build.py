
def main():
    import sys, os, distutils.util
    build_lib = os.path.join('build', 'lib.%s-%s' % (distutils.util.get_platform(), sys.version[0:3]))
    sys.path.insert(0, build_lib)
    import test_syck
    test_syck.main('test_syck')

if __name__ == '__main__':
    main()

