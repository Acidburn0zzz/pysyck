
============================================================
PySyck: Python bindings for the Syck YAML parser and emitter
============================================================

:Author: Kirill Simonov
:Contact: xi@resolvent.net
:Web site: http://pyyaml.org/wiki/PySyck

.. contents::


Overview
========

YAML_ is a data serialization format designed for human readability and
interaction with scripting languages.

Syck_ is an extension for reading and writing YAML in scripting languages. Syck
provides bindings to the Python_ programming language, but they are somewhat
limited and leak memory.

PySyck_ is aimed to update the current Python bindings for Syck. The new
bindings provide a wrapper for the Syck emitter and give access to YAML
representation graphs.

PySyck_ may be used for various tasks, in particular, as a replacement of the
module pickle_.

.. _YAML: http://yaml.org/
.. _Syck: http://whytheluckystiff.net/syck/
.. _Python: http://python.org/
.. _PySyck: http://pyyaml.org/wiki/PySyck
.. _pickle: http://docs.python.org/lib/module-pickle.html


Requirements
============

PySyck requires Syck 0.55 or higher and Python 2.3 or higher.


Installation
============

Please note that Syck 0.55 or higher must be installed. We recommend to use
Syck_ from `the Syck SVN repository`_ together with `my Syck patches`_. For
your convenience, a tarball is provided:
http://pyyaml.org/download/pysyck/syck-0.61+svn232+patches.tar.gz.

If you install PySyck from source, unpack the source tarball and type::

  $ python setup.py install

Windows binaries for Python 2.3 and 2.4 are provided. Windows binaries are
linked against Syck_ statically.

.. _the Syck SVN repository: http://code.whytheluckystiff.net/svn/syck/trunk
.. _my Syck patches: http://pyyaml.org/wiki/SyckPatches


Usage
=====

The documentation is still rough and incomplete. See `the source code`_ for
more information.

.. _the source code: http://pyyaml.org/browser/pysyck/

Quick Example
-------------

::

  >>> from syck import *
  >>> print load("""
  ... - foo
  ... - bar
  ... - baz
  ... """)
  ['foo', 'bar', 'baz']
  >>> print dump(['foo', 'bar', 'baz'])
  ---
  - foo
  - bar
  - baz

Important notice: Do not load a YAML stream from any untrusted source.
Like ``pickle.load``, ``syck.load`` may call an arbitrary Python function.


YAML syntax
-----------

We do not describe the YAML syntax here. Please check http://yaml.org/ for the
reference.

In addition to the tags defined in `the YAML types repository`_, PySyck understands
the following Python-specific tags:

* ``tag:python.yaml.org,2002:none``,
* ``tag:python.yaml.org,2002:bool``,
* ``tag:python.yaml.org,2002:int``,
* ``tag:python.yaml.org,2002:float``,
* ``tag:python.yaml.org,2002:str``,
* ``tag:python.yaml.org,2002:unicode``,
* ``tag:python.yaml.org,2002:list``,
* ``tag:python.yaml.org,2002:tuple``,
* ``tag:python.yaml.org,2002:dict``,
* ``tag:python.yaml.org,2002:name:...``,
* ``tag:python.yaml.org,2002:object:...``,
* ``tag:python.yaml.org,2002:new:...``,
* ``tag:python.yaml.org,2002:apply:...``.

Most of these tags are self-explanatory. The tags ``!python/name:...``,
``!python/object:...``, ``!python/new:...``, and ``!python/apply:...`` are used
for constructing Python functions, classes, and objects. See the sections `Use
Python-specific tags in YAML documents`_ and `Use Python-specific tags to
construct Python objects`_ for some examples.

.. _the YAML types repository: http://yaml.org/type/index.html

Common Tasks
------------

Import the module
~~~~~~~~~~~~~~~~~

::

  >>> from syck import *

or

::

  >>> import syck

Load a document from a string
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> source = "..."
  >>> object = load(source)

Load a document from a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> source = file(..., 'r')
  >>> object = load(source)

Convert a Python object to a YAML document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> object = ...
  >>> document = dump(object)

Dump a Python object to a YAML stream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> object = ...
  >>> output = file(..., 'w')
  >>> dump(object, output)

Format the output YAML stream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> object = ...
  >>> output = file(..., 'w')
  >>> dump(object, output,
  ...     headless=False, use_header=False, use_version=False,
  ...     explicit_typing=True, style=None, best_width=80, indent=2)

