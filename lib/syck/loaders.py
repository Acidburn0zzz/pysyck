
"""
sdgsdf gsfdg sfdg sfd gsdfg
"""

import _syck

import re, datetime, sets

__all__ = ['GenericLoader', 'Loader',
    'parse', 'load', 'parse_documents', 'load_documents']

class GenericLoader(_syck.Parser):
    """
    ssdfg sfdgs dfgsdfgs
    sdfgs dfgsfdgsfgsfdgsfdg sdfg
    """

    def load(self):
        node = self.parse()
        if self.eof:
            return
        return self._convert(node, {})

    def _convert(self, node, node_to_object):
        if node in node_to_object:
            return node_to_object[node]
        value = None
        if node.kind == 'scalar':
            value = node.value
        elif node.kind == 'seq':
            value = []
            for item_node in node.value:
                value.append(self._convert(item_node, node_to_object))
        elif node.kind == 'map':
            value = {}
            for key_node in node.value:
                key_object = self._convert(key_node, node_to_object)
                value_object = self._convert(node.value[key_node],
                        node_to_object)
                if key_object in value:
                    value = None
                    break
                try:
                    value[key_object] = value_object
                except TypeError:
                    value = None
                    break
            if value is None:
                value = []
                for key_node in node.value:
                    key_object = self_convert(key_node, node_to_object)
                    value_object = self._convert(node.value[key_node],
                            node_to_object)
                value.append((key_object, value_object))
        node.value = value
        object = self.construct(node)
        node_to_object[node] = object
        return object

    def construct(self, node):
        return node.value

class Merge:
    pass

class Default:
    pass

class Loader(GenericLoader):

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

    def __init__(self, *args, **kwds):
        super(Loader, self).__init__(*args, **kwds)
        self.tags = {}
        self.add_builtin_types()

    def add_builtin_types(self):
        self.add_builtin_type('null', lambda node: None)
        self.add_builtin_type('bool#yes', lambda node: True)
        self.add_builtin_type('bool#no', lambda node: False)
        self.add_builtin_type('float#fix', lambda node: float(node.value))
        self.add_builtin_type('float#exp', lambda node: float(node.value))
        self.add_builtin_type('float#base60', 'construct_base60_float')
        self.add_builtin_type('float#inf', lambda node: self.inf_value)
        self.add_builtin_type('float#neginf', lambda node: -self.inf_value)
        self.add_builtin_type('float#nan', lambda node: self.nan_value)
        self.add_builtin_type('int', lambda node: int(node.value))
        self.add_builtin_type('int#hex', lambda node: int(node.value, 16))
        self.add_builtin_type('int#oct', lambda node: int(node.value, 8))
        self.add_builtin_type('int#base60', 'construct_base60_int')
        self.add_builtin_type('binary', lambda node: node.value.decode('base64'))
        self.add_builtin_type('timestamp#ymd', 'construct_timestamp')
        self.add_builtin_type('timestamp#iso8601', 'construct_timestamp')
        self.add_builtin_type('timestamp#spaced', 'construct_timestamp')
        self.add_builtin_type('timestamp', 'construct_timestamp')
        self.add_builtin_type('merge', 'construct_merge')
        self.add_builtin_type('default', 'construct_default')
        self.add_builtin_type('omap', 'construct_omap')
        self.add_builtin_type('pairs', 'construct_pairs')
        self.add_builtin_type('set', 'construct_set')

    def add_type(self, type_tag, constuctor):
        self.tags[type_tag] = constructor

    def add_domain_type(self, domain, type_tag, constructor):
        self.tags['tag:%s:%s' % (domain, type_tag)] = constructor

    def add_builtin_type(self, type_tag, constructor):
        self.tags['tag:yaml.org,2002:'+type_tag] = constructor

    def add_python_type(self, type_tag, constructor):
        self.tags['tag:python.yaml.org,2002:'+type_tag] = constructor

    def add_private_type(self, type_tag, constructor):
        self.tags['x-private:'+type_tag] = constructor

    def construct(self, node):
        if node.kind == 'map' and self.merge_key in node.value:
            self.merge_maps(node)
        if node.tag in self.tags:
            constructor = self.tags[node.tag]
            if isinstance(constructor, str):
                constructor = getattr(self, constructor)
            return constructor(node)
        else:
            return node.value

    def construct_base60_float(self, node):
        return self.construct_base60(float, node)

    def construct_base60_int(self, node):
        return self.construct_base60(int, node)

    def construct_base60(self, num_type, node):
        digits = [num_type(part) for part in node.value.split(':')]
        digits.reverse()
        base = 1
        value = num_type(0)
        for digit in digits:
            value += digit*base
            base *= 60
        return value

    def construct_timestamp(self, node):
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

    def construct_merge(self, node):
        return self.merge_key

    def construct_default(self, node):
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

    def construct_omap(self, node):
        omap = []
        for mapping in node.value:
            for key in mapping:
                omap.append((key, mapping[key]))
        return omap

    def construct_pairs(self, node): # Same as construct_omap.
        pairs = []
        for mapping in node.value:
            for key in mapping:
                pairs.append((key, mapping[key]))
        return pairs

    def construct_set(self, node):
        return sets.Set(node.value)

def parse(source):
    """Parses 'source' and returns the root of the 'Node' graph."""
    loader = Loader(source)
    return loader.parse()

def load(source):
    """Parses 'source' and returns the root object."""
    loader = Loader(source)
    return loader.load()

def parse_documents(source):
    """Iterates over 'source' and yields the root node of each document."""
    loader = Loader(source)
    while True:
        node = loader.parse()
        if loader.eof:
            break
        yield node

def load_documents(source):
    """Iterates over 'source' and yields the root object of each document."""
    loader = Loader(source)
    while True:
        object = loader.load()
        if loader.eof:
            break
        yield object

