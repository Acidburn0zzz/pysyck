
#include <Python.h>
#include <syck.h>

/* Python 2.2 compatibility. */

#ifndef PyDoc_STR
#define PyDoc_VAR(name)         static char name[]
#define PyDoc_STR(str)          (str)
#define PyDoc_STRVAR(name, str) PyDoc_VAR(name) = PyDoc_STR(str)
#endif

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC  void
#endif

/* Global objects: _syck.error, 'scalar', 'seq', 'map',
    '1quote', '2quote', 'fold', 'literal', 'plain', '+', '-'. */

static PyObject *PySyck_Error;

static PyObject *PySyck_ScalarKind;
static PyObject *PySyck_SeqKind;
static PyObject *PySyck_MapKind;

static PyObject *PySyck_1QuoteStyle;
static PyObject *PySyck_2QuoteStyle;
static PyObject *PySyck_FoldStyle;
static PyObject *PySyck_LiteralStyle;
static PyObject *PySyck_PlainStyle;

static PyObject *PySyck_StripChomp;
static PyObject *PySyck_KeepChomp;

/* The type _syck.Node. */

PyDoc_STRVAR(PySyckNode_doc,
    "The base Node type\n\n"
    "_syck.Node is an abstract type. It is a base type for _syck.Scalar,\n"
    "_syck.Seq, and _syck.Map. You cannot create an instance of _syck.Node\n"
    "directly. You may use _syck.Node for type checking.\n");

static PyTypeObject PySyckNode_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                          /* ob_size */
    "_syck.Node",                               /* tp_name */
    sizeof(PyObject),                           /* tp_basicsize */
    0,                                          /* tp_itemsize */
    0,                                          /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,     /* tp_flags */
    PySyckNode_doc,                             /* tp_doc */
};

/* The type _syck.Scalar */

PyDoc_STRVAR(PySyckScalar_doc,
    "The Scalar node type\n\n"
    "_syck.Scalar represents a scalar node in Syck parser and emitter\n"
    "graph. A scalar node points to a single string value.\n\n"
    "Attributes:\n\n"
    "kind -- always 'scalar'; read-only\n"
    "value -- the node value, a string\n"
    "tag -- the node tag; a string or None\n"
    "anchor -- the name of the node anchor or None; read-only\n"
    "style -- the node style; None (means literal or plain),\n"
    "         '1quote', '2quote', 'fold', 'literal', 'plain'\n"
    "indent -- indentation, an integer; 0 means default\n"
    "width -- the preferred width; 0 means default\n"
    "chomp -- None (clip), '-' (strip), or '+' (keep)\n");

typedef struct {
    PyObject_HEAD
    PyObject *value;
    PyObject *tag;
    PyObject *anchor;
    enum scalar_style style;
    int indent;
    int width;
    char chomp;
} PySyckScalarObject;

static int
PySyckScalar_clear(PySyckScalarObject *self)
{
    Py_XDECREF(self->value);
    self->value = NULL;
    Py_XDECREF(self->tag);
    self->tag = NULL;
    Py_XDECREF(self->anchor);
    self->anchor = NULL;

    return 0;
}

static int
PySyckScalar_traverse(PySyckScalarObject *self, visitproc visit, void *arg)
{
    if (self->value && visit(self->value, arg) < 0)
        return -1;
    if (self->tag && visit(self->tag, arg) < 0)
        return -1;
    if (self->anchor && visit(self->anchor, arg) < 0)
        return -1;

    return 0;
}

static void
PySyckScalar_dealloc(PySyckScalarObject *self)
{
    PySyckScalar_clear(self);
    self->ob_type->tp_free((PyObject *)self);
}

static PyObject *
PySyckScalar_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PySyckScalarObject *self;

    self = (PySyckScalarObject *)type->tp_alloc(type, 0);
    if (!self) return NULL;

    self->value = PyString_FromString("");
    if (!self->value) {
        Py_DECREF(self);
        return NULL;
    }

    self->tag = NULL;
    self->anchor = NULL;
    self->style = scalar_none;
    self->indent = 0;
    self->width = 0;
    self->chomp = 0;

    return (PyObject *)self;
}

static PyObject *
PySyckScalar_getkind(PySyckScalarObject *self, void *closure)
{
    Py_INCREF(PySyck_ScalarKind);
    return PySyck_ScalarKind;
}

static PyObject *
PySyckScalar_getvalue(PySyckScalarObject *self, void *closure)
{
    Py_INCREF(self->value);
    return self->value;
}

static int
PySyckScalar_setvalue(PySyckScalarObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "cannot delete 'value'");
        return -1;
    }
    if (!PyString_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "'value' must be a string");
        return -1;
    }

    Py_DECREF(self->value);
    Py_INCREF(value);
    self->value = value;

    return 0;
}

static PyObject *
PySyckScalar_gettag(PySyckScalarObject *self, void *closure)
{
    PyObject *value = self->tag ? self->tag : Py_None;
    Py_INCREF(value);
    return value;
}