Load several documents from a YAML stream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> source = ...
  >>> objects = load_documents(source)
  >>> for object in objects:
  ...     # ...

Create several documents in a YAML stream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> objects = [...]
  >>> output = file(..., 'w')
  >>> dump_documents(objects, output)

Construct a representation tree of a YAML document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> source = ...
  >>> root_node = parse(source)

Convert a representation tree to a YAML document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> scalar_node = Scalar('...', tag='tag:...',
  ...     style='...', indent=.., width=..)
  >>> sequence_node = Seq(list_of_nodes, tag='tag:...', inline=..)
  >>> mapping_node = Map(dictionary_of_nodes, tag='tag:...', inline=..)
  >>> root_node = ...
  >>> output = file(..., 'w')
  >>> emit(root_node, output)

Use PySyck as a pickle replacement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> object = ...
  >>> stream = ...
  >>> dump(object, stream)
  
  >>> stream = ...
  >>> object = load(stream)

Use PySyck to display the structure of a complex object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> object = ...
  >>> print dump(object)

Use PySyck to display a YAML representation graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> source = ...
  >>> node = parse(source)
  >>> print dump(node)

Use Python-specific tags in YAML documents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  --- %YAML:1.0
  - !python/none ''       # You may also use '!null'.
  - !python/bool 'False'  # You may also use '!bool'.
  - !python/int '123'     # You may also use '!int'.
  - !python/long '1234567890'
  - !python/float '123.456789'  # Also '!float'.
  - !python/str 'a string'      # Also '!str'.
  - !python/unicode 'a unicode string encoded in utf-8'
  - !python/list [1, 2, 3]      # The same as '!seq' or no tag.
  - !python/tuple [1, 2, 3]
  - !python/dict { 1: foo, 2: bar } # The same as '!map' or no tag.

Use Python-specific tags to construct functions or classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  --- %YAML:1.0
  - !python/name:package.module.function_name ''
  - !python/name:package.module.class_name ''

Use Python-specific tags to construct Python objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  --- %YAML:1.0
  - !python/object:package.module.type
    attribute1: value1
    attribute2: value2
    # ...
  - !python/new:package.module.type
    - parameter1
    - parameter2
    # ...
  - !python/new:package.module.type
    args: [parameter1, parameter2, ...]
    kwds: {kwd1: val1, kwd2: val2, ...}
    state: {attr1: val1, attr2: val2, ...}
    # ...
  - !python/apply:package.module.function
    - parameter1
    - parameter2
    # ...
  - !python/apply:package.module.function
    args: [parameter1, parameter2, ...]
    kwds: {kwd1: val1, kwd2: val2, ...}
    state: {attr1: val1, attr2: val2, ...}
    # ...

Use application specific tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  >>> class MyClass:
  ...   # ...

  >>> class MyLoader(Loader):
  ...     def construct_private_my_tag(self, node):
  ...         # ...
  ...         return MyClass(...)

  >>> class MyDumper(Dumper):
  ...     def represent_MyDumper(self, object):
  ...         # ...
  ...         return Map(...)

  >>> source = """--- !!my_tag { ... }"""
  >>> my_instance = load(source, Loader=MyLoader)

  >>> my_instance = MyClass(...)
  >>> output = dump(my_instance, Dumper=MyDumper)

Reference
---------

Functions
~~~~~~~~~

``load`` : function
  ``load(source, Loader=Loader, **parameters)``

  The function ``load()`` returns a Python object corresponding to the first
  document in the source. If the source is empty, ``load()`` returns ``None``.
  ``source`` must be a string or a file-like object that has the method
  ``read(max_length)``.

  By default, the function ``load()`` uses an instance of the class ``Loader``
  for parsing. You may use another class or pass additional parameters to the
  class constructor. See the section Parser_ for more details.

  Example::

    >>> load("""
    ... - foo
    ... - bar
    ... - baz
    ... """)
    ['foo', 'bar', 'baz']

``parse`` : function
  ``parse(source, Loader=Loader, **parameters)``

  The function ``parse()`` parses the source and returns a representation tree
  of the first document. ``source`` must be a string or a file-like object
  that has the method ``read(max_length)``.

  By default, the function ``parse()`` uses an instance of the class ``Loader``
  for parsing. You may use another class or pass additional parameters to the
  class constructor. See the section Parser_ for more details.

  Example::

    >>> parse("""
    ... - foo
    ... - bar
    ... - baz
    ... """)
    <_syck.Seq object at 0xb7a3f2fc>

