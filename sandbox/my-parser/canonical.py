
import re, unittest

class Marker(object):

    def __init__(self, source, data, index, length=0):
        self.source = source
        self.data = data
        self.index = index
        self.length = length
        self._line = None
        self._position = None

    def line(self):
        if not self._line:
            self._make_line_position()
        return self._line

    def position(self):
        if not self._position:
            self._make_line_position()
        return self._position

    def _make_line_position(self):
        line_start = self.data.rfind('\n', 0, self.index)+1
        line_end = self.data.find('\n', self.index)+1
        if line_end == 0:
            line_end = len(self.data)
        self._line = (line_start, line_end)
        row = self.data.count('\n', 0, line_start)
        col = self.index-line_start
        self._position = (row, col)

class Error(Exception):

    def __init__(self, message=None, marker=None):
        Exception.__init__(self)
        self.message = message
        if isinstance(marker, list):
            if marker:
                marker = marker[0].marker
            else:
                marker = None
        self.marker = marker

    def __str__(self):
        if self.marker is not None:
            row, col = self.marker.position()
            start, end = self.marker.line()
            error_position = "source \"%s\", line %s, column %s:\n%s\n"  \
                    % (self.marker.source, row+1, col+1, self.marker.data[start:end].rstrip().encode('utf-8'))
            error_pointer = " " * col + "^\n"
        else:
            error_position = ""
            error_pointer = ""
        if self.message is not None:
            error_message = self.message
        else:
            error_message = "YAML error"
        return error_position+error_pointer+error_message

def scanner_rule(pattern):
    def make(function):
        function.pattern = pattern
        return function
    return make

class Token:

    def __init__(self, name, value, marker=None):
        self.name = name
        self.value = value
        self.marker = marker

class YAMLScanner:

    @scanner_rule(r"\s+")
    def WHITESPACE(self, tokens, token):
        pass
            
    @scanner_rule(r"%YAML")
    def DIRECTIVE_NAME(self, tokens, token):
        tokens.append(token)

    @scanner_rule(r"\d+\.\d+")
    def DIRECTIVE_VALUE(self, tokens, token):
        token.value = float(token.value)
        tokens.append(token)

    @scanner_rule(r"---")
    def DOCUMENT_SEPARATOR(self, tokens, token):
        tokens.append(token)

    @scanner_rule(r"\[")
    def SEQ_START(self, tokens, token):
        tokens.append(token)

    @scanner_rule(r"\]")
    def SEQ_END(self, tokens, token):
        tokens.append(token)

    @scanner_rule(r"\{")
    def MAP_START(self, tokens, token):
        tokens.append(token)

    @scanner_rule(r"\}")
    def MAP_END(self, tokens, token):
        tokens.append(token)

    @scanner_rule(r"\?")
    def MAP_KEY(self, tokens, token):
        tokens.append(token)

    @scanner_rule(r":")
    def MAP_VALUE(self, tokens, token):
        tokens.append(token)

    @scanner_rule(r",")
    def COLL_ENTRY(self, tokens, token):
        tokens.append(token)

    @scanner_rule(r"!\S*")
    def TAG(self, tokens, token):
        if token.value == "!":
            token.value = ""
        elif token.value.startswith(r"!<") and token.value.endswith(r">"):
            token.value = token.value[2:-1]
        elif token.value.startswith(r"!!"):
            token.value = "tag:yaml.org,2002:" + token.value[2:]
        tokens.append(token)

    escapes_re = re.compile(r"\\(?P<value>[\\\"abefnrtvNLP_0 ]|x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})", re.U)
    escapes = {
        "\\": u"\\",
        "\"": u"\"",
        " ": u" ",
        "a": u"\x07",
        "b": u"\x08",
        "e": u"\x1B",
        "f": u"\x0C",
        "n": u"\x0A",
        "r": u"\x0D",
        "t": u"\x09",
        "v": u"\x0B",
        "N": u"\u0085",
        "L": u"\u2028",
        "P": u"\u2029",
        "_": u"_",
        "0": u"\x00",
    }

    def escapes_replace(self, match):
        value = match.group('value')
        if len(value) == 1:
            return self.escapes[value]
        else:
            return unichr(int(value[1:], 16))

    @scanner_rule(r"\"(?:[^\"\\]|\\[\\\"abefnrtvNLP_0 ]|\\x[0-9A-Fa-f]{2}|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})*\"")
    def SCALAR(self, tokens, token):
        token.value = self.escapes_re.sub(self.escapes_replace, token.value[1:-1])
        tokens.append(token)

    @scanner_rule(r"&\S+")
    def ANCHOR(self, tokens, token):
        token.value = token.value[1:]
        tokens.append(token)

    @scanner_rule(r"\*\S+")
    def ALIAS(self, tokens, token):
        token.value = token.value[1:]
        tokens.append(token)

    def __init__(self):
        rules = []
        for name, function in vars(self.__class__).items():
            if hasattr(function, 'pattern'):
                rules.append((name, function.pattern))
        patterns = [r'(?P<%s>%s)' % (name, pattern) for name, pattern in rules]
        self.scanner_re = re.compile('|'.join(patterns), re.U)

    def scan(self, source, data):
        data = unicode(data, 'utf-8')
        tokens = []
        index = 0
        while index < len(data):
            match = self.scanner_re.match(data, index)
            if not match:
                raise Error("invalid token", Marker(source, data, index))
            name = match.lastgroup
            value = match.group()
            marker = Marker(source, data, index, len(value))
            token = Token(name, value, marker)
            processor = getattr(self, name)
            processor(tokens, token)
            index += len(value)
        return tokens

