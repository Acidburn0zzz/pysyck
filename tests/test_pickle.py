# coding: utf-8

import unittest

import syck

SIMPLE = """
- !python/none ~
- !python/bool True
- !python/bool False
- !python/int 123
- !python/long 12345678901234567890
- !python/float 123.456
- !python/float 123456e-3
- !python/complex 1.0
- !python/complex 0.0+1.0j
- !python/str foo bar
- !python/unicode FOO ФУ bar ба
- !python/list [1, 2, 3]
- !python/tuple [foo, bar]
- !python/dict {foo: bar}
""", [
    None,
    True,
    False,
    123,
    12345678901234567890L,
    123.456,
    123.456,
    1+0j,
    1j,
    'foo bar',
    unicode('FOO ФУ bar ба', 'utf-8'),
    [1, 2, 3],
    ('foo', 'bar'),
    {'foo': 'bar'},
]

class AClass:
    pass

class ASubclass(AClass):
    pass

class AType(object):
    pass

class ASubtype(AType):
    pass

def a_function(*args, **kwds):
    pass

NAMES = """
- !python/name:unittest.TestCase
- !python/name:test_pickle.AClass
- !python/name:test_pickle.ASubclass
- !python/name:test_pickle.AType
- !python/name:test_pickle.ASubtype
- !python/name:test_pickle.a_function
- !python/name:list
- !python/name:__builtin__.dict
- !python/name:file
- !python/name:map
- !python/name:type
- !python/name:object
""", [
    unittest.TestCase,
    AClass,
    ASubclass,
    AType,
    ASubtype,
    a_function,
    list,
    dict,
    file,
    map,
    type,
    object,
]

import sys, unittest, encodings.cp1251, os.path

MODULES = """
- !python/module:sys
- !python/module:unittest
- !python/module:encodings.cp1251
- !python/module:os.path
""", [sys, unittest, encodings.cp1251, os.path]

class AnObject(object):

    def __new__(cls, foo=None, bar=None, baz=None):
        self = object.__new__(cls)
        self.foo = foo
        self.bar = bar
        self.baz = baz
        return self

    def __cmp__(self, other):
        return cmp((type(self), self.foo, self.bar, self.baz),
                (type(other), other.foo, other.bar, other.baz))

    def __eq__(self, other):
        return type(self) is type(other) and    \
                (self.foo, self.bar, self.baz) == (other.foo, other.bar, other.baz)

class AnInstance:

    def __init__(self, foo=None, bar=None, baz=None):
        self.foo = foo
        self.bar = bar
        self.baz = baz

    def __cmp__(self, other):
        return cmp((type(self), self.foo, self.bar, self.baz),
                (type(other), other.foo, other.bar, other.baz))

    def __eq__(self, other):
        return type(self) is type(other) and    \
                (self.foo, self.bar, self.baz) == (other.foo, other.bar, other.baz)

class AState(AnInstance):

    def __getstate__(self):
        return {
            '_foo': self.foo,
            '_bar': self.bar,
            '_baz': self.baz,
        }

    def __setstate__(self, state):
        self.foo = state['_foo']
        self.bar = state['_bar']
        self.baz = state['_baz']

OBJECTS = """
- !python/object:test_pickle.AnObject
    foo: 1
    bar: two
    baz: [3, 4, 5]
- !python/object:test_pickle.AnInstance
    foo: 1
    bar: two
    baz: [3, 4, 5]
- !python/object:test_pickle.AState
    _foo: 1
    _bar: two
    _baz: [3, 4, 5]
""", [
    AnObject(foo=1, bar='two', baz=[3,4,5]),
    AnInstance(foo=1, bar='two', baz=[3,4,5]),
    AState(foo=1, bar='two', baz=[3,4,5]),
]

class ACustomState(AnInstance):

    def __getstate__(self):
        return (self.foo, self.bar, self.baz)

    def __setstate__(self, state):
        self.foo, self.bar, self.baz = state

class InitArgs(AnInstance):

    def __getinitargs__(self):
        return (self.foo, self.bar, self.baz)

class InitArgsWithState(AnInstance):

    def __getinitargs__(self):
        return (self.foo, self.bar)

    def __getstate__(self):
        return self.baz[:]

    def __setstate__(self, state):
        self.baz = state[:]

class NewArgs(AnObject):

    def __getnewargs__(self):
        return (self.foo, self.bar, self.baz)

    def __getstate__(self):
        return None

class NewArgsWithState(AnObject):

    def __getnewargs__(self):
        return (self.foo, self.bar)

    def __getstate__(self):
        return self.baz[:]

    def __setstate__(self, state):
        self.baz = state[:]