``load_documents`` : function
  ``load_documents(source, Loader=Loader, **parameters)``

  The function ``load_documents()`` parses the source and an iterator.  The
  iterator produces Python objects corresponding the documents of the source
  stream. ``source`` must be a string or a file-like object that has the method
  ``read(max_length)``.

  By default, the function ``load_documents()`` uses an instance of the class
  ``Loader`` for parsing. You may use another class or pass additional
  parameters to the class constructor. See the section Parser_ for more
  details.

  Example::

    >>> source = """
    ... --- >
    ... This is the
    ... first document.
    ... --- >
    ... This is the
    ... next document.
    ... --- >
    ... This is the
    ... last document.
    ... """
    >>> for object in load_documents(source): print object
    ...
    This is the first document.

    This is the next document.

    This is the last document.

``parse_documents`` : function
  ``parse_documents(source, Loader=Loader, **parameters)``

  The function ``parse_documents()`` is similar to ``load_documents()``, but
  produces representation graphs for all documents in the source.
  
``dump`` : function
  ``dump(object, output=None, Dumper=Dumper, **parameters)``

  The function ``dump()`` converts ``object`` to a representation graph
  and write it to ``output``. ``output`` must be ``None`` or a file-like
  object that has the method ``write(data)``. If ``output`` is ``None``,
  ``dump()`` returns the generated document.

  By default, the function ``dump()`` uses an instance of the class ``Dumper``
  for emitting. You may use another class or pass additional parameters to the
  class constructor. See the section Emitter_ for more details.

  Example::

    >>> object = ['foo', 'bar', ['baz']]
    >>> dump(object, sys.stdout)
    ---
    - foo
    - bar
    - - baz
    >>> print dump(object)
    ---
    - foo
    - bar
    - - baz

    >>> print dump(object, use_version=True, indent=5)
    --- %YAML:1.0
    - foo
    - bar
    -    - baz

``emit`` : function
  ``emit(node, output=None, Dumper=Dumper, **parameters)``

  The function ``emit()`` write the representation graph to the output stream.
  ``output`` must be ``None`` or a file-like object that has the method
  ``write(data)``. If ``output`` is ``None``, ``emit()`` returns the generated
  document.

  By default, the function ``emit()`` uses an instance of the class ``Dumper``
  for emitting. You may use another class or pass additional parameters to the
  class constructor. See the section Emitter_ for more details.

  Example::

    >>> foo = Scalar('a string')
    >>> bar = Scalar('a unicode string', tag="tag:python.yaml.org,2002:unicode")
    >>> baz = Scalar('12345', tag="tag:yaml.org,2002:int")
    >>> seq = Seq([foo, bar, baz], tag="tag:python.taml.org,2002:tuple")
    >>> print emit(seq, use_version=True)
    --- %YAML:1.0 !python.taml.org,2002/tuple
    - a string
    - !python/unicode a unicode string
    - 12345

``dump_documents`` : function
  ``dump_documents(objects, output=None, Dumper=Dumper, **parameters)``

  The function ``dump_documents()`` takes a list of objects and converts
  each object to a YAML document. If ``output`` is ``None``, it returns
  the produced documents. Otherwise it writes down them to ``output``,
  which must be a file-like object with the method ``write(data)``.

  By default, the function ``dump_documents()`` uses an instance of the class
  ``Dumper`` for emitting. You may use another class or pass additional
  parameters to the class constructor. See the section Emitter_ for more
  details.

  Example::

    >>> print dump_documents(['foo', 'bar', 'baz'])
    --- foo
    --- bar
    --- baz

``emit_documents`` : function
  ``emit_documents(nodes, output=None, Dumper=Dumper, **parameters)``

  The function ``emit_documents()`` is similar to ``dump_documents()``, but
  it requires a list of representation graphs.

Exceptions
~~~~~~~~~~

``error`` : exception
  This exception is raised by the Syck parser when it detects a syntax error.

  The attribute ``args`` of the exception is a triple: *message*, *row*,
  *column*.

  Example::

    >>> load("""---
    ... - foo
    ... - '''
    ... - bar
    ... """)
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "build/lib.linux-i686-2.3/syck/loaders.py", line 384, in load
      File "build/lib.linux-i686-2.3/syck/loaders.py", line 42, in load
    _syck.error: ('syntax error', 4, 2)

Nodes
~~~~~

