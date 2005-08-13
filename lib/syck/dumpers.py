
import _syck

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

__all__ = ['GenericDumper', 'Dumper',
    'emit', 'dump', 'emit_documents', 'dump_documents']

INF = 1e300000
NEGINF = -INF
NAN = INF/INF


class GenericDumper(_syck.Emitter):

    def dump(self, object):
        self.emit(self._convert(object, {}))

    def _convert(self, object, object_to_node):
        if id(object) in object_to_node and self.allow_aliases(object):
            return object_to_node[id(object)][1]
        node = self.represent(object)
        object_to_node[id(object)] = object, node
        if node.kind == 'seq':
            for index, item in enumerate(node.value):
                node.value[index] = self._convert(item, object_to_node)
        elif node.kind == 'map':
            for key in node.value.keys():
                value = node.value[key]
                del node.value[key]
                node.value[self._convert(key, object_to_node)] =    \
                        self._convert(value, object_to_node)
#        # Workaround against a Syck bug:
#        if node.kind == 'scalar' and node.style not in ['1quote', '2quote'] \
#                and node.value and node.value[-1] in [' ', '\t']:
#            node.style = '2quote'
        return node

    def represent(self, object):
        if isinstance(object, dict):
            return _syck.Map(object.copy(), tag="tag:yaml.org,2002:map")
        elif isinstance(object, list):
            return _syck.Seq(object[:], tag="tag:yaml.org,2002:seq")
        else:
            return _syck.Scalar(str(object), tag="tag:yaml.org,2002:str")

    def allow_aliases(self, object):
        return True

