
import _syck, re, datetime, sets

__all__ = ['error', 'GenericParser', 'Parser']

error = _syck.error

class GenericParser:

    implicit_typing = True
    taguri_expansion = True
    eof_value = None

    def resolve(self, node):
        return node

    def load(self, source):
        syck_parser = _syck.Parser(source, self.resolve, self.implicit_typing, self.taguri_expansion)
        value = syck_parser.parse()
        if syck_parser.eof():
            return self.eof_value
        return value

    def load_documents(self, source):
        syck_parser = _syck.Parser(source, self.resolve, self.implicit_typing, self.taguri_expansion)
        while True:
            value = syck_parser.parse()
            if syck_parser.eof():
                break
            yield value

class Merge:
    pass

class Default:
    pass

class Parser(GenericParser):

    inf_value = 1e300000
    nan_value = inf_value/inf_value

    ymd_expr = re.compile(r'(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)')
    timestamp_expr = re.compile(r'(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)'
            r'(?:'
                r'(?:[Tt]|[ \t]+)(?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)'
                r'(?:\.(?P<micro>\d+)?)?'
                r'[ \t]*(?:Z|(?P<zhour>[+-]\d\d)(?::(?P<zminute>\d\d))?)?'
            r')?')

    merge_key = Merge()
    default_key = Default()

    def __init__(self):
        self.tags = {}
        self.add_builtin_types()

    def add_builtin_types(self):
        self.add_builtin_type('null', lambda node: None)
        self.add_builtin_type('bool#yes', lambda node: True)
        self.add_builtin_type('bool#no', lambda node: False)
        self.add_builtin_type('float#fix', lambda node: float(node.value))
        self.add_builtin_type('float#exp', lambda node: float(node.value))
        self.add_builtin_type('float#base60', lambda node: self.transfer_base60(float, node))
        self.add_builtin_type('float#inf', lambda node: self.inf_value)
        self.add_builtin_type('float#neginf', lambda node: -self.inf_value)
        self.add_builtin_type('float#nan', lambda node: self.nan_value)
        self.add_builtin_type('int', lambda node: int(node.value))
        self.add_builtin_type('int#hex', lambda node: int(node.value, 16))
        self.add_builtin_type('int#oct', lambda node: int(node.value, 8))
        self.add_builtin_type('int#base60', lambda node: self.transfer_base60(int, node))
        self.add_builtin_type('binary', lambda node: node.value.decode('base64'))
        self.add_builtin_type('timestamp#ymd', self.transfer_timestamp)
        self.add_builtin_type('timestamp#iso8601', self.transfer_timestamp)
        self.add_builtin_type('timestamp#spaced', self.transfer_timestamp)
        self.add_builtin_type('timestamp', self.transfer_timestamp)
        self.add_builtin_type('merge', self.transfer_merge)
        self.add_builtin_type('default', self.transfer_default)
        self.add_builtin_type('omap', self.transfer_omap)
        self.add_builtin_type('pairs', self.transfer_pairs)
        self.add_builtin_type('set', self.transfer_set)

    def add_type(self, type_tag, transfer):
        self.tags[type_tag] = transfer

    def add_domain_type(self, domain, type_tag, tranfser):
        self.tags['tag:%s:%s' % (domain, type_tag)] = transfer

    def add_builtin_type(self, type_tag, transfer):
        self.tags['tag:yaml.org,2002:'+type_tag] = transfer

    def add_python_type(self, type_tag, transfer):
        self.tags['tag:python.yaml.org,2002:'+type_tag] = transfer

    def add_private_type(self, type_tag, transfer):
        self.tags['x-private:'+type_tag] = transfer

    def resolve(self, node):
        if node.kind == 'map' and self.merge_key in node.value:
            self.merge_maps(node)
        if node.type_id in self.tags:
            return self.tags[node.type_id](node)
        else:
            return node.value

    def transfer_float_base60(self, node):
        digits = [float(part) for part in node.value.split(':')]
        digits.reverse()
        base = 1
        value = 0.0
        for digit in digits:
            value += digit*base
            base *= 60
        return value

    def transfer_base60(self, num_type, node):
        digits = [num_type(part) for part in node.value.split(':')]
        digits.reverse()
        base = 1
        value = num_type(0)
        for digit in digits:
            value += digit*base
            base *= 60
        return value

    def transfer_timestamp(self, node):
        match = self.timestamp_expr.match(node.value)
        values = match.groupdict()
        for key in values:
            if values[key]:
                values[key] = int(values[key])
            else:
                values[key] = 0
        micro = values['micro']
        if micro:
            while 10*micro < 1000000:
                micro *= 10
        stamp = datetime.datetime(values['year'], values['month'], values['day'],
                values['hour'], values['minute'], values['second'], micro)
        diff = datetime.timedelta(hours=values['zhour'], minutes=values['zminute'])
        return stamp-diff

    def transfer_merge(self, node):
        return self.merge_key

    def transfer_default(self, node):
        return self.default_key

    def merge_maps(self, node):
        maps = node.value[self.merge_key]
        del node.value[self.merge_key]
        if not isinstance(maps, list):
            maps = [maps]
        maps.reverse()
        maps.append(node.value.copy())
        for item in maps:
            node.value.update(item)

    def transfer_omap(self, node):
        omap = []
        for mapping in node.value:
            for key in mapping:
                omap.append((key, mapping[key]))
        return omap

    def transfer_pairs(self, node): # Same as transfer_omap.
        pairs = []
        for mapping in node.value:
            for key in mapping:
                pairs.append((key, mapping[key]))
        return pairs

    def transfer_set(self, node):
        return sets.Set(node.value)