The following four classes represents nodes in the YAML representation graph:

``Node`` : class
  ``Node`` is an abstract class; you cannot create an instance of the class
  ``Node``. ``Node`` is the base class of ``Scalar``, ``Seq``, and ``Map``.

``Scalar`` : subclass of ``Node``
  ``Scalar`` represents a scalar node. Its value is a string.

``Seq`` : subclass of ``Node``
  ``Seq`` represents a sequence node. Its value is a list of nodes.

``Map`` : subclass of ``Node``
  ``Map`` represents a mapping node. Its value is a list of pairs or a
  dictionary.

All instances of ``Scalar``, ``Seq``, and ``Map`` have the following
attributes:

``kind`` : string
  ``'scalar'``, ``'seq'``, or ``'map'``; read-only.

``anchor`` : string or ``None``
  The node anchor.

``tag`` : string or ``None``
  The node tag.

``value``
  The node value. For scalar nodes, it should be a string. For sequence nodes,
  it should be a list. For mapping nodes, it should be a list of pairs or a
  dictionary.

``Scalar`` instances have additional attributes:

``style`` : string or ``None``
  The node style. Possible values are ``None`` (means literal or plain),
  ``'1quote'``, ``'2quote'``, ``'fold'``, ``'literal'``, ``'plain'``.

``indent`` : integer
  The node indentation. ``0`` means the default value.

``width`` : integer
  The width of the node field. Longer scalars will be broken on several lines
  to fit the field. ``0`` means the default value.

``chomp`` : string or ``None``
  The chomping method. Possible values are ``None`` (clip), ``'-'`` (strip),
  ``'+'`` (keep).

``Seq`` and ``Map`` instances have an additional attribute:

``inline`` : boolean
  The block/flow flag.

For example, let us create a representation graph and transform it into a YAML
stream::

  >>> # Create three scalar nodes:
  >>> foo = Scalar('foo', tag="tag:example.com,2005:foo", style='fold',
  ...     indent=5)
  >>> bar = Scalar('bar', style='1quote')
  >>> baz = Scalar('baz')

  >>> # Create a sequence node:
  >>> seq = Seq([foo, bar, baz], tag="x-private:seq")

  >>> # Emit it into a YAML stream:
  >>> print emit(seq)
  --- !!seq
  - !example.com,2005/foo >-
       foo
  - 'bar'
  - baz

Now let us construct a representation graph from a YAML document::

  >>> # The function 'parse' generates a representation graph:
  >>> root = parse("""
  ... - foo
  ... - bar
  ... - baz
  ... """)

  >>> # The object 'root' is a sequence node:
  >>> root
  <_syck.Seq object at 0xb7e124b4>

  >>> # We can transform 'root' back into a YAML stream:
  >>> print emit(root)
  ---
  - foo
  - bar
  - baz

  >>> # We can also display the structure of the representation tree using a
  >>> # clever trick:
  >>> print dump(root)
  --- !python/object:_syck.Seq
  value:
  - !python/object:_syck.Scalar
    value: foo
    tag: tag:yaml.org,2002:str
  - !python/object:_syck.Scalar
    value: bar
    tag: tag:yaml.org,2002:str
  - !python/object:_syck.Scalar
    value: baz
    tag: tag:yaml.org,2002:str

Parser
~~~~~~

``Parser`` : class
  The class ``Parser`` is a low-level wrapper of a Syck YAML parser. It can
  generate a representation graph from a YAML stream.

  The class constructor has the following arguments:

  * ``Parser(source, implicit_typing=True, taguri_expansion=True)``.

  The parameter ``source`` is a YAML stream. It must be a string
  or a file-like object. If it is not a string, it should have a
  method named ``read(max_length)`` that returns a string.

  It is not recommended to change the default values of the parameters
  ``implicit_typing`` and ``taguri_expansion``. See the Syck documentation
  for more details about them.

  The class defines a single method:

  * ``Parser.parse()``.

  It parses the source and returns the root node of the corresponding
  representation graph. If the stream is finished, it returns ``None`` and
  set the flag ``eof`` on.

``GenericLoader`` : subclass of ``Parser``
  The subclass ``GenericLoader`` defines two additional methods:

  * ``GenericLoader.load()``,

  * ``GenericLoader.construct(node)``.

  The method ``load()`` parses the source and constructs the corresponding
  Python object. To generate an object by a node, ``load()`` uses the
  ``construct()`` method. The ``construct()`` method defined in
  ``GenericLoader`` just returns the value of the node: a string, a list,
  or a dictionary.

