
#include <Python.h>
#include <syck.h>

static PyMethodDef _syck_methods[] = {
    {NULL}  /* Sentinel */
};

static char _syck_doc[] =
    "This module provides low-level access to the Syck parser and emitter.\n"
    "Do not use this module directly, use the module 'syck' instead.\n";

PyMODINIT_FUNC
init_syck(void)
{
    Py_InitModule3("_syck", _syck_methods, _syck_doc);
}

