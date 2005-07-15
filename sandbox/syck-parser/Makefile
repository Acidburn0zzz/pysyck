
.PHONY: default clean

default: syck-parser

clean:
	rm -f syck-parser
	rm -f syck-parser.o

syck-parser: syck-parser.o
	gcc syck-parser.o -o syck-parser -lsyck -L${HOME}/lib -Wall -Wstrict-prototypes

syck-parser.o: syck-parser.c
	gcc -c syck-parser.c -o syck-parser.o -I${HOME}/include