``Loader`` : subclass of ``GenericLoader``
  
  ``Loader`` redefines the method

  * ``Loader.construct(node)``,

  defines an additional method:

  * ``Loader.find_constructor(node)``,

  and add many other auxiliary methods for constructing Python objects.

  ``Loader.construct()`` calls ``find_constructor()`` for the given node,
  and uses the returned constructor to generate a Python object.

  ``Loader.find_constructor()`` determines the constructor of a node by
  the following rules:

  * If the node tag has the form ``tag:yaml.org,2002:type_id``, returns the
    method ``Loader.construct_type_id``.

  * If the node tag has the form ``tag:python.yaml.org,2002:type_id``, returns
    the method ``Loader.construct_python_type_id``.

  * If the node tag has the form ``x-private:type_id``, returns
    ``Loader.construct_private_type_id``.

  * If the node tag has the form ``tag:domain.tld,year:type_id``, returns
    ``Loader.construct_domain_tld_year_type_id``.

  See the source for more details.

Let us show how ``Parser``, ``GenericLoader``, and ``Loader`` parse the same
document::

  >>> # The source stream includes PySyck specific tags '!python/tuple'
  >>> # and '!python/unicode'. It also includes implicitly typed integer
  >>> # '12345'
  >>> source = """--- !python/tuple
  ... - a string
  ... - !python/unicode a unicode string
  ... - 12345
  ... """

  >>> # 'Parser.parse()' returns the root node of the representation tree:
  >>> p = Parser(source)
  >>> print p.parse()
  <_syck.Seq object at 0xb7a33f54>

  >>> # 'GenericLoader.load()' returns a Python object, but ignores the tags:
  >>> gl = GenericLoader(source)
  >>> print gl.load()
  ['a string', 'a unicode string', '12345']

  >>> # 'Loader.load()' is aware of the tags:
  >>> l = Loader(source)
  >>> print l.load()
  ('a string', u'a unicode string', 12345)

Emitter
~~~~~~~

``Emitter`` : class
  The class ``Emitter`` is a low-level wrapper of a Syck YAML emitter. It can
  generate a YAML stream from a representation graph.

  The class constructor has the following signature:

  * ``Emitter(output, headless=False, use_header=False, use_version=False,
    explicit_typing=True, style=None, best_width=80, indent=2)``.

  The parameter ``output`` must be a file-like object that provides a method
  ``write(data)``. The other parameters describe the formatting of the output
  document.

  The class defines a single method:

  * ``emit(node)``.

  The parameter ``node`` must be the root node of a YAML representation graph.
  The method ``emit()`` writes the generated YAML document to the ``output``
  stream.

``GenericDumper`` : subclass of ``Emitter``
  The subclass ``GenericDumper`` adds the following methods:

  * ``GenericDumper.dump(object)``,

  * ``GenericDumper.represent(object)``,

  * ``GenericDumper.allow_aliases(object)``.

  The method ``dump()`` converts the given object into a representation graph,
  generates a YAML document, and writes it to the ``output`` stream. It uses
  the method ``represent()`` to convert an object to a representation node.
  The method ``represent()`` defined in ``GenericDumper`` generates a sequence
  node for a list object and a mapping node for a dictionary object. Otherwise
  it generates a scalar node with the value equal to ``str(object)``.

  The Syck YAML emitter automatically detects if the same object is reffered
  from different parts of the graph and generates aliases for it. Unfortunately
  it does not work well with immutable Python objects such as strings, numbers,
  and tuples. To prevent generating unnecessary aliases, the method
  ``allow_aliases()`` is used. If ``allow_aliases()`` for a given object
  returns ``False``, the alias will never be generated.

  The ``allow_aliases()`` method defined in ``GenericDumper`` always returns
  ``True``.

``Dumper`` : subclass of ``GenericDumper``
  The subclass ``Dumpers`` redefines the methods:

  * ``Dumper.represent(object)``,

  * ``Dumper.allow_aliases(object)``,

  defines the method

  * ``Dumper.find_representer(object)``,

  and add many other auxiliary methods for representing objects as nodes.

  ``Dumper.find_representer()`` finds a method that can represent the given
  object as a node in a representation tree. ``find_representer()`` checks the
  class of the object. If the class has the form ``package.module.type``,
  ``find_representer()`` returns the method
  ``Dumper.represent_package_module_type`` if it exists. If this method does
  not exists, ``find_representer()`` consults its base class, and so on.

  ``Dumper.represent()`` calls ``Dumper.find_representer()`` for the given
  object and uses the returned method to generate a representation node.

  See the source for more details.

