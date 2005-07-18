
#include <Python.h>
#include <syck.h>

/* Global objects. */

static PyObject *PySyck_Error;

static PyObject *PySyck_ScalarKind;
static PyObject *PySyck_SeqKind;
static PyObject *PySyck_MapKind;

/* Node type. */

typedef struct {
    PyObject_HEAD
    PyObject *kind;
    PyObject *type_id;
    PyObject *value;
} PySyckNodeObject;

static void
PySyckNode_dealloc(PySyckNodeObject *self)
{
    Py_XDECREF(self->kind);
    Py_XDECREF(self->type_id);
    Py_XDECREF(self->value);
    PyObject_Del(self);
}

static PyObject *
PySyckNode_getattr(PySyckNodeObject *self, char *name)
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

static char PySyckNode_doc[] =
    "Node object\n"
    "\n"
    "Attributes of the Node object:\n\n"
    "kind -- 'scalar', 'seq', or 'map'.\n"
    "type_id -- the tag of the node.\n"
    "value -- the value of the node, a string, list or dict object.\n";

static PyTypeObject PySyckNode_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "_syck.Node",                       /* tp_name */
    sizeof(PySyckNodeObject),           /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)PySyckNode_dealloc,     /* tp_dealloc */
    0,                                  /* tp_print */
    (getattrfunc)PySyckNode_getattr,    /* tp_getattr */
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
    PySyckNode_doc,                     /* tp_doc */
};

static PyObject *
PySyckNode_New(char *type_id, PyObject *value) /* Note: steals the reference to the value. */
{
    PySyckNodeObject *self;
    PyObject *kind;

    self = PyObject_NEW(PySyckNodeObject, &PySyckNode_Type);
    if (!self) {
        Py_XDECREF(value);
        return NULL;
    }

    self->value = value;

    if (PyList_Check(value))
        kind = PySyck_SeqKind;
    else if (PyDict_Check(value))
        kind = PySyck_MapKind;
    else
        kind = PySyck_ScalarKind;
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

static PyObject *
PySyck_Node(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":_syck.Node"))
        return NULL;

    PyErr_SetString(PyExc_TypeError, "Node object cannot be created explicitly. Use _syck.Parser.parse() instead.");
    return NULL;
}

static char PySyck_Node_doc[] =
    "Node object cannot be created explicitly. Use _syck.Parser.parse() instead.";

/* Parser type. */

typedef struct {
    PyObject_HEAD
    PyObject *source;
    PyObject *resolver;
    PyObject *symbols;
    SyckParser *syck;
    int error;
} PySyckParserObject;

static void
PySyckParser_free(PySyckParserObject *parser)
{
    Py_XDECREF(parser->source);
    parser->source = NULL;
    Py_XDECREF(parser->resolver);
    parser->resolver = NULL;
    Py_XDECREF(parser->symbols);
    parser->symbols = NULL;
    if (parser->syck) {
        syck_free_parser(parser->syck);
        parser->syck = NULL;
    }
}

static PyObject *
PySyckParser_parse(PySyckParserObject *parser, PyObject *args)
{
    SYMID index;
    PyObject *value;

    if (!PyArg_ParseTuple(args, ":parse"))
        return NULL;

    if (!parser->syck) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    if (parser->symbols) {
        PyErr_SetString(PyExc_RuntimeError, "do not call Parser.parse while it is running");
        return NULL;
    }

    parser->symbols = PyList_New(0);
    if (!parser->symbols) {
        return NULL;
    }

    index = syck_parse(parser->syck);

    if (parser->error) {
        PySyckParser_free(parser);
        return NULL;
    }

    if (parser->syck->eof) {
        PySyckParser_free(parser);
        Py_INCREF(Py_None);
        return Py_None;
    }

    value = PyList_GetItem(parser->symbols, index);

    Py_DECREF(parser->symbols);
    parser->symbols = NULL;

    return value;
}

