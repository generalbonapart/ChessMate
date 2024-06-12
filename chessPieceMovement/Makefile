CC = gcc
CFLAGS = -Wall -Wextra -pedantic -std=c99
LIBS = -lSDL2 -lSDL2_ttf

SRCS = smartGUI.c
OBJS = $(SRCS:.c=.o)
TARGET = smartGUI

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(TARGET) $(LIBS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	$(RM) $(OBJS) $(TARGET)