Let us show how ``Emitter``, ``GenericDumper``, and ``Dumper`` work::

  >>> # For our demonstration, we define a representation tree named 'seq'
  >>> # and a Python tuple named 'object':
  >>> foo = Scalar('a string')
  >>> bar = Scalar('a unicode string', tag="tag:python.yaml.org,2002:unicode")
  >>> baz = Scalar('12345', tag="tag:yaml.org,2002:int")
  >>> seq = Seq([foo, bar, baz], tag="tag:python.taml.org,2002:tuple")
  >>> object = ('a string', u'a unicode string', 12345)

  >>> # An 'Emitter' instance can dump a representation tree into a stream,
  >>> # but obviously failed to dump a Python object:
  >>> e = Emitter(sys.stdout)
  >>> e.emit(seq)
  --- !python.taml.org,2002/tuple
  - a string
  - !python/unicode a unicode string
  - 12345
  >>> e.emit(object)
  Traceback (most recent call last):
    File "<stdin>", line 1, in ?
  TypeError: Node instance is required

  >>> # A 'GenericDumper' instance dumps almost everything as a scalar:
  >>> gd = GenericDumper(sys.stdout)
  >>> gd.dump(seq)
  --- <_syck.Seq object at 0xb7a3c2fc>
  >>> gd.dump(object)
  --- ('a string', u'a unicode string', 12345)

  >>> # Finally, a 'Dumper' instance dumps a representation tree as a complex
  >>> # Python object:
  >>> d = Dumper(sys.stdout)
  >>> d.dump(seq)
  --- !python/object:_syck.Seq
  value:
  - !python/object:_syck.Scalar
    value: a string
  - !python/object:_syck.Scalar
    value: a unicode string
    tag: tag:python.yaml.org,2002:unicode
  - !python/object:_syck.Scalar
    value: "12345"
    tag: tag:yaml.org,2002:int
  tag: tag:python.taml.org,2002:tuple
  >>> # It also dumps the 'object' object as expected:
  >>> d.dump(object)
  --- !python/tuple
  - a string
  - !python/unicode a unicode string
  - 12345


Development and Bug Reports
===========================

You may check out the PySyck_ source code from `PySyck SVN repository`_.

If you find a bug in PySyck_, please file a bug report to `PySyck BTS`_. You
may review open bugs on `the list of active tickets`_.

You may use `YAML-core mailing list`_ for discussions of PySyck_.

.. _PySyck SVN repository: http://svn.pyyaml.org/pysyck/
.. _PySyck BTS: http://pyyaml.org/newticket?component=pysyck
.. _the list of active tickets: http://pyyaml.org/query?action=view&component=pysyck&order=priority
.. _YAML-core mailing list: http://lists.sourceforge.net/lists/listinfo/yaml-core


Known Bugs
==========

PySyck_ does not support Unicode for real. It is a Syck_ limitation.


History
=======

* PySyck-0.61.2 (2006-03-26):

  - ``ext/_syckmodule.c``: fix a leak in the parser (thanks, jbj).
  - ``setup.py``: set the development status to Production/Stable.

* PySyck-0.61.1 (2006-03-15):

  - ``setup.py``: check if ``syck.h`` is present, complain if it doesn't.
  - ``ext/_syckmodule.c``: release GIL_ before calling Syck_. Note that this
    change broke Python 2.2 compatibility.
  - ``lib/syck/loader.py``, ``lib/syck/dumper.py``: change treatment of the
    ``!str`` tag. Now ``!str``-tagged scalars are converted to Unicode strings
    if they are valid UTF-8, but are not valid ASCII.
  - Windows binaries are compiled against the latest Syck_ from
    `the Syck SVN repository`_ with `my Syck patches`_.
  - The site is moved to http://pyyaml.org/wiki/PySyck.

* PySyck-0.55.1 (2005-08-30): Initial release.

.. _GIL: http://docs.python.org/api/threads.html


Author and Copyright
====================

The PySyck_ module was written by `Kirill Simonov`_.

PySyck_ is released under the BSD license as Syck_ itself.

.. _Kirill Simonov: mailto:xi@resolvent.net

..
  vim: ft=rst:
