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
#define SPR 350        // steps per revolution
#define SPR_CALIBRATE 100 // steps per revolution
#define MAX_LEFT 8
#define MAX_DOWN 8
int calibration = 1;

// Direction arrays
// CW = 1 CCW = 0 error = -1
// Motor a and b (direction and power)
//            {aDir, bDir, aPower, bPower}
 int YDOWN[4]  =   {1, 1, 1, 1};
 int YUP[4]    =   {0, 0, 1, 1};
 int XLEFT[4]  =   {1, 0, 1, 1};
 int XRIGHT[4] =   {0, 1, 1, 1};
 int DUPR[4]   =   {0, 0, 1, 0}; // motor A is on motor B is off, last two values
 int DUPL[4]   =   {0, 1, 0, 1};
 int DDOWNR[4] =   {0, 0, 0, 1}; 
 int DDOWNL[4] =   {1, 0, 1, 0};

void moveTrolleyDiagUR(int steps);
void moveTrolleyDiagDL(int steps);
void moveTrolleyDiagUL(int steps);
void moveTrolleyDiagDR(int steps);
void moveTrolleyRight(int steps);
void moveTrolleyLeft(int steps);
void moveTrolleyUp(int steps);
void moveTrolleyDown(int steps);

 typedef void (*MoveFunc)(int);

 // Define movement functions
MoveFunc diagMoves[4] = {moveTrolleyDiagUR, moveTrolleyDiagDL, moveTrolleyDiagUL, moveTrolleyDiagDR};
MoveFunc straightMovesX[2] = {moveTrolleyRight, moveTrolleyLeft};
MoveFunc straightMovesY[2] = {moveTrolleyUp, moveTrolleyDown};

// Define delta checks for diagonals
int diagDeltaChecks[4][2] = {
    {1, 1},   // UR: deltaX > 0 && deltaY > 0
    {-1, -1}, // DL: deltaX < 0 && deltaY < 0
    {-1, 1},  // UL: deltaX > 0 && deltaY < 0
    {1, -1}   // DR: deltaX < 0 && deltaY > 0
};

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

void moveTrolley(const int dir[], int n) {
    gpioWrite(dirPin, dir[0]);
    gpioWrite(dirPin2, dir[1]);
    int steps = (calibration)?SPR_CALIBRATE:SPR;

    for (int x = 0; x < steps; x++) {
        gpioWrite(stepPin,  dir[2]);
        gpioWrite(stepPin2, dir[3]);
        gpioDelay(1000);

        gpioWrite(stepPin,  0);
        gpioWrite(stepPin2, 0);
        gpioDelay(1000);
    }
}

// currently not in use
void moveTrolleyByN(const int dir[], int n) {
    for (int i = 0; i < n; i++) {
        moveTrolley(dir, n);
        gpioDelay(50000);  // Delay in microseconds
    }
    
}

void moveTrolleyDown(int n) {
    moveTrolleyByN(YDOWN, n);
}

void moveTrolleyUp(int n) {
    moveTrolleyByN(YUP, n);
}

void moveTrolleyRight(int n) {
    moveTrolleyByN(XRIGHT, n);
}

void moveTrolleyLeft(int n) {
    moveTrolleyByN(XLEFT, n);
}

void moveTrolleyDiagUL(int n) {
    moveTrolleyByN(DUPL, n);
}

void moveTrolleyDiagDL(int n) {
    moveTrolleyByN(DDOWNL, n);
}

void moveTrolleyDiagUR(int n) {
    moveTrolleyByN(DUPR, n);
}

void moveTrolleyDiagDR(int n) {
    moveTrolleyByN(DDOWNR, n);
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
    *y = (chessPosition[1] - '0') - 1;
}

// Function to calculate movement from one chess square to another
void calculateMovement(int x1, int y1, int x2, int y2) {
    // Calculate differences in x and y coordinates with respect to the origin (0,0)
    int deltaX = x2 - x1;
    int deltaY = y2 - y1;
    int absDeltaX = abs(deltaX);
    int absDeltaY = abs(deltaY);
    
    printf("DeltaX: %d, DeltaY: %d\n", deltaX, deltaY);
    // Move the trolley based on the calculated displacements

    //Check Diag movenents 
    for (int i = 0; i < 4; i++) {
        if (deltaX == diagDeltaChecks[i][0] * absDeltaX && deltaY == diagDeltaChecks[i][1] * absDeltaY) {
            diagMoves[i](absDeltaX); // Diagonal moves magnitude is same
            return;
        }
    }
    // Check for  X movements
    if (deltaX != 0) {
        straightMovesX[deltaX > 0 ? 0 : 1](absDeltaX);
    }

    // Check for  Y movements
    if (deltaY != 0) {
        straightMovesY[deltaY > 0 ? 0 : 1](absDeltaY);
    }
}

void calibrateTrolley(){
    moveTrolleyLeft(MAX_LEFT);
    moveTrolleyDown(MAX_DOWN);
    calibration = 0;
}

int main() {
    char endSquare[3];
    char exitKey;
    int currentX = 0, currentY = 0;  // Assuming starting at a1 (0,7)

    // Initialize GPIO setup
    setup();

    // Calibrate the board
    calibrateTrolley();
    
    
    // Run continuously until the user decides to exit
    do {
        // Input the ending chess square
        printf("Enter the ending chess square (e.g., a1): ");
        scanf("%s", endSquare);
        
        // Translate chess notation to Cartesian coordinates for the ending square
        int endX, endY;
        chessToCartesian(endSquare, &endX, &endY);

        gpioWrite(mag_pin, PI_HIGH);
        // Calculate and move the trolley based on the movement between squares
        calculateMovement(currentX, currentY, endX, endY);

    	gpioWrite(mag_pin, PI_LOW);
        // Update the current position
        currentX = endX;
        currentY = endY;

    } while (exitKey != 'q');

    // Move back to the starting position (a1)
    printf("Returning to starting position (a1)...\n");
    int startX = 0, startY = 0; // a1 in Cartesian coordinates
    calculateMovement(currentX, currentY, startX, startY);

    gpioTerminate(); // Clean up GPIO resources
    return 0;
}

