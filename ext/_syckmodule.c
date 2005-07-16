
#include <Python.h>
#include <syck.h>

/* Global objects. */

static PyObject *_syck_Error;

static PyObject *_syck_ScalarKind;
static PyObject *_syck_SeqKind;
static PyObject *_syck_MapKind;

/* Node type. */

typedef struct {
    PyObject_HEAD
    PyObject *kind;
    PyObject *type_id;
    PyObject *value;
} _syck_Node;

static void
_syck_Node_dealloc(_syck_Node *self)
{
    Py_XDECREF(self->kind);
    Py_XDECREF(self->type_id);
    Py_XDECREF(self->value);
    PyObject_Del(self);
}

static PyObject *
_syck_Node_getattr(_syck_Node *self, char *name)
{
    PyObject *value;

    if (strcmp(name, "kind") == 0)
        value = self->kind;
    else if (strcmp(name, "type_id") == 0)
        value = self->type_id;
    else if (strcmp(name, "value") == 0)
        value = self->value;
    else {
        PyErr_SetString(PyExc_AttributeError, name);
        return NULL;
    }

    Py_INCREF(value);
    return value;
}

static char _syck_Node_doc[] =
    "Node object\n"
    "\n"
    "Attributes of the Node object:\n\n"
    "kind -- 'scalar', 'seq', or 'map'.\n"
    "type_id -- the tag of the node.\n"
    "value -- the value of the node, a string, list or dict object.\n";

static PyTypeObject _syck_NodeType = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "_syck.Node",                       /* tp_name */
    sizeof(_syck_Node),                 /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)_syck_Node_dealloc,     /* tp_dealloc */
    0,                                  /* tp_print */
    (getattrfunc)_syck_Node_getattr,    /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_compare */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags */
    _syck_Node_doc,                     /* tp_doc */
};

static PyObject *
_syck_NewNode(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":_syck.Node"))
        return NULL;

    PyErr_SetString(PyExc_TypeError, "Node object cannot be created explicitly. Use _syck.Parser.parse() instead.");
    return NULL;
}

static char _syck_NewNode_doc[] =
    "Node object cannot be created explicitly. Use _syck.Parser.parse() instead.";

static PyObject *
_syck_NewNode_FromValue(char *type_id, PyObject *value) /* Note: steals the reference to the value. */
{
    _syck_Node *self;
    PyObject *kind;

    self = PyObject_NEW(_syck_Node, &_syck_NodeType);
    if (!self) {
        Py_XDECREF(value);
        return NULL;
    }

    self->value = value;

    if (PyList_Check(value))
        kind = _syck_SeqKind;
    else if (PyDict_Check(value))
        kind = _syck_MapKind;
    else
        kind = _syck_ScalarKind;
    Py_INCREF(kind);
    self->kind = kind;

    if (type_id) {
        self->type_id = PyString_FromString(type_id);
        if (!self->type_id) {
            Py_DECREF(self);
            return NULL;
        }
    }
    else {
        Py_INCREF(Py_None);
        self->type_id = Py_None;
    }

    return (PyObject *)self;
}

/* Parser type. */

typedef struct {
    PyObject_HEAD
    PyObject *source;
    PyObject *resolver;
    PyObject *symbols;
    int error_state;
    int mark;
    SyckParser *parser;
} _syck_Parser;

static PyObject *
_syck_Parser_parse(_syck_Parser *self, PyObject *args)
{
    SYMID index;
    PyObject *value;

    if (!PyArg_ParseTuple(args, ":parse"))
        return NULL;

    if (!self->parser) {
        PyErr_SetString(PyExc_TypeError, "Parser object is closed");
        return NULL;
    }

    self->symbols = PyList_New(0);
    if (!self->symbols) {
        return NULL;
    }

    index = syck_parse(self->parser);
    if (!self->error_state && !self->parser->eof) {
        value = PyList_GetItem(self->symbols, index-1);
    }

    Py_DECREF(self->symbols);

    if (self->error_state) {
        self->error_state = 0;
        return NULL;
    }

    if (self->parser->eof) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    
    return value;
}

static char _syck_Parser_parse_doc[] =
    "Parses the next document in the YAML stream, return the root Node object or None on EOF.";

