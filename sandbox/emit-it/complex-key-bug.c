
#include <stdio.h>

#include <syck.h>

void output_handler(SyckEmitter *e, char *str, long len)
{
    fwrite(str, 1, len, stdout);
}

void emitter_handler(SyckEmitter *e, st_data_t id)
{
    switch (id) {

        case 1:
            syck_emit_map(e, NULL, map_none);
            syck_emit_item(e, 2);
            syck_emit_item(e, 3);
            syck_emit_end(e);
            break;

        case 2:
            syck_emit_map(e, "x-private:key", map_none);
            syck_emit_item(e, 4);
            syck_emit_item(e, 5);
            syck_emit_end(e);
            break;

        case 3:
        case 4:
        case 5:
            syck_emit_scalar(e, NULL, scalar_none, 0, 0, 0, "foo", 3);
            break;
    }
        
}

int main(int argc, char *argv[])
{
    SyckEmitter *e;

    e = syck_new_emitter();
    syck_emitter_handler(e, emitter_handler);
    syck_output_handler(e, output_handler);
    syck_emitter_mark_node(e, 1);
    syck_emitter_mark_node(e, 2);
    syck_emitter_mark_node(e, 3);
    syck_emitter_mark_node(e, 4);
    syck_emitter_mark_node(e, 5);
    syck_emit(e, 1);
    syck_emitter_flush(e, 0);
    syck_free_emitter(e);
}

