CC=gcc
CFLAGS=-I.
SRC=$(wildcard *.c)
OBJ=$(SRC:.c=.o)

# The name of your executable
TARGET = gfw 

# Compile the program
$(TARGET): $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

# Compile each object file
%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

# Clean up object and executable files
clean:
	rm -f $(OBJ) $(TARGET)
