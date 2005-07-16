
#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <error.h>
#include <string.h>

#include <syck.h>

#define USAGE   \
    "Usage:\n"  \
    "\tsyck-parser filename [implicit_typing [taguri_expansion]]\n"   \
    "where implicit_typing and taguri_expansion equal 1 or 0 (default: 1)\n"

#define INDENT "  "

SyckNode *copy_node(SyckNode *n)
{
    SyckNode *m;
    long i;

    switch (n->kind) {
        case syck_str_kind:
            m = syck_new_str2(n->data.str->ptr, n->data.str->len, n->data.str->style);
            break;
        case syck_seq_kind:
            m = syck_alloc_seq();
            for (i = 0; i < syck_seq_count(n); i++) {
                syck_seq_add(m, syck_seq_read(n, i));
            }
            break;
        case syck_map_kind:
            m = syck_alloc_map();
            for (i = 0; i < syck_map_count(n); i++) {
                syck_map_add(m, syck_map_read(n, map_key, i), syck_map_read(n, map_value, i));
            }
            break;
    }

    if (n->type_id) {
        m->type_id = strdup(n->type_id);
    }
/*    else {
        m->type_id = strdup("");
    }*/
    if (n->anchor) {
        m->anchor = strdup(n->anchor);
    }
/*    else {
        m->anchor = strdup("");
    }*/

    return m;
}

void release(SyckParser *p, SYMID id)
{
    SyckNode *n;
    int i;
    
    syck_lookup_sym(p, id, (char **)&n);

    switch (n->kind) {
        case syck_seq_kind:
            for (i = 0; i < syck_seq_count(n); i++) {
                release(p, syck_seq_read(n, i));
            }
            break;
        case syck_map_kind:
            for (i = 0; i < syck_map_count(n); i++) {
                release(p, syck_map_read(n, map_key, i));
                release(p, syck_map_read(n, map_value, i));
            }
            break;
    }
    syck_free_node(n);
}

SYMID node_handler(SyckParser *p, SyckNode *n)
{
    SyckNode *m = copy_node(n);
    SYMID id = syck_add_sym(p, (char *)m);
    
    m->id = id;
    return id;
}

void error_handler(SyckParser *p, char *str)
{
    errx(1, "Error handler is not implemented");
}

SyckNode *bad_anchor_handler(SyckParser *p, char *anchor)
{
    errx(1, "Bad anchor handler is not implemented");
    return NULL;
}

void output(int indent, const char *template, ...)
{
    va_list ap;
    int k;

    for (k = 0; k < indent; k++) {
        printf(INDENT);
    }

    va_start(ap, template);
    vprintf(template, ap);
    va_end(ap);

    printf("\n");
}

void traverse(SyckParser *p, int indent, SYMID id)
{
    SyckNode *n;

    int i;
    
    syck_lookup_sym(p, id, (char **)&n);

    switch (n->kind) {
        case syck_str_kind:
            output(indent, "Node Scalar (%s):", n->type_id);
            output(indent+1, "Value: '%s'", n->data.str->ptr);
            break;
        case syck_seq_kind:
            output(indent, "Node Sequence (%s):", n->type_id);
            for (i = 0; i < syck_seq_count(n); i++) {
                output(indent+1, "Item #%d:", i+1);
                traverse(p, indent+2, syck_seq_read(n, i));
            }
            break;
        case syck_map_kind:
            output(indent, "Node Mapping (%s):", n->type_id);
            for (i = 0; i < syck_map_count(n); i++) {
                output(indent+1, "Key #%d:", i+1);
                traverse(p, indent+2, syck_map_read(n, map_key, i));
                output(indent+1, "Value #%d:", i+1);
                traverse(p, indent+2, syck_map_read(n, map_value, i));
            }
            break;
    }
}

int main(int argc, char *argv[])
{
    FILE *stream;
    SyckParser *p;
    char *filename;
    int implicit_typing;
    int taguri_expansion;
    SYMID document;
    int document_number = 0;

    if (argc <= 1 || argc > 4) {
        fprintf(stderr, USAGE);
        exit(1);
    }
    filename = argv[1];
    implicit_typing = !(argc >= 3 && strcmp(argv[2], "0") == 0);
    taguri_expansion = !(argc >= 4 && strcmp(argv[3], "0") == 0);

    p = syck_new_parser();

    syck_parser_implicit_typing(p, implicit_typing);
    syck_parser_taguri_expansion(p, taguri_expansion);

    stream = fopen(argv[1], "r");
    if (!stream) err(1, "Cannot open file");
    syck_parser_file(p, stream, NULL);

    syck_parser_handler(p, node_handler);
//    syck_parser_error_handler(p, error_handler);
    syck_parser_bad_anchor_handler(p, bad_anchor_handler);

    output(0, "Stream '%s':", argv[1]);
    document = syck_parse(p);
    document_number ++;
    while (!p->eof) {
        output(1, "Document #%d:", document_number);
        traverse(p, 2, document);
        release(p, document);
        document = syck_parse(p);
        document_number ++;
    }
    output(0, "DONE.");

    return 0;
}