NEWS = """
- !python/new:test_pickle.ACustomState
    state: !python/tuple [1, two, [3, 4, 5]]
- !python/new:test_pickle.InitArgs [1, two, [3, 4, 5]]
- !python/new:test_pickle.InitArgs
    args: [1]
    kwds: {bar: two, baz: [3, 4, 5]}
- !python/new:test_pickle.InitArgsWithState
    args: [1, two, [3, 4, 5]]
    state: [3, 4, 5]
- !python/new:test_pickle.NewArgs [1, two, [3, 4, 5]]
- !python/new:test_pickle.NewArgs
    args: [1]
    kwds: {bar: two, baz: [3, 4, 5]}
- !python/new:test_pickle.NewArgsWithState
    args: [1, two, [3, 4, 5]]
    state: [3, 4, 5]
""", [
    ACustomState(foo=1, bar='two', baz=[3,4,5]),
    InitArgs(foo=1, bar='two', baz=[3,4,5]),
    InitArgs(foo=1, bar='two', baz=[3,4,5]),
    InitArgsWithState(foo=1, bar='two', baz=[3,4,5]),
    NewArgs(foo=1, bar='two', baz=[3,4,5]),
    NewArgs(foo=1, bar='two', baz=[3,4,5]),
    NewArgsWithState(foo=1, bar='two', baz=[3,4,5]),
]

class Reduce(AnObject):

    def __reduce__(self):
        return self.__class__, (self.foo, self.bar, self.baz)

class ReduceWithState(AnObject):

    def __reduce__(self):
        return self.__class__, (self.foo, self.bar), self.baz[:]

    def __setstate__(self, state):
        self.baz = state[:]

APPLIES = """
- !python/apply:test_pickle.Reduce [1, two, [3, 4, 5]]
- !python/apply:test_pickle.Reduce
    args: [1]
    kwds: {bar: two, baz: [3, 4, 5]}
- !python/apply:test_pickle.ReduceWithState
    args: [1, two]
    state: [3, 4, 5]
""", [
    Reduce(foo=1, bar='two', baz=[3,4,5]),
    Reduce(foo=1, bar='two', baz=[3,4,5]),
    ReduceWithState(foo=1, bar='two', baz=[3,4,5]),
]

class TestPickle(unittest.TestCase):

    def testSimple(self):
        self._testPickle(SIMPLE)

    def testNames(self):
        self._testPickle(NAMES)

    def testModules(self):
        self._testPickle(MODULES)

    def testObjects(self):
        self._testPickle(OBJECTS)

    def testNews(self):
        self._testPickle(NEWS)

    def testApplies(self):
        self._testPickle(APPLIES)

    def _testPickle(self, (source, object)):
        for left, right in zip(syck.load(source), object):
            self.assertEqual(left, right)
        for left, right in zip(syck.load(syck.dump(object)), object):
            self.assertEqual(left, right)

class MyPrivateType(AnObject):
    pass

class MyPublicType(AnObject):
    pass

class MyMapping(AnObject):

    def yaml_construct(cls, node):
        return cls(**node.value)
    yaml_construct = classmethod(yaml_construct)

    def yaml_represent(self, node):
        return syck.Map(self.__dict__.copy(), inline=True)

EXTENSIONS = """
- !!MyPrivateType [1, 2, 3]
- !domain.tld,2005/MyPublicType [1, 2, 3]
- !domain.tld,2005/AnotherPublicType [1, 2, 3]
- {foo: 1, bar: 2, baz: 3}
""", [
    MyPrivateType(1,2,3),
    MyPublicType(1,2,3),
    MyPublicType(1,2,3),
    MyMapping(1,2,3),
]

NODES = """
- foo
- [bar, baz]
"""

BUGGY_NODES = """
- foo
- { bar: baz }
"""

class ExLoader(syck.Loader):

    def find_constructor(self, node):
        if node.kind == 'map':
            return MyMapping.yaml_construct
        return super(ExLoader, self).find_constructor(node)

    def make_mapping(self, node):
        return MyMapping(**node.value)

    def construct_private_MyPrivateType(self, node):
        return MyPrivateType(*node.value)

    def construct_domain_tld_2005(self, node):
        return MyPublicType(*node.value)

class ExDumper(syck.Dumper):

    def find_representer(self, object):
        if isinstance(object, MyMapping):
            return object.yaml_represent
        return super(ExDumper, self).find_representer(object)

    def represent_test_pickle_MyPrivateType(self, object):
        return syck.Seq([object.foo, object.bar, object.baz],
                tag="x-private:MyPrivateType", inline=True)

    def represent_test_pickle_MyPublicType(self, object):
        return syck.Seq([object.foo, object.bar, object.baz],
                tag="tag:domain.tld,2005:APublicType", inline=True)

class TestExtensions(unittest.TestCase):

    def testExtensions(self):
        source = EXTENSIONS[0]
        object = EXTENSIONS[1]
        object2 = syck.load(source, Loader=ExLoader)
        for left, right in zip(object, object2):
            self.assertEqual(left, right)
        source2 = syck.dump(object2, Dumper=ExDumper)
        object3 = syck.load(source2, Loader=ExLoader)
        for left, right in zip(object, object3):
            self.assertEqual(left, right)

class TestNodesReduce(unittest.TestCase):

    def testNodesReduce(self):
        object = syck.load(NODES)
        nodes = syck.parse(NODES)
        output = syck.dump(nodes)
        #print output
        nodes2 = syck.load(output)
        output2 = syck.emit(nodes2)
        object2 = syck.load(output2)
        self.assertEqual(object, object2)

    def testBuggyNodesReduce(self):
        object = syck.load(BUGGY_NODES)
        nodes = syck.parse(BUGGY_NODES)
        output = syck.dump(nodes)
        #print output
        nodes2 = syck.load(output)
        output2 = syck.emit(nodes2)
        object2 = syck.load(output2)
        self.assertEqual(object, object2)

