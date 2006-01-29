
import unittest

import _syck

import StringIO, gc

EXAMPLE = _syck.Seq([
        _syck.Scalar('Mark McGwire'),
        _syck.Scalar('Sammy Sosa'),
        _syck.Scalar('Ken Griffey'),
])

COMPLEX_EXAMPLE = _syck.Map({
    _syck.Scalar('scalars') : _syck.Seq([
            _syck.Scalar(),
            _syck.Scalar('on'),
            _syck.Scalar('12345', tag="tag:yaml.org,2002:int"),
# Syck bug with trailing spaces.
#            _syck.Scalar('long '*100, width=20, indent=5),
            _syck.Scalar('long long long long long\n'*100, width=20, indent=5),
            _syck.Scalar('"1quote"', style='1quote'),
            _syck.Scalar("'2quote'", style='2quote'),
            _syck.Scalar("folding\n"*10, style='fold'),
            _syck.Scalar("literal\n"*10, style='literal'),
            _syck.Scalar("plain text", style='plain'),
        ]),
    _syck.Scalar('sequences') : _syck.Seq([
            _syck.Seq([
                    _syck.Seq([_syck.Scalar('foo'), _syck.Scalar('bar', style='literal')]),
            ], inline=True),
            _syck.Seq([
                _syck.Scalar('foo'),
                _syck.Scalar('bar'),
            ], tag="x-private:myprivatesequence")
        ]),
    _syck.Scalar('mappings') : _syck.Seq([
            _syck.Map({
                _syck.Seq([_syck.Scalar('1'), _syck.Scalar('2')]) :
                    _syck.Seq([_syck.Scalar('3'), _syck.Scalar('4')]),
                _syck.Scalar('5') : _syck.Scalar('6'),
            }),
            _syck.Map({
                _syck.Scalar('foo') :
                    _syck.Seq([_syck.Scalar('bar')])
            }, inline=True, tag="x-private:myprivatemapping"),
        ]),
    _syck.Scalar('empty'): _syck.Seq([
            _syck.Scalar(),
            _syck.Seq(),
            _syck.Map(),
            _syck.Map({_syck.Scalar(tag='tag:yaml.org,2002:str') : _syck.Scalar(tag='tag:yaml.org,2002:str')}),
            _syck.Map({_syck.Scalar('foo') : _syck.Scalar()}),
            _syck.Map({_syck.Scalar(tag='tag:yaml.org,2002:str') : _syck.Scalar('bar')}),
        ]),
})

PAIRS = _syck.Map([
    (_syck.Scalar('foo'), _syck.Scalar('bar')),
    (_syck.Scalar('bar'), _syck.Scalar('baz')),
])

CYCLE = _syck.Seq()
CYCLE.value.append(CYCLE)

ALIASED_OBJECT = _syck.Map({
        _syck.Scalar('key1'): _syck.Scalar('value1'),
        _syck.Scalar('key2'): _syck.Scalar('value2'),
        _syck.Scalar('key3'): _syck.Seq([_syck.Scalar('value3')]),
})

ALIASES = _syck.Seq([ALIASED_OBJECT, ALIASED_OBJECT])

TAGS = [
    'tag:yaml.org,2002:str',
    'tag:yaml.org,2002:int',
    'tag:python.yaml.org,2002:object',
    'tag:domain.tld,2002:my/own/type#variant',
    'x-private:private',
]

INVALID_ROOT = 'break me'

INVALID_SEQ = [
    _syck.Seq([1,2,3]),
    _syck.Map({
        _syck.Scalar('valid'): _syck.Seq([_syck.Scalar('valid'), _syck.Scalar('valid')]),
        _syck.Scalar('invalid'): _syck.Seq([_syck.Scalar('valid'), 'invalid', _syck.Scalar('valid')]),
    }),        
]

INVALID_MAP = [
    _syck.Map({'foo': 'bar'}),
    _syck.Map({'foo': _syck.Scalar('valid')}),
    _syck.Map({_syck.Scalar('valid'): 'bar'}),
    _syck.Seq([
        _syck.Map({}),
        _syck.Map({_syck.Scalar('valid'): 'invalid'}),
    ]),
]

COMPLEX_ITEMS = [
    _syck.Scalar("foo"),
    _syck.Scalar("foo", tag='x-private:complex'),
    _syck.Scalar("foo bar baz", style='fold'),
    _syck.Scalar("foo bar baz", style='fold', tag='x-private:complex'),
    _syck.Seq([]),
    _syck.Seq([], tag='x-private:complex'),
    _syck.Seq([_syck.Scalar('alpha'), _syck.Scalar('beta'), _syck.Scalar('gamma')]),
    _syck.Seq([_syck.Scalar('alpha'), _syck.Scalar('beta'), _syck.Scalar('gamma')], tag='x-private:complex'),
    _syck.Seq([_syck.Scalar('alpha'), _syck.Scalar('beta'), _syck.Scalar('gamma')], inline=True, tag='x-private:complex'),
    _syck.Map({}),
    _syck.Map({}, tag='x-private:complex'),
    _syck.Map([(_syck.Scalar('alpha'), _syck.Scalar('beta')), (_syck.Scalar('gamma'), _syck.Scalar('delta'))], tag='x-private:complex'),
    _syck.Map([(_syck.Scalar('alpha'), _syck.Scalar('beta')), (_syck.Scalar('gamma'), _syck.Scalar('delta'))], inline=True, tag='x-private:complex'),
]

