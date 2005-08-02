
import unittest
import syck
import StringIO
import test_emitter

EXAMPLE = {
    'foo': 'bar',
    'sequence': ['alpha', 'beta', 'gamma'],
    'mapping': {'a': 'alpha', 'b': 'beta', 'c': 'gamma'},
}

SIMPLE_EXAMPLE = [
    'Mark McGwire',
    'Sammy Sosa',
    'Ken Griffey',
]

class TestOutput(unittest.TestCase):

    def testStringOutput(self):
        source = syck.dump(EXAMPLE)
        object = syck.load(source)
        self.assertEqual(object, EXAMPLE)

    def testFileOutput(self):
        output = StringIO.StringIO()
        syck.dump(EXAMPLE, output)
        output.seek(0)
        object = syck.load(output)
        self.assertEqual(object, EXAMPLE)

    def testNonsenseOutput(self):
        self.assertRaises(AttributeError, lambda: syck.dump(EXAMPLE, 'output'))

class TestDocuments(unittest.TestCase):

    def _get_examples(self):
        yield EXAMPLE
        yield SIMPLE_EXAMPLE
        yield EXAMPLE

    def testStringOutput(self):
        source = syck.dump_documents(self._get_examples())
        documents = syck.load_documents(source)
        self.assertEqual(list(documents), list(self._get_examples()))
        
    def testFileOutput(self):
        output = StringIO.StringIO()
        syck.dump_documents(self._get_examples(), output)
        output.seek(0)
        documents = syck.load_documents(output)
        self.assertEqual(list(documents), list(self._get_examples()))

class TestEmitter(unittest.TestCase):

    def _get_examples(self):
        yield test_emitter.EXAMPLE
        yield test_emitter.EXAMPLE

    def testStringDocument(self):
        source = syck.emit(test_emitter.EXAMPLE)
        node = syck.parse(source)
        self.assertEqual(test_emitter.strip(test_emitter.EXAMPLE),
                test_emitter.strip(node))

    def testFileDocument(self):
        output = StringIO.StringIO()
        syck.emit_documents(self._get_examples(), output)
        output.seek(0)
        nodes = syck.parse_documents(output)
        self.assertEqual(map(test_emitter.strip, self._get_examples()),
                map(test_emitter.strip, nodes))