static char PySyckParser_parse_doc[] =
    "Parses the next document in the YAML stream, return the root Node object or None on EOF.";

static PyObject *
PySyckParser_eof(PySyckParserObject *parser, PyObject *args)
{
    PyObject *value;

    if (!PyArg_ParseTuple(args, ":eof"))
        return NULL;

    value = parser->syck ? Py_False : Py_True;

    Py_INCREF(value);
    return value;
}

static char PySyckParser_eof_doc[] =
    "Checks if the parser is stopped.";

static PyMethodDef PySyckParser_methods[] = {
    {"parse",  (PyCFunction)PySyckParser_parse, METH_VARARGS, PySyckParser_parse_doc},
    {"eof",  (PyCFunction)PySyckParser_eof, METH_VARARGS, PySyckParser_eof_doc},
    {NULL}  /* Sentinel */
};

static void
PySyckParser_dealloc(PySyckParserObject *parser)
{
    PySyckParser_free(parser);
    PyObject_Del(parser);
}

static PyObject *
PySyckParser_getattr(PySyckParserObject *parser, char *name)
{
    return Py_FindMethod(PySyckParser_methods, (PyObject *)parser, name);
}

static char PySyckParser_doc[] =
    "_syck.Parser(yaml_string_or_file, resolver=None, implicit_typing=True, taguri_expansion=True) -> Parser object\n"
    "\n"
    "Methods of the Parser object:\n\n"
    "parse() -- Parses the next document in the YAML stream, return the root Node object or None on EOF.\n"
    "eof() -- Checks if the parser is stopped.\n";

static PyTypeObject PySyckParser_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "_syck.Parser",                     /* tp_name */
    sizeof(PySyckParserObject),         /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)PySyckParser_dealloc,   /* tp_dealloc */
    0,                                  /* tp_print */
    (getattrfunc)PySyckParser_getattr,  /* tp_getattr */
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
    PySyckParser_doc,                   /* tp_doc */
};

static long
PySyckParser_read_handler(char *buf, SyckIoFile *file, long max_size, long skip)
{
    PySyckParserObject *parser = (PySyckParserObject *)file->ptr;

    PyObject *value;

    char *str;
    int length;

    buf[skip] = '\0';

    if (parser->error) {
        return skip;
    }
    
    max_size -= skip;

    value = PyObject_CallMethod(parser->source, "read", "(i)", max_size);
    if (!value) {
        parser->error = 1;
        return skip;
    }

    if (!PyString_Check(value)) {
        Py_DECREF(value);
        PyErr_SetString(PyExc_TypeError, "file-like object should return a string");
        parser->error = 1;
        
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
        parser->error = 1;
        return skip;
    }

    memcpy(buf+skip, str, length);
    length += skip;
    buf[length] = '\0';

    Py_DECREF(value);

    return length;
}

static SYMID
PySyckParser_node_handler(SyckParser *syck, SyckNode *node)
{
    PySyckParserObject *parser = (PySyckParserObject *)syck->bonus;

    SYMID index;
    PyObject *object = NULL;

    PyObject *key, *value, *item;
    int k;

    if (parser->error)
        return -1;

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
                item = PyList_GetItem(parser->symbols, index);
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
                key = PyList_GetItem(parser->symbols, index);
                if (!key) goto error;
                index = syck_map_read(node, map_value, k);
                value = PyList_GetItem(parser->symbols, index);
                if (!value) goto error;
                if (PyDict_SetItem(object, key, value) < 0)
                    goto error;
            }
            break;
    }

    object = PySyckNode_New(node->type_id, object);
    if (!object) goto error;

    if (parser->resolver) {
        value = PyObject_CallFunction(parser->resolver, "(O)", object);
        if (!value) goto error;
        Py_DECREF(object);
        object = value;
    }

    if (PyList_Append(parser->symbols, object) < 0)
        goto error;

    index = PyList_Size(parser->symbols)-1;
    return index;

error:
    Py_XDECREF(object);
    parser->error = 1;
    return -1;
}