static PyObject *
_syck_Parser_parse_documents(_syck_Parser *self, PyObject *args)
{
    SYMID index;
    PyObject *value = NULL;
    PyObject *result = NULL;

    if (!PyArg_ParseTuple(args, ":parse_document"))
        return NULL;

    if (!self->parser) {
        PyErr_SetString(PyExc_TypeError, "Parser object is closed");
        return NULL;
    }

    result = PyList_New(0);
    if (!result) return NULL;

    while (1) {

        self->symbols = PyList_New(0);
        if (!self->symbols) {
            Py_DECREF(result);
            return NULL;
        };

        index = syck_parse(self->parser);

        if (!self->error_state && !self->parser->eof) {
            value = PyList_GetItem(self->symbols, index-1);
            if (!value) {
                Py_DECREF(self->symbols);
                Py_DECREF(result);
                return NULL;
            }
            if (PyList_Append(result, value) < 0) {
                Py_DECREF(self->symbols);
                Py_DECREF(value);
                Py_DECREF(result);
                return NULL;
            }
            Py_DECREF(value);
        }

        Py_DECREF(self->symbols);

        if (self->error_state) {
            self->error_state = 0;
            Py_DECREF(result);
            return NULL;
        }

        if (self->parser->eof) break;
    }

    return result;
}

static char _syck_Parser_parse_documents_doc[] =
    "Parses the entire YAML stream and returns list of documents.";

static PyObject *
_syck_Parser_close(_syck_Parser *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":close"))
        return NULL;

    Py_XDECREF(self->source);
    self->source = NULL;

    if (self->parser) {
        syck_free_parser(self->parser);
    }
    self->parser = NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static char _syck_Parser_close_doc[] =
    "Closes the parser and frees memory";

static PyMethodDef _syck_Parser_methods[] = {
    {"parse",  (PyCFunction)_syck_Parser_parse, METH_VARARGS, _syck_Parser_parse_doc},
    {"parse_documents",  (PyCFunction)_syck_Parser_parse_documents, METH_VARARGS, _syck_Parser_parse_documents_doc},
    {"close",  (PyCFunction)_syck_Parser_close, METH_VARARGS, _syck_Parser_close_doc},
    {NULL}  /* Sentinel */
};

static void
_syck_Parser_dealloc(_syck_Parser *self)
{
    Py_XDECREF(self->source);
    if (self->parser) {
        syck_free_parser(self->parser);
    }
    PyObject_Del(self);
}

static PyObject *
_syck_Parser_getattr(_syck_Parser *self, char *name)
{
    return Py_FindMethod(_syck_Parser_methods, (PyObject *)self, name);
}

static char _syck_Parser_doc[] =
    "_syck.Parser(yaml_string_or_file, implicit_typing=True, taguri_expansion=True) -> Parser object\n"
    "\n"
    "Methods of the Parser object:\n\n"
    "parse() -- Parses the next document in the YAML stream, return the root Node object or None on EOF.\n"
    "parse_documents() -- Parses the entire YAML stream and returns list of documents.\n"
    "close() -- Closes the parser and frees memory.\n";

static PyTypeObject _syck_ParserType = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "_syck.Parser",                     /* tp_name */
    sizeof(_syck_Parser),               /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)_syck_Parser_dealloc,   /* tp_dealloc */
    0,                                  /* tp_print */
    (getattrfunc)_syck_Parser_getattr,  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_compare */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags */
    _syck_Parser_doc,                   /* tp_doc */
};

static long
_syck_Parser_io_file_read(char *buf, SyckIoFile *file, long max_size, long skip)
{
    _syck_Parser *runtime = (_syck_Parser *)file->ptr;

    PyObject *value;

    char *str;
    int length;

    buf[skip] = '\0';

    if (runtime->error_state) {
        return skip;
    }
    
    max_size -= skip;

    value = PyObject_CallMethod(runtime->source, "read", "(i)", max_size);
    if (!value) {
        runtime->error_state = 1;
        return skip;
    }

    if (!PyString_Check(value)) {
        Py_DECREF(value);
        PyErr_SetString(PyExc_TypeError, "file-like object should return a string");
        runtime->error_state = 1;
        
        return skip;
    }

    str = PyString_AS_STRING(value);
    length = PyString_GET_SIZE(value);
    if (!length) {
        Py_DECREF(value);
        return skip;
    }

    if (length > max_size) {
        Py_DECREF(value);
        PyErr_SetString(PyExc_ValueError, "read returns an overly long string");
        runtime->error_state = 1;
        return skip;
    }

    memcpy(buf+skip, str, length);
    length += skip;
    buf[length] = '\0';

    Py_DECREF(value);

    return length;
}

