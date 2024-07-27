CC = gcc
SRCDIR = src
BUILDDIR = build
TARGET = $(BUILDDIR)/trolley

CFLAGS = -Wall
LDFLAGS =

ifdef PI
	CFLAGS += -DPI
	LDFLAGS += -lpigpio -pthread
endif

$(TARGET): $(SRCDIR)/trolley.c
	mkdir -p $(BUILDDIR)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

clean:
	rm -rf $(BUILDDIR)

.PHONY: clean