static void
PySyckParser_error_handler(SyckParser *syck, char *str)
{
    PySyckParserObject *parser = (PySyckParserObject *)syck->bonus;
    PyObject *value;

    if (parser->error) return;

    parser->error = 1;

    value = Py_BuildValue("(sii)", str, syck->linect, syck->cursor-syck->lineptr);
    if (value) {
        PyErr_SetObject(PySyck_Error, value);
    }
}

static PyObject *
PySyck_Parser(PyObject *self, PyObject *args, PyObject *kwds)
{
    PySyckParserObject *parser;
    PyObject *source;
    PyObject *resolver = NULL;
    int implicit_typing = 1;
    int taguri_expansion = 1;

    static char *kwdlist[] = {"source", "resolver", "implicit_typing", "taguri_expansion", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|Oii", kwdlist,
                &source, &resolver, &implicit_typing, &taguri_expansion))
        return NULL;

    parser = PyObject_NEW(PySyckParserObject, &PySyckParser_Type);
    if (!parser)
        return NULL;

    parser->error = 0;
    parser->symbols = NULL;

    Py_INCREF(source);
    parser->source = source;

    if (resolver == Py_None)
        resolver = NULL;
    Py_XINCREF(resolver);
    parser->resolver = resolver;

    parser->syck = syck_new_parser();
    parser->syck->bonus = parser;

    if (PyString_Check(source)) {
        syck_parser_str(parser->syck, PyString_AS_STRING(source), PyString_GET_SIZE(source), NULL);
    }
    else {
        syck_parser_file(parser->syck, (FILE *)parser, PySyckParser_read_handler);
    }
    syck_parser_implicit_typing(parser->syck, implicit_typing);
    syck_parser_taguri_expansion(parser->syck, taguri_expansion);

    syck_parser_handler(parser->syck, PySyckParser_node_handler);
    syck_parser_error_handler(parser->syck, PySyckParser_error_handler);
    /*
    syck_parser_bad_anchor_handler(parser, PySyckParser_bad_anchor_handler);
    */

    return (PyObject *)parser;
}

static char PySyck_Parser_doc[] =
    "Creates a new Parser object.";

/* The module definitions. */

static PyMethodDef PySyck_methods[] = {
    {"Node",  (PyCFunction)PySyck_Node, METH_VARARGS, PySyck_Node_doc},
    {"Parser",  (PyCFunction)PySyck_Parser, METH_VARARGS|METH_KEYWORDS, PySyck_Parser_doc},
    {NULL}  /* Sentinel */
};

static char PySyck_doc[] =
    "This module provides low-level access to the Syck parser and emitter.\n"
    "Do not use this module directly, use the package 'syck' instead.\n";

PyMODINIT_FUNC
init_syck(void)
{
    PyObject *m;

    PySyckNode_Type.ob_type = &PyType_Type;
    PySyckParser_Type.ob_type = &PyType_Type;

    PySyck_Error = PyErr_NewException("_syck.error", NULL, NULL);
    if (!PySyck_Error)
        return;

    PySyck_ScalarKind = PyString_FromString("scalar");
    if (!PySyck_ScalarKind)
        return;
    PySyck_SeqKind = PyString_FromString("seq");
    if (!PySyck_SeqKind)
        return;
    PySyck_MapKind = PyString_FromString("map");
    if (!PySyck_MapKind)
        return;

    m = Py_InitModule3("_syck", PySyck_methods, PySyck_doc);

    Py_INCREF(PySyck_Error);
    if (!PyModule_AddObject(m, "error", PySyck_Error) < 0)
        return;

    Py_INCREF(&PySyckNode_Type);
    if (PyModule_AddObject(m, "NodeType", (PyObject *)&PySyckNode_Type) < 0)
        return;

    Py_INCREF(&PySyckParser_Type);
    if (PyModule_AddObject(m, "ParserType", (PyObject *)&PySyckParser_Type) < 0)
        return;
}