def strip(node, node_to_object=None):
    if node_to_object is None:
        node_to_object = {}
    if node in node_to_object:
        return node_to_object[node]
    object = None
    if node.kind == 'scalar':
        object = node.value
    elif node.kind == 'seq':
        object = []
        for item in node.value:
            object.append(strip(item, node_to_object))
        object = tuple(object)
    elif node.kind == 'map':
        object = []
        dict_value = dict(node.value)
        for key in dict_value:
            object.append((strip(key, node_to_object), strip(dict_value[key], node_to_object)))
        object.sort()
    node_to_object[node] = object
    return object

class TestAttributes(unittest.TestCase):

    def testAttributes(self):
        output = StringIO.StringIO()
        emitter = _syck.Emitter(output)
        self.assertEqual(type(emitter), _syck.Emitter)
        self.assertEqual(emitter.output, output)
        self.assertEqual(emitter.headless, False)
        self.assertEqual(emitter.use_header, False)
        self.assertEqual(emitter.use_version, False)
        self.assertEqual(emitter.explicit_typing, False)
        self.assertEqual(emitter.style, None)
        self.assertEqual(emitter.best_width, 80)
        self.assertEqual(emitter.indent, 2)
        emitter = _syck.Emitter(output, headless=True, use_header=True,
                use_version=True, explicit_typing=True, style='fold',
                best_width=100, indent=4)
        self.assertEqual(emitter.headless, True)
        self.assertEqual(emitter.use_header, True)
        self.assertEqual(emitter.use_version, True)
        self.assertEqual(emitter.explicit_typing, True)
        self.assertEqual(emitter.style, 'fold')
        self.assertEqual(emitter.best_width, 100)
        self.assertEqual(emitter.indent, 4)

    def testInvalidTypesAndValues(self):
        self.assertRaises(TypeError, lambda: _syck.Emitter(None, headless='on'))
        self.assertRaises(TypeError, lambda: _syck.Emitter(None, use_header='on'))
        self.assertRaises(TypeError, lambda: _syck.Emitter(None, use_version='on'))
        self.assertRaises(TypeError, lambda: _syck.Emitter(None, explicit_typing='on'))
        self.assertRaises(ValueError, lambda: _syck.Emitter(None, style='no_quote'))
        self.assertRaises(TypeError, lambda: _syck.Emitter(None, best_width='100'))
        self.assertRaises(ValueError, lambda: _syck.Emitter(None, best_width=0))
        self.assertRaises(ValueError, lambda: _syck.Emitter(None, best_width=-100))
        self.assertRaises(TypeError, lambda: _syck.Emitter(None, indent='2'))
        self.assertRaises(ValueError, lambda: _syck.Emitter(None, indent=0))
        self.assertRaises(ValueError, lambda: _syck.Emitter(None, indent=-2))

    def testHeadless(self):
        emitter = _syck.Emitter(StringIO.StringIO(), headless=False)
        emitter.emit(CYCLE)
        self.assert_(emitter.output.getvalue().find('---') != -1)
        emitter = _syck.Emitter(StringIO.StringIO(), headless=True)
        emitter.emit(CYCLE)
        self.assert_(emitter.output.getvalue().find('---') == -1)

    def testUseHeader(self):
        emitter = _syck.Emitter(StringIO.StringIO(), headless=True)
        emitter.emit(EXAMPLE)
        self.assert_(emitter.output.getvalue().find('---') == -1)
        emitter = _syck.Emitter(StringIO.StringIO(), use_header=True)
        emitter.emit(EXAMPLE)
        self.assert_(emitter.output.getvalue().find('---') != -1)

    def testExplicitTyping(self):
        pass    # anyway it's Syck's responsibility to interpret correctly the parameters.

class TestExample(unittest.TestCase):

    def testExample(self):
        emitter = _syck.Emitter(StringIO.StringIO())
        emitter.emit(EXAMPLE)
        parser = _syck.Parser(emitter.output.getvalue())
        node = parser.parse()
        self.assertEqual(strip(EXAMPLE), strip(node))

    def testPairs(self):
        emitter = _syck.Emitter(StringIO.StringIO())
        emitter.emit(PAIRS)
        parser = _syck.Parser(emitter.output.getvalue())
        node = parser.parse()
        self.assertEqual(strip(PAIRS), strip(node))

    def testComplexExample(self):
        emitter = _syck.Emitter(StringIO.StringIO())
        emitter.emit(COMPLEX_EXAMPLE)
        parser = _syck.Parser(emitter.output.getvalue())
        node = parser.parse()
        self.assertEqual(strip(COMPLEX_EXAMPLE), strip(node))

    def testDocuments(self):
        emitter = _syck.Emitter(StringIO.StringIO())
        emitter.emit(EXAMPLE)
        emitter.emit(EXAMPLE)
        emitter.emit(EXAMPLE)
        parser = _syck.Parser(emitter.output.getvalue())
        self.assertEqual(strip(EXAMPLE), strip(parser.parse()))
        self.assertEqual(strip(EXAMPLE), strip(parser.parse()))
        self.assertEqual(strip(EXAMPLE), strip(parser.parse()))
        self.assert_(not parser.eof)
        parser.parse()
        self.assert_(parser.eof)