static SYMID
_syck_Parser_node_handler(SyckParser *parser, SyckNode *node)
{
    _syck_Parser *runtime = (_syck_Parser *)parser->bonus;

    SYMID index;
    PyObject *object = NULL;

    PyObject *key, *value, *item;
    int k;

    if (runtime->error_state)
        return 0;

    switch (node->kind) {

        case syck_str_kind:
            object = PyString_FromStringAndSize(node->data.str->ptr,
                    node->data.str->len);
            if (!object) goto error;
            break;

        case syck_seq_kind:
            object = PyList_New(node->data.list->idx);
            if (!object) goto error;
            for (k = 0; k < node->data.list->idx; k++) {
                index = syck_seq_read(node, k);
                item = PyList_GetItem(runtime->symbols, index-1);
                if (!item) goto error;
                Py_INCREF(item);
                PyList_SET_ITEM(object, k, item);
            }
            break;

        case syck_map_kind:
            object = PyDict_New();
            if (!object) goto error;
            for (k = 0; k < node->data.pairs->idx; k++)
            {
                index = syck_map_read(node, map_key, k);
                key = PyList_GetItem(runtime->symbols, index-1);
                if (!key) goto error;
                index = syck_map_read(node, map_value, k);
                value = PyList_GetItem(runtime->symbols, index-1);
                if (!value) goto error;
                if (PyDict_SetItem(object, key, value) < 0)
                    goto error;
            }
            break;
    }

    object = _syck_NewNode_FromValue(node->type_id, object);
    if (!object) goto error;

    if (PyList_Append(runtime->symbols, object) < 0)
        goto error;

    index = PyList_Size(runtime->symbols);
    return index;

error:
    Py_XDECREF(object);
    runtime->error_state = 1;
    return 0;
}

static void
_syck_Parser_error_handler(SyckParser *parser, char *str)
{
    _syck_Parser *runtime = (_syck_Parser *)parser->bonus;
    PyObject *value;

    if (runtime->error_state) return;

    runtime->error_state = 1;

    value = Py_BuildValue("(sii)", str, parser->linect, parser->cursor-parser->lineptr);
    if (value) {
        PyErr_SetObject(_syck_Error, value);
    }
}

static PyObject *
_syck_NewParser(PyObject *self, PyObject *args, PyObject *kwds)
{
    _syck_Parser *parser;
    PyObject *source;
    int implicit_typing = 1;
    int taguri_expansion = 1;

    static char *kwdlist[] = {"source", "implicit_typing", "taguri_expansion", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|ii", kwdlist,
                &source, &implicit_typing, &taguri_expansion))
        return NULL;

    parser = PyObject_NEW(_syck_Parser, &_syck_ParserType);
    if (!parser)
        return NULL;

    Py_INCREF(source);
    parser->source = source;
    parser->error_state = 0;

    parser->parser = syck_new_parser();
    parser->parser->bonus = parser;

    if (PyString_Check(source)) {
        syck_parser_str_auto(parser->parser, PyString_AS_STRING(source), NULL);
    }
    else {
        syck_parser_file(parser->parser, (FILE *)parser, _syck_Parser_io_file_read);
    }
    syck_parser_implicit_typing(parser->parser, implicit_typing);
    syck_parser_taguri_expansion(parser->parser, taguri_expansion);

    syck_parser_handler(parser->parser, _syck_Parser_node_handler);
    syck_parser_error_handler(parser->parser, _syck_Parser_error_handler);
    /*
    syck_parser_bad_anchor_handler(parser, _syck_Parser_bad_anchor_handler);
    */

    return (PyObject *)parser;
}

static char _syck_NewParser_doc[] =
    "Creates a new Parser object.";

/* The module definitions. */

static PyMethodDef _syck_methods[] = {
    {"Node",  (PyCFunction)_syck_NewNode, METH_VARARGS, _syck_NewNode_doc},
    {"Parser",  (PyCFunction)_syck_NewParser, METH_VARARGS|METH_KEYWORDS, _syck_NewParser_doc},
    {NULL}  /* Sentinel */
};

static char _syck_doc[] =
    "This module provides low-level access to the Syck parser and emitter.\n"
    "Do not use this module directly, use the package 'syck' instead.\n";

PyMODINIT_FUNC
init_syck(void)
{
    PyObject *m;

    _syck_NodeType.ob_type = &PyType_Type;
    _syck_ParserType.ob_type = &PyType_Type;

    _syck_Error = PyErr_NewException("_syck.error", NULL, NULL);
    if (!_syck_Error)
        return;

    _syck_ScalarKind = PyString_FromString("scalar");
    if (!_syck_ScalarKind)
        return;
    _syck_SeqKind = PyString_FromString("seq");
    if (!_syck_SeqKind)
        return;
    _syck_MapKind = PyString_FromString("map");
    if (!_syck_MapKind)
        return;

    m = Py_InitModule3("_syck", _syck_methods, _syck_doc);

    Py_INCREF(_syck_Error);
    if (!PyModule_AddObject(m, "error", _syck_Error) < 0)
        return;

    Py_INCREF(&_syck_NodeType);
    if (PyModule_AddObject(m, "NodeType", (PyObject *)&_syck_NodeType) < 0)
        return;

    Py_INCREF(&_syck_ParserType);
    if (PyModule_AddObject(m, "ParserType", (PyObject *)&_syck_ParserType) < 0)
        return;
}