class Dumper(GenericDumper):

    def __init__(self, *args, **kwds):
        super(Dumper, self).__init__(*args, **kwds)

    def find_representer(self, object):
        for object_type in type(object).__mro__:
            if object_type.__module__ == '__builtin__':
                name = object_type.__name__
            else:
                name = '%s.%s' % (object_type.__module__, object_type.__name__)
            method = 'represent_' + name.replace('.', '_')
            if hasattr(self, method):
                return getattr(self, method)

    def represent(self, object):
        representer = self.find_representer(object)
        if representer:
            return representer(object)
        else:
            return super(Dumper, self).represent(object)

    def represent_object(self, object):
        return _syck.Scalar(repr(object), tag="tag:yaml.org,2002:str")

    def represent_NoneType(self, object):
        return _syck.Scalar('~', tag="tag:yaml.org,2002:null")

    def represent_bool(self, object):
        return _syck.Scalar(repr(object), tag="tag:yaml.org,2002:bool")

    def represent_str(self, object):
        return _syck.Scalar(str(object), tag="tag:yaml.org,2002:str")

    def represent_list(self, object):
        return _syck.Seq(object[:], tag="tag:yaml.org,2002:seq")

    def represent_dict(self, object):
        return _syck.Map(object.copy(), tag="tag:yaml.org,2002:map")

    def represent_int(self, object):
        return _syck.Scalar(repr(object), tag="tag:yaml.org,2002:int")

    def represent_float(self, object):
        value = repr(object)
        if value == repr(INF):
            value = '.inf'
        elif value == repr(NEGINF):
            value = '-.inf'
        elif value == repr(NAN):
            value = '.nan'
        return _syck.Scalar(value, tag="tag:yaml.org,2002:float")

    def represent_sets_Set(self, object):
        return _syck.Seq(list(object), tag="tag:yaml.org,2002:set")

    def represent_datetime_datetime(self, object):
        return _syck.Scalar(object.isoformat(), tag="tag:yaml.org,2002:timestamp")

    def represent_long(self, object):
        return _syck.Scalar(repr(object), tag="tag:python.yaml.org,2002:long")

    def represent_unicode(self, object):
        return _syck.Scalar(object.encode('utf-8'), tag="tag:python.yaml.org,2002:unicode")

    def represent_tuple(self, object):
        return _syck.Seq(list(object), tag="tag:python.yaml.org,2002:tuple")

    def represent_type(self, object):
        name = '%s.%s' % (object.__module__, object.__name__)
        return _syck.Scalar('', tag="tag:python.yaml.org,2002:name:"+name)
    represent_classobj = represent_type
    represent_function = represent_type
    represent_builtin_function_or_method = represent_type

    def represent_instance(self, object):
        cls = object.__class__
        class_name = '%s.%s' % (cls.__module__, cls.__name__)
        args = ()
        state = {}
        if hasattr(object, '__getinitargs__'):
            args = object.__getinitargs__()
        if hasattr(object, '__getstate__'):
            state = object.__getstate__()
        elif not hasattr(object, '__getinitargs__'):
            state = object.__dict__.copy()
        if not args and isinstance(state, dict):
            return _syck.Map(state.copy(),
                    tag="tag:python.yaml.org,2002:object:"+class_name)
        value = {}
        if args:
            value['args'] = list(args)
        if state or not isinstance(state, dict):
            value['state'] = state
        return _syck.Map(value,
                tag="tag:python.yaml.org,2002:new:"+class_name)

    def represent_object(self, object): # Do you understand this? I don't.
        cls = type(object)
        class_name = '%s.%s' % (cls.__module__, cls.__name__)
        args = ()
        if cls.__reduce__ is type.__reduce__:
            if hasattr(object, '__reduce_ex__'):
                reduce = object.__reduce_ex__(2)
                args = reduce[1][1:]
            else:
                reduce = object.__reduce__()
            if len(reduce) > 2:
                state = reduce[2]
            if state is None:
                state = {}
            if not args and isinstance(state, dict):
                return _syck.Map(state.copy(),
                        tag="tag:python.yaml.org,2002:object:"+class_name)
            if not state and isinstance(state, dict):
                return _syck.Seq(list(args),
                        tag="tag:python.yaml.org,2002:new:"+class_name)
            value = {}
            if args:
                value['args'] = list(args)
            if state or not isinstance(state, dict):
                value['state'] = state
            return _syck.Map(value,
                    tag="tag:python.yaml.org,2002:new:"+class_name)
        else:
            reduce = object.__reduce__()
            cls = reduce[0]
            class_name = '%s.%s' % (cls.__module__, cls.__name__)
            args = reduce[1]
            state = None
            if len(reduce) > 2:
                state = reduce[2]
            if state is None:
                state = {}
            if not state and isinstance(state, dict):
                return _syck.Seq(list(args),
                        tag="tag:python.yaml.org,2002:apply:"+class_name)
            value = {}
            if args:
                value['args'] = list(args)
            if state or not isinstance(state, dict):
                value['state'] = state
            return _syck.Map(value,
                    tag="tag:python.yaml.org,2002:apply:"+class_name)

    def allow_aliases(self, object):
        if object is None or type(object) in [int, bool, float]:
            return False
        if type(object) is str and (not object or object.isalnum()):
            return False
        if type(object) is tuple and not object:
            return False
        return True

def emit(node, output=None, **parameters):
    if output is None:
        dumper = Dumper(StringIO.StringIO(), **parameters)
    else:
        dumper = Dumper(output, **parameters)
    dumper.emit(node)
    if output is None:
        return dumper.output.getvalue()

def dump(object, output=None, **parameters):
    if output is None:
        dumper = Dumper(StringIO.StringIO(), **parameters)
    else:
        dumper = Dumper(output, **parameters)
    dumper.dump(object)
    if output is None:
        return dumper.output.getvalue()

def emit_documents(nodes, output=None, **parameters):
    if output is None:
        dumper = Dumper(StringIO.StringIO(), **parameters)
    else:
        dumper = Dumper(output, **parameters)
    for node in nodes:
        dumper.emit(node)
    if output is None:
        return dumper.output.getvalue()

def dump_documents(objects, output=None, **parameters):
    if output is None:
        dumper = Dumper(StringIO.StringIO(), **parameters)
    else:
        dumper = Dumper(output, **parameters)
    for object in objects:
        dumper.dump(object)
    if output is None:
        return dumper.output.getvalue()


