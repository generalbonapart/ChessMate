#ifndef __LONG_H
#define __LONG_H

#include <stdint.h>
#include <stdio.h>

void make_move(int Side, char *output_move);
void parse_move(int Side, uint8_t *InBuf);
void start_game();

#endif
