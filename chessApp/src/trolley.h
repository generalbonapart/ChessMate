#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#define PORT 65432

// #define PI

#ifdef PI
#include <pigpio.h>
#define mag_pin 18  // BCM GPIO 18
#define dirPin 23   // BCM GPIO 23
#define stepPin 24  // BCM GPIO 24
#define dirPin2 4   // BCM GPIO 4
#define stepPin2 25 // BCM GPIO 25
#define motors 13   // Placeholder for motor enable pin
#endif

#define stepsPerRevolution 250
#define stepsPerRevolutionDiag stepsPerRevolution * 2

typedef struct
{
    int startX;
    int startY;
    int endX;
    int endY;
} Move;