class Value:
    def __init__(self, tag, anchor, value):
        self.tag = tag
        self.anchor = anchor
        self.value = value
    def __eq__(self, other):
        return (self.__class__, self.__dict__) == (other.__class__, other.__dict__)

class Scalar(Value):
    pass

class Sequence(Value):
    pass

class Mapping(Value):
    pass

class Alias:
    def __init__(self, link):
        self.link = link
    def __eq__(self, other):
        return (self.__class__, self.__dict__) == (other.__class__, other.__dict__)

class YAMLParser:

    # stream: document*
    def parse_stream(self, tokens):
        documents = []
        while tokens:
            if self.check_token(tokens, ['DIRECTIVE_NAME', 'DOCUMENT_SEPARATOR']):
                documents.append(self.parse_document(tokens))
            else:
                raise Error("document is expected", tokens)
        return documents

    # document: (DIRECTIVE_NAME DIRECTIVE_VALUE)? DOCUMENT_SEPARATOR node?
    def parse_document(self, tokens):
        node = None
        if self.check_token(tokens, ['DIRECTIVE_NAME']):
            self.eat_token(tokens, 'DIRECTIVE_NAME')
            self.eat_token(tokens, 'DIRECTIVE_VALUE')
        self.eat_token(tokens, 'DOCUMENT_SEPARATOR')
        if self.check_token(tokens, ['TAG', 'ANCHOR', 'ALIAS', 'SCALAR', 'SEQ_START', 'MAP_START']):
            node = self.parse_node(tokens)
        return node

    # node: TAG? ANCHOR? (SCALAR|sequence|mapping) | ALIAS")
    def parse_node(self, tokens):
        if self.check_token(tokens, ['ALIAS']):
            return Alias(self.eat_token(tokens, 'ALIAS'))
        else:
            tag = None
            anchor = None
            if self.check_token(tokens, ['TAG']):
                tag = self.eat_token(tokens, 'TAG')
            if self.check_token(tokens, ['ANCHOR']):
                anchor = self.eat_token(tokens, 'ANCHOR')
            if self.check_token(tokens, ['SCALAR']):
                return Scalar(tag, anchor, self.eat_token(tokens, 'SCALAR'))
            elif self.check_token(tokens, ['SEQ_START']):
                return Sequence(tag, anchor, self.parse_sequence(tokens))
            elif self.check_token(tokens, ['MAP_START']):
                return Mapping(tag, anchor, self.parse_mapping(tokens))
            else:
                raise Error("SCALAR, sequence or mapping is expected", tokens)

    # sequence: SEQ_START (node (COLL_ENTRY node)*)? SEQ_END
    def parse_sequence(self, tokens):
        values = []
        self.eat_token(tokens, 'SEQ_START')
        if not self.check_token(tokens, ['SEQ_END']):
            values.append(self.parse_node(tokens))
            while not self.check_token(tokens, ['SEQ_END']):
                self.eat_token(tokens, 'COLL_ENTRY')
                values.append(self.parse_node(tokens))
        self.eat_token(tokens, 'SEQ_END')
        return values

    # mapping: MAP_START (map_entry (COLL_ENTRY map_entry)*)? MAP_END
    def parse_mapping(self, tokens):
        values = []
        self.eat_token(tokens, 'MAP_START')
        if not self.check_token(tokens, ['MAP_END']):
            values.append(self.parse_map_entry(tokens))
            while not self.check_token(tokens, ['MAP_END']):
                self.eat_token(tokens, 'COLL_ENTRY')
                values.append(self.parse_map_entry(tokens))
        self.eat_token(tokens, 'MAP_END')
        return values

    # map_entry: MAP_KEY node MAP_VALUE node
    def parse_map_entry(self, tokens):
        self.eat_token(tokens, 'MAP_KEY')
        key = self.parse_node(tokens)
        self.eat_token(tokens, 'MAP_VALUE')
        value = self.parse_node(tokens)
        return (key, value)

    def check_token(self, tokens, names):
        return tokens and tokens[0].name in names

    def eat_token(self, tokens, name):
        if not tokens:
            raise Error("%s is expected, EOF is found" % name, tokens)
        if tokens and tokens[0].name != name:
            raise Error("%s is expected, %s is found" % (name, tokens[0].name), tokens)
        return tokens.pop(0).value

    def __init__(self):
        self.scanner = YAMLScanner()

    def parse(self, source, data):
        tokens = self.scanner.scan(source, data)
        return self.parse_stream(tokens)

