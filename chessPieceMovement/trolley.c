#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gpiod.h>
#include <unistd.h>  // For sleep and usleep
#include <math.h>

#define CONSUMER "gpio_consumer"  // Consumer label for gpiod

const char *chipname = "gpiochip0";  // GPIO chip name, modify if different

// Define GPIO line numbers (BCM numbering)
#define MAG_PIN 18    // BCM GPIO 18
#define DIR_PIN 23    // BCM GPIO 23
#define STEP_PIN 24   // BCM GPIO 24
#define DIR_PIN2 4    // BCM GPIO 4
#define STEP_PIN2 25  // BCM GPIO 25
#define MOTORS 27     // Placeholder for motor enable pin (choose an available GPIO)
#define STEPS_PER_REVOLUTION 220
#define ONE_SQUARE_UNIT 1 // Adjust accordingly 

struct gpiod_chip *chip;
struct gpiod_line *mag_pin, *dir_pin, *step_pin, *dir_pin2, *step_pin2, *motors;

// Direction arrays
// CW = 1 CCW = 0 error = -1
// Motor a and b (direction and power)
//            {aDir, bDir, aPower, bPower}
 int YDOWN[4]  =   {0, 1, 1, 1};
 int YUP[4]    =   {1, 0, 1, 1};
 int XLEFT[4]  =   {0, 0, 1, 1};
 int XRIGHT[4] =   {1, 1, 1, 1};
 int DUPR[4]   =   {1, 0, 1, 0}; // motor A is on motor B is off, last two values
 int DUPL[4]   =   {0, 1, 0, 1};
 int DDOWNR[4] =   {0, 0, 1, 0}; 
 int DDOWNL[4] =   {0, 0, 0, 1};

void setup() {
    // Open GPIO chip
    chip = gpiod_chip_open_by_name(chipname);
    if (!chip) {
        perror("gpiod_chip_open_by_name failed");
        exit(1);
    }

    // Get GPIO lines and set directions
    mag_pin = gpiod_chip_get_line(chip, MAG_PIN);
    step_pin = gpiod_chip_get_line(chip, STEP_PIN);
    dir_pin = gpiod_chip_get_line(chip, DIR_PIN);
    step_pin2 = gpiod_chip_get_line(chip, STEP_PIN2);
    dir_pin2 = gpiod_chip_get_line(chip, DIR_PIN2);
    motors = gpiod_chip_get_line(chip, MOTORS);

    // Set lines as output and initialize low
    gpiod_line_request_output(mag_pin, CONSUMER, 0);
    gpiod_line_request_output(step_pin, CONSUMER, 0);
    gpiod_line_request_output(dir_pin, CONSUMER, 0);
    gpiod_line_request_output(step_pin2, CONSUMER, 0);
    gpiod_line_request_output(dir_pin2, CONSUMER, 0);
    gpiod_line_request_output(motors, CONSUMER, 0);
}

void moveTrolley(int dir[], int delta) {
    gpiod_line_set_value(dir_pin, dir[0]);
    gpiod_line_set_value(dir_pin2, dir[1]);
    int total_steps = delta * STEPS_PER_REVOLUTION * ONE_SQUARE_UNIT; 
    // to move diagnoally the total_steps must be slightly more than X or Y steps because hypotenuse
    for (int x = 0; x < total_steps; x++) {
        gpiod_line_set_value(step_pin, dir[2]);
        gpiod_line_set_value(step_pin2, dir[3]);
        usleep(1500);  // Delay in microseconds
        gpiod_line_set_value(step_pin, 0);
        gpiod_line_set_value(step_pin2, 0);
        usleep(1500);
    }
}




void moveTrolleyDown(int delta) {
    moveTrolley(YDOWN, delta);
}

void moveTrolleyUp(int delta) {
    moveTrolley(YUP, delta);
}

void moveTrolleyRight(int delta) {
    moveTrolley(XRIGHT, delta);
}

void moveTrolleyLeft(int delta) {
    moveTrolley(XLEFT, delta);
}

void moveTrolleyDiagUR(int delta) {
    moveTrolley(DUPR, delta);
}

void moveTrolleyDiagUL(int delta) {
    moveTrolley(DUPL, delta);
}
void moveTrolleyDiagDR(int delta) {
    moveTrolley(DDOWNR, delta);
}
void moveTrolleyDiagDL(int delta) {
    moveTrolley(DDOWNL, delta);
}



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

    //a1 = (0,0) and h8 = (7,7) rows/cols 0 to 7
}

int main() {

    //To run this use: gcc -o trolley trolley.c -lgpiod -lm 

    // plus any additoinal libraries necessary
    setup();

    endSquare[3];
    int moveDiag = 0;
    int currentX = 0, currentY = 0;  // Assuming starting at a1 (0,7)
    char exitKey;

    // Run continuously until the user decides to exit
    do {
        printf("Enter the ending chess square (e.g., a1): ");
        scanf("%s", endSquare);

        printf("Move diagonally?");
        scanf("%d", &moveDiag);

        int endX, endY;        
        chessToCartesian(endSquare, &endX, &endY);

        //handle delta = 0
        int deltaX = endX - currentX;
        int deltaY =  endY - currentY;
        //handle sqrt(0)
        int deltaDiag = sqrt(deltaX * deltaX + deltaY * deltaY) * ONE_SQUARE_UNIT; //maybe floor and ceil function might make it more accurate
    
        if(moveDiag){
            if(deltaX >= 0 && deltaY >= 0){
                // move trolley diag up
                moveTrolleyDiagUR(deltaDiag);
            }
            else if (deltaX < 0 && deltaY >= 0){
                moveTrolleyDiagUL(deltaDiag);
            }
            else if (deltaX >= 0 && deltaY < 0){
                moveTrolleyDiagDR(deltaDiag);
            }
            else if (deltaX < 0 && deltaY < 0){
                moveTrolleyDiagDL(deltaDiag);
            }
            else{
                fprintf(stderr, "Cannot move in any diagonal direction \n");
                exit(1);
            }
        }
        else{
             // if delta = 0 do nothing
            if (deltaX > 0) moveTrolleyRight(deltaX);
            else if (deltaX < 0) moveTrolleyLeft(deltaX);

            if (deltaY > 0) moveTrolleyUp(deltaY);
            else if (deltaY < 0) moveTrolleyDown(deltaY);
        }

        // Update the current position
        currentX = endX;
        currentY = endY;
       
        printf("Press 'q' to quit or any other key to continue: ");
        scanf(" %c", &exitKey);  // Note: space before %c to consume whitespace
    } while (exitKey != 'q');

    // Move back to the starting position (a1)
    printf("Returning to starting position (a1)...\n");
    int startX = 0, startY = 0; // a1 in Cartesian coordinates
    calculateMovement(currentX, currentY, startX, startY);

    // Cleanup
    gpiod_chip_close(chip);

    return 0;
}
