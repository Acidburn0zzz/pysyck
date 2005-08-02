
import _syck

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

__all__ = ['GenericDumper', 'Dumper',
    'emit', 'dump', 'emit_documents', 'dump_documents']

class GenericDumper(_syck.Emitter):

    def dump(self, object):
        self.emit(self._convert(object, {}))

    def _convert(self, object, object_to_node):
        if id(object) in object_to_node:
            return object_to_node[id(object)]
        node = self.represent(object)
        object_to_node[id(object)] = node
        if node.kind == 'seq':
            for index, item in enumerate(node.value):
                node.value[index] = self._convert(item, object_to_node)
        elif node.kind == 'map':
            for key in node.value.keys():
                value = node.value[key]
                del node.value[key]
                node.value[self._convert(key, object_to_node)] =    \
                        self._convert(value, object_to_node)
        return node

    def represent(self, object):
        if isinstance(object, dict):
            return _syck.Map(object.copy(), tag="tag:yaml.org,2002:map")
        elif isinstance(object, list):
            return _syck.Seq(object[:], tag="tag:yaml.org,2002:seq")
        else:
            return _syck.Scalar(str(object), tag="tag:yaml.org,2002:str")

class Dumper(GenericDumper):

    def represent(self, object):
        return super(Dumper, self).represent(object)

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