class Test(unittest.TestCase):

    def testScalar(self):
        parser = YAMLParser()
        documents = parser.parse('testScalar', """--- !!str "foo"\n""")
        self.failUnlessEqual(documents, [Scalar('tag:yaml.org,2002:str', None, "foo")])

    def testSequence(self):
        parser = YAMLParser()
        documents = parser.parse('testSequence', """%YAML 1.1\n--- !!seq\n["foo", "bar", "baz"]\n""")
        self.failUnlessEqual(documents, [
            Sequence('tag:yaml.org,2002:seq', None, [
                Scalar(None, None, "foo"),
                Scalar(None, None, "bar"),
                Scalar(None, None, "baz"),
            ])
        ])

    def testMapping(self):
        parser = YAMLParser()
        documents = parser.parse('testMapping', """%YAML 1.1\n--- !!map\n{ ? "foo" : "bar", ? "baz" : "bat" }\n""")
        self.failUnlessEqual(documents, [
            Mapping('tag:yaml.org,2002:map', None, [
                (Scalar(None, None, "foo"), Scalar(None, None, "bar")),
                (Scalar(None, None, "baz"), Scalar(None, None, "bat")),
            ])
        ])

    def testAlias(self):
        parser = YAMLParser()
        documents = parser.parse('testSequence', """%YAML 1.1\n--- !!seq\n[ &id "foo", *id ]\n""")
        self.failUnlessEqual(documents, [
            Sequence('tag:yaml.org,2002:seq', None, [
                Scalar(None, 'id', "foo"),
                Alias('id'),
            ])
        ])

    def testMultiplyDocuments(self):
        parser = YAMLParser()
        documents = parser.parse('testMultiplyDocuments', """%YAML 1.1\n--- "foo"\n--- "bar"\n--- "baz"\n""")
        self.failUnlessEqual(documents, [
            Scalar(None, None, "foo"),
            Scalar(None, None, "bar"),
            Scalar(None, None, "baz"),
        ])

if __name__ == '__main__':
    unittest.main()

