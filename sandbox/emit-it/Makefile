
.PHONY: default clean

default: emit-it

clean:
	rm -f emit-it
	rm -f emit-it.o

emit-it: emit-it.o
	gcc emit-it.o -o emit-it -lsyck -L${HOME}/lib -Wall -Wstrict-prototypes

emit-it.o: emit-it.c
	gcc -c emit-it.c -o emit-it.o -I${HOME}/include