static int
PySyckScalar_settag(PySyckScalarObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "cannot delete 'tag'");
        return -1;
    }

    if (value == Py_None) {
        Py_XDECREF(self->tag);
        self->tag = NULL;
        return 0;
    }

    if (!PyString_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "'tag' must be a string");
        return -1;
    }

    Py_XDECREF(self->tag);
    Py_INCREF(value);
    self->tag = value;

    return 0;
}

static PyObject *
PySyckScalar_getanchor(PySyckScalarObject *self, void *closure)
{
    PyObject *value = self->anchor ? self->anchor : Py_None;
    Py_INCREF(value);
    return value;
}

static int
PySyckScalar_setanchor(PySyckScalarObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "cannot delete 'anchor'");
        return -1;
    }

    if (value == Py_None) {
        Py_XDECREF(self->anchor);
        self->anchor = NULL;
        return 0;
    }

    if (!PyString_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "'anchor' must be a string");
        return -1;
    }

    Py_XDECREF(self->anchor);
    Py_INCREF(value);
    self->anchor = value;

    return 0;
}

static PyObject *
PySyckScalar_getstyle(PySyckScalarObject *self, void *closure)
{
    PyObject *value;

    switch (self->style) {
        case scalar_1quote: value = PySyck_1QuoteStyle; break;
        case scalar_2quote: value = PySyck_2QuoteStyle; break;
        case scalar_fold: value = PySyck_FoldStyle; break;
        case scalar_literal: value = PySyck_LiteralStyle; break;
        case scalar_plain: value = PySyck_PlainStyle; break;
        default: value = Py_None;
    }

    Py_INCREF(value);
    return value;
}

static int
PySyckScalar_setstyle(PySyckScalarObject *self, PyObject *value, void *closure)
{
    char *str;

    if (!value) {
        PyErr_SetString(PyExc_TypeError, "cannot delete 'style'");
        return -1;
    }

    if (value == Py_None) {
        self->style = scalar_none;
        return 0;
    }

    if (!PyString_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "'style' must be a string or None");
        return -1;
    }

    str = PyString_AsString(value);
    if (!str) return -1;

    if (strcmp(str, "1quote") == 0)
        self->style = scalar_1quote;
    else if (strcmp(str, "2quote") == 0)
        self->style = scalar_2quote;
    else if (strcmp(str, "fold") == 0)
        self->style = scalar_fold;
    else if (strcmp(str, "literal") == 0)
        self->style = scalar_literal;
    else if (strcmp(str, "plain") == 0)
        self->style = scalar_plain;
    else {
        PyErr_SetString(PyExc_TypeError, "unknown 'style'");
        return -1;
    }

    return 0;
}

static PyObject *
PySyckScalar_getindent(PySyckScalarObject *self, void *closure)
{
    return PyInt_FromLong(self->indent);
}

static int
PySyckScalar_setindent(PySyckScalarObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "cannot delete 'indent'");
        return -1;
    }

    if (!PyInt_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "'indent' must be an integer");
        return -1;
    }

    self->indent = PyInt_AS_LONG(value);

    return 0;
}

static PyObject *
PySyckScalar_getwidth(PySyckScalarObject *self, void *closure)
{
    return PyInt_FromLong(self->width);
}

static int
PySyckScalar_setwidth(PySyckScalarObject *self, PyObject *value, void *closure)
{
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "cannot delete 'width'");
        return -1;
    }

    if (!PyInt_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "'width' must be an integer");
        return -1;
    }

    self->width = PyInt_AS_LONG(value);

    return 0;
}

static PyObject *
PySyckScalar_getchomp(PySyckScalarObject *self, void *closure)
{
    PyObject *value;

    switch (self->chomp) {
        case NL_CHOMP: value = PySyck_StripChomp; break;
        case NL_KEEP: value = PySyck_KeepChomp; break;
        default: value = Py_None;
    }

    Py_INCREF(value);
    return value;
}

static int
PySyckScalar_setchomp(PySyckScalarObject *self, PyObject *value, void *closure)
{
    char *str;

    if (!value) {
        PyErr_SetString(PyExc_TypeError, "cannot delete 'chomp'");
        return -1;
    }

    if (value == Py_None) {
        self->chomp = 0;
        return 0;
    }

    if (!PyString_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "'chomp' must be '+', '-', or None");
        return -1;
    }

    str = PyString_AsString(value);
    if (!str) return -1;

    if (strcmp(str, "-") == 0)
        self->chomp = NL_CHOMP;
    else if (strcmp(str, "+") == 0)
        self->chomp = NL_KEEP;
    else {
        PyErr_SetString(PyExc_TypeError, "'chomp' must be '+', '-', or None");
        return -1;
    }

    return 0;
}

