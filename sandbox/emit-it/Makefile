
ALL = emit-it complex-key-bug trailing-space-bug

.PHONY: default clean

default: $(ALL)

clean:
	rm -f *.o
	rm -f $(ALL)

%.o: %.c
	gcc -c $< -o $@ -Wall -Wstrict-prototypes -I${HOME}/include

$(ALL): %: %.o
	gcc $< -o $@ -lsyck -L${HOME}/lib -Wall -Wstrict-prototypes