class TestAliases(unittest.TestCase):

    def testAliases(self):
        emitter = _syck.Emitter(StringIO.StringIO())
        emitter.emit(ALIASES)
        parser = _syck.Parser(emitter.output.getvalue())
        node = parser.parse()
        self.assert_(node.value[0] is node.value[1])

class TestTags(unittest.TestCase):

    def testTags(self):
        document = _syck.Seq()
        for tag in TAGS:
            document.value.append(_syck.Scalar('foo', tag=tag))
        emitter = _syck.Emitter(StringIO.StringIO())
        emitter.emit(document)
        parser = _syck.Parser(emitter.output.getvalue())
        document = parser.parse()
        self.assertEqual(len(document.value), len(TAGS))
        for index in range(len(document.value)):
            node = document.value[index]
            self.assertEqual(node.tag, TAGS[index])

class TestInvalidNodes(unittest.TestCase):

    def testRoot(self):
        emitter = _syck.Emitter(StringIO.StringIO())
        self.assertRaises(TypeError, lambda: emitter.emit(INVALID_ROOT))

    def testSeq(self):
        for invalid in INVALID_SEQ:
            emitter = _syck.Emitter(StringIO.StringIO())
            self.assertRaises(TypeError, lambda: emitter.emit(invalid))

    def testMap(self):
        for invalid in INVALID_MAP:
            emitter = _syck.Emitter(StringIO.StringIO())
            self.assertRaises(TypeError, lambda: emitter.emit(invalid))

class TestOutput(unittest.TestCase):

    def testBadOutput(self):
        emitter = _syck.Emitter(None)
        self.assertRaises(AttributeError, lambda: emitter.emit(EXAMPLE))

    def testDouble(self):
        class Stream:
            def __init__(self):
                self.emitter = None
            def write(self, data):
                if self.emitter:
                    self.emitter.emit(EXAMPLE)
        emitter = _syck.Emitter(Stream())
        emitter.output.emitter = emitter
        self.assertRaises(RuntimeError, lambda: emitter.emit(EXAMPLE))

class TestGarbage(unittest.TestCase):

    def testGarbage(self):
        gc.collect()
        output = []
        emitter = _syck.Emitter(output)
        output.append(emitter)
        del output, emitter
        self.assertEqual(gc.collect(), 2)


class TestSyckBugWithTrailingSpace(unittest.TestCase):

    def testSyckBugWithTrailingSpace(self):
        emitter = _syck.Emitter(StringIO.StringIO())
        emitter.emit(_syck.Scalar('foo ', tag="tag:yaml.org,2002:str"))
        parser = _syck.Parser(emitter.output.getvalue())
        self.assertEqual(parser.parse().value, 'foo ')



class TestSyckComplexKeyBugs(unittest.TestCase):

    def testEmptyCollectionKeyBug(self):
        tree1 = _syck.Map({_syck.Map(): _syck.Scalar('foo')})
        self._testTree(tree1)
        tree2 = _syck.Map({_syck.Seq(): _syck.Scalar('foo')})
        self._testTree(tree2)

    def testCollectionWithTagKeyBug(self):
        tree = _syck.Map({_syck.Seq([_syck.Scalar('foo')], tag='x-private:key'):
                _syck.Scalar('bar')})
        self._testTree(tree)

    def testFlowCollectionKeyBug(self):
        tree = _syck.Map({_syck.Seq([_syck.Scalar('foo')], inline=True):
                _syck.Scalar('bar')})
        self._testTree(tree)

    def testEmptyCollectionWithAliasKeyBug(self):
        node = _syck.Map()
        tree = _syck.Map({node: node})
        self._testTree(tree)

    def testScalarWithAliasKeyBug(self):
        node = _syck.Scalar('foo', tag='x-private:bug')
        tree = _syck.Map({node: node})
        self._testTree(tree)

    def _testTree(self, tree):
        emitter = _syck.Emitter(StringIO.StringIO())
        emitter.emit(tree)
        #print emitter.output.getvalue()
        parser = _syck.Parser(emitter.output.getvalue())
        self.assertEqual(strip(tree), strip(parser.parse()))

    def testSyckBugWithComplexKeys(self):
        broken = 0
        for key in COMPLEX_ITEMS:
            for value in COMPLEX_ITEMS:
                node = _syck.Map({key: value})
                emitter = _syck.Emitter(StringIO.StringIO())
                emitter.emit(node)
                parser = _syck.Parser(emitter.output.getvalue())
                self.assertEqual(strip(node), strip(parser.parse()))