static int
PySyckScalar_init(PySyckScalarObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *value = NULL;
    PyObject *tag = NULL;
    PyObject *anchor = NULL;
    PyObject *style = NULL;
    PyObject *indent = NULL;
    PyObject *width = NULL;
    PyObject *chomp = NULL;

    static char *kwdlist[] = {"value", "tag", "anchor",
        "style", "indent", "width", "chomp", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OOOOOOO", kwdlist,
                &value, &tag, &anchor, &style, &indent, &width, &chomp))
        return -1;

    if (value && PySyckScalar_setvalue(self, value, NULL) < 0)
        return -1;

    if (tag && PySyckScalar_settag(self, tag, NULL) < 0)
        return -1;

    if (anchor && PySyckScalar_setanchor(self, anchor, NULL) < 0)
        return -1;

    if (style && PySyckScalar_setstyle(self, style, NULL) < 0)
        return -1;

    if (indent && PySyckScalar_setindent(self, indent, NULL) < 0)
        return -1;

    if (width && PySyckScalar_setwidth(self, width, NULL) < 0)
        return -1;

    if (chomp && PySyckScalar_setchomp(self, chomp, NULL) < 0)
        return -1;

    return 0;
}

static PyGetSetDef PySyckScalar_getsetters[] = {
    {"kind", (getter)PySyckScalar_getkind, NULL,
        "the node kind", NULL},
    {"value", (getter)PySyckScalar_getvalue, (setter)PySyckScalar_setvalue,
        "the node value", NULL},
    {"tag", (getter)PySyckScalar_gettag, (setter)PySyckScalar_settag,
        "the node tag", NULL},
    {"anchor", (getter)PySyckScalar_getanchor, (setter)PySyckScalar_setanchor,
        "the node anchor", NULL},
    {"style", (getter)PySyckScalar_getstyle, (setter)PySyckScalar_setstyle,
        "the node style", NULL},
    {"indent", (getter)PySyckScalar_getindent, (setter)PySyckScalar_setindent,
        "the field indentation", NULL},
    {"width", (getter)PySyckScalar_getwidth, (setter)PySyckScalar_setwidth,
        "the field width", NULL},
    {"chomp", (getter)PySyckScalar_getchomp, (setter)PySyckScalar_setchomp,
        "the chomping method", NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject PySyckScalar_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                          /* ob_size */
    "_syck.Scalar",                             /* tp_name */
    sizeof(PySyckScalarObject),                 /* tp_basicsize */
    0,                                          /* tp_itemsize */
    (destructor)PySyckScalar_dealloc,           /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_HAVE_GC,  /* tp_flags */
    PySyckScalar_doc,                           /* tp_doc */
    (traverseproc)PySyckScalar_traverse,        /* tp_traverse */
    (inquiry)PySyckScalar_clear,                /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    PySyckScalar_getsetters,                    /* tp_getset */
    &PySyckNode_Type,                           /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    (initproc)PySyckScalar_init,                /* tp_init */
    0,                                          /* tp_alloc */
    PySyckScalar_new,                           /* tp_new */
};


/*
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


*/
#if 0
    
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


*/

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

/* PyMODINIT_FUNC - does not work with versions <2.3 */
void
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

#endif

/* The module _syck. */

static PyMethodDef PySyck_methods[] = {
    {NULL}  /* Sentinel */
};

PyDoc_STRVAR(PySyck_doc,
    "The low-level wrapper for the Syck YAML parser and emitter\n\n"
    "Types:\n\n"
    "Node -- the base Node type\n");

PyMODINIT_FUNC
init_syck(void)
{
    PyObject *m;

    if (PyType_Ready(&PySyckNode_Type) < 0)
        return;
    if (PyType_Ready(&PySyckScalar_Type) < 0)
        return;
    
    PySyck_Error = PyErr_NewException("_syck.error", NULL, NULL);
    if (!PySyck_Error) return;

    PySyck_ScalarKind = PyString_FromString("scalar");
    if (!PySyck_ScalarKind) return;
    PySyck_SeqKind = PyString_FromString("seq");
    if (!PySyck_SeqKind) return;
    PySyck_MapKind = PyString_FromString("map");
    if (!PySyck_MapKind) return;

    PySyck_1QuoteStyle = PyString_FromString("1quote");
    if (!PySyck_1QuoteStyle) return;
    PySyck_2QuoteStyle = PyString_FromString("2quote");
    if (!PySyck_2QuoteStyle) return;
    PySyck_FoldStyle = PyString_FromString("fold");
    if (!PySyck_FoldStyle) return;
    PySyck_LiteralStyle = PyString_FromString("literal");
    if (!PySyck_LiteralStyle) return;
    PySyck_PlainStyle = PyString_FromString("plain");
    if (!PySyck_PlainStyle) return;

    PySyck_StripChomp = PyString_FromString("-");
    if (!PySyck_StripChomp) return;
    PySyck_KeepChomp = PyString_FromString("+");
    if (!PySyck_KeepChomp) return;

    m = Py_InitModule3("_syck", PySyck_methods, PySyck_doc);

    Py_INCREF(&PySyckNode_Type);
    if (PyModule_AddObject(m, "Node", (PyObject *)&PySyckNode_Type) < 0)
        return;

    Py_INCREF(&PySyckScalar_Type);
    if (PyModule_AddObject(m, "Scalar", (PyObject *)&PySyckScalar_Type) < 0)
        return;
}


