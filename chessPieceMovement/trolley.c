#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pigpio.h>

#define mag_pin 18    // BCM GPIO 18
#define dirPin 23     // BCM GPIO 23
#define stepPin 24    // BCM GPIO 24
#define dirPin2 4     // BCM GPIO 4
#define stepPin2 25   // BCM GPIO 25
#define motors 13     // Placeholder for motor enable pin
#define stepsPerRevolution 220

const int YDOWN[2] = {0, 1};
const int YUP[2] = {1, 0};
const int XLEFT[2] = {0, 0};
const int XRIGHT[2] = {1, 1};

void setup() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "pigpio initialization failed\n");
        exit(1);
    }

    gpioSetMode(mag_pin, PI_OUTPUT);
    gpioSetMode(stepPin, PI_OUTPUT);
    gpioSetMode(dirPin, PI_OUTPUT);
    gpioSetMode(stepPin2, PI_OUTPUT);
    gpioSetMode(dirPin2, PI_OUTPUT);
    gpioSetMode(motors, PI_OUTPUT);
    gpioWrite(motors, PI_LOW);
}

void moveTrolley(int dir[]) {
    gpioWrite(dirPin, dir[0]);
    gpioWrite(dirPin2, dir[1]);

    for (int x = 0; x < stepsPerRevolution; x++) {
        gpioWrite(stepPin, PI_HIGH);
        gpioWrite(stepPin2, PI_HIGH);
        gpioDelay(1500);  // Delay in microseconds
        gpioWrite(stepPin, PI_LOW);
        gpioWrite(stepPin2, PI_LOW);
        gpioDelay(1500);
    }
}

void moveTrolleyByN(int dir[], int n) {
    for (int i = 0; i < n; i++) {
        moveTrolley(dir);
        gpioDelay(500000);  // Delay in microseconds
    }
}

void moveTrolleyDown() {
    moveTrolley(YDOWN);
}

void moveTrolleyUp() {
    moveTrolley(YUP);
}

void moveTrolleyRight(int n) {
    moveTrolleyByN(XRIGHT, n);
}

void moveTrolleyLeft(int n) {
    moveTrolleyByN(XLEFT, n);
}

void leftDiagUp() {
    for (int x = 0; x < stepsPerRevolution; x++) {
        gpioWrite(dirPin, PI_HIGH);
        gpioWrite(stepPin, PI_HIGH);
        gpioDelay(1500);
        gpioWrite(stepPin, PI_LOW);
        gpioDelay(1500);
    }
}

void leftDiagDown() {
    for (int x = 0; x < stepsPerRevolution; x++) {
        gpioWrite(dirPin, PI_LOW);
        gpioWrite(stepPin, PI_HIGH);
        gpioDelay(1500);
        gpioWrite(stepPin, PI_LOW);
        gpioDelay(1500);
    }
}

// Function to translate chess notation to Cartesian coordinates
void chessToCartesian(char *chessPosition, int *x, int *y) {
    // Ensure the input string is in the correct format (e.g., "a1" to "h8")
    if (strlen(chessPosition) != 2 ||
        chessPosition[0] < 'a' || chessPosition[0] > 'h' ||
        chessPosition[1] < '1' || chessPosition[1] > '8') {
        fprintf(stderr, "Invalid chess position format: %s\n", chessPosition);
        exit(1);
    }

    // Convert the letter part of the chess notation to x coordinate
    *x = chessPosition[0] - 'a';

    // Convert the numeric part of the chess notation to y coordinate
    *y = 8 - (chessPosition[1] - '0');
}

// Function to calculate movement from one chess square to another
void calculateMovement(char *chessSquare1, char *chessSquare2) {
    int x1, y1, x2, y2;
    
    // Translate chess notation to Cartesian coordinates for both squares
    chessToCartesian(chessSquare1, &x1, &y1);
    chessToCartesian(chessSquare2, &x2, &y2);
    
    // Calculate differences in x and y coordinates with respect to the origin (0,0)
    int deltaX = x2 - x1;
    int deltaY = y2 - y1;
    
    // Move the trolley based on the calculated displacements
    if (deltaX > 0) {
        moveTrolleyRight(deltaX);
    } else if (deltaX < 0) {
        moveTrolleyLeft(-deltaX);
    }
    
    if (deltaY > 0) {
        moveTrolleyUp(deltaY);
    } else if (deltaY < 0) {
        moveTrolleyDown(-deltaY);
    }
}

int main() {
    char startSquare[3], endSquare[3];
    char exitKey;

    // Initialize GPIO setup
    setup();

    // Run continuously until the user decides to exit
    do {
        // Input the starting and ending chess squares
        printf("Enter the starting chess square (e.g., a1): ");
        scanf("%s", startSquare);
        
        printf("Enter the ending chess square (e.g., a1): ");
        scanf("%s", endSquare);
        
        // Calculate and move the trolley based on the movement between squares
        calculateMovement(startSquare, endSquare);

        // Prompt the user to exit or continue
        printf("Press 'q' to quit or any other key to continue: ");
        scanf(" %c", &exitKey); // Note: space before %c to consume whitespace

    } while (exitKey != 'q');

    gpioTerminate(); // Clean up GPIO resources
    return 0;
}

