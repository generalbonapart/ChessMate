#include "trolley.h"

// Direction arrays
// CW = 1 CCW = 0 error = -1
// Motor a and b (direction and power)
//            {aDir, bDir, aPower, bPower}
int YDOWN[4] = {1, 1, 1, 1};
int YUP[4] = {0, 0, 1, 1};
int XLEFT[4] = {1, 0, 1, 1};
int XRIGHT[4] = {0, 1, 1, 1};
int DUPR[4] = {0, 0, 1, 0}; // motor A is on motor B is off, last two values
int DUPL[4] = {0, 1, 0, 1};
int DDOWNR[4] = {0, 0, 0, 1};
int DDOWNL[4] = {1, 0, 1, 0};

int currentX, currentY;

#ifdef PI
void gpio_setup()
{
    if (gpioInitialise() < 0)
    {
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

void moveTrolley(int dir[], int steps)
{
    gpioWrite(dirPin, dir[0]);
    gpioWrite(dirPin2, dir[1]);

    for (int x = 0; x < steps; x++)
    {
        if (dir[2])
            gpioWrite(stepPin, PI_HIGH);
        if (dir[3])
            gpioWrite(stepPin2, PI_HIGH);
        gpioDelay(1500); // Delay in microseconds
        if (dir[2])
            gpioWrite(stepPin, PI_LOW);
        if (dir[3])
            gpioWrite(stepPin2, PI_LOW);
        gpioDelay(1500);
    }
}

// Turn magnet on
void magnetOn()
{
    gpioWrite(mag_pin, PI_HIGH);
}

// Turn magnet off
void magnetOff()
{
    gpioWrite(mag_pin, PI_LOW);
}
#endif

void moveTrolleyByN(int dir[], int n, int steps)
{
#ifdef PI
    for (int i = 0; i < n; i++)
    {
        moveTrolley(dir, steps);
        gpioDelay(50000); // Delay in microseconds
    }
#else
    printf("Trolley: Making a move...\n");
    for (int i = 0; i < n; i++)
    {
        usleep(50000); // Delay in microseconds
    }
#endif
}

void moveTrolleyDown(int n)
{
    moveTrolleyByN(YDOWN, n, stepsPerRevolution);
}

void moveTrolleyUp(int n)
{
    moveTrolleyByN(YUP, n, stepsPerRevolution);
}

void moveTrolleyRight(int n)
{
    moveTrolleyByN(XRIGHT, n, stepsPerRevolution);
}

void moveTrolleyLeft(int n)
{
    moveTrolleyByN(XLEFT, n, stepsPerRevolution);
}

void moveTrolleyDiagUL(int n)
{
    moveTrolleyByN(DUPL, n, stepsPerRevolution * 2);
}

void moveTrolleyDiagDL(int n)
{
    moveTrolleyByN(DDOWNL, n, stepsPerRevolution * 2);
}

void moveTrolleyDiagUR(int n)
{
    moveTrolleyByN(DUPR, n, stepsPerRevolution * 2);
}

void moveTrolleyDiagDR(int n)
{
    moveTrolleyByN(DDOWNR, n, stepsPerRevolution * 2);
}

void moveKnight(int deltaX, int deltaY)
{
    if (abs(deltaX) == 2 && abs(deltaY) == 1)
    {
        moveTrolleyByN((deltaY > 0) ? YUP : YDOWN, 1, stepsPerRevolution / 2);
        moveTrolleyByN((deltaX > 0) ? XRIGHT : XLEFT, abs(deltaX), stepsPerRevolution);
        moveTrolleyByN((deltaY > 0) ? YUP : YDOWN, 1, stepsPerRevolution / 2);
    }
    else if (abs(deltaX) == 1 && abs(deltaY) == 2)
    {
        moveTrolleyByN((deltaX > 0) ? XRIGHT : XLEFT, 1, stepsPerRevolution / 2);
        moveTrolleyByN((deltaY > 0) ? YUP : YDOWN, abs(deltaY), stepsPerRevolution);
        moveTrolleyByN((deltaX > 0) ? XRIGHT : XLEFT, 1, stepsPerRevolution / 2);
    }
}

// Function to translate chess notation to Cartesian coordinates
void chessToCartesian(char *chessPosition, Move *move)
{
    // Ensure the input string is in the correct format (e.g., "a1" to "h8")
    if (strlen(chessPosition) != 4)
    {
        fprintf(stderr, "Invalid chess position format: %s\n", chessPosition);
        exit(1);
    }
    if (chessPosition[0] < 'a' || chessPosition[0] > 'h' ||
        chessPosition[1] < '1' || chessPosition[1] > '8')
    {
        fprintf(stderr, "Invalid chess position format: %s\n", chessPosition);
        exit(1);
    }
    if (chessPosition[2] < 'a' || chessPosition[2] > 'h' ||
        chessPosition[3] < '1' || chessPosition[3] > '8')
    {
        fprintf(stderr, "Invalid chess position format: %s\n", chessPosition);
        exit(1);
    }

    // Convert the letter part of the chess notation to x coordinate
    move->startX = chessPosition[0] - 'a';
    move->endX = chessPosition[2] - 'a';
    // Convert the numeric part of the chess notation to y coordinate
    move->startY = (chessPosition[1] - '0') - 1;
    move->endY = (chessPosition[3] - '0') - 1;
}

// Function to calculate movement from one chess square to another
void calculateMovement(int x1, int y1, int x2, int y2)
{
    // Calculate differences in x and y coordinates with respect to the origin (0,0)
    int deltaX = x2 - x1;
    int deltaY = y2 - y1;

    printf("Trolley: DeltaX: %d, DeltaY: %d\n", deltaX, deltaY);
    // Move the trolley based on the calculated displacements
    if ((abs(deltaX) == 2 && abs(deltaY) == 1) || (abs(deltaX) == 1 && abs(deltaY) == 2))
    {
        moveKnight(deltaX, deltaY);
    }
    else if (deltaX == deltaY)
    {
        if (deltaX > 0)
        {
            moveTrolleyDiagUR(deltaX);
        }
        else
        {
            moveTrolleyDiagDL(-deltaX);
        }
    }
    else if (deltaX == -deltaY)
    {
        if (deltaX > 0)
        {
            moveTrolleyDiagUL(deltaX);
        }
        else
        {
            moveTrolleyDiagDR(-deltaX);
        }
    }
    else
    {
        if (deltaX > 0)
        {
            moveTrolleyRight(deltaX);
        }
        else if (deltaX < 0)
        {
            moveTrolleyLeft(-deltaX);
        }

        if (deltaY > 0)
        {
            moveTrolleyUp(deltaY);
        }
        else if (deltaY < 0)
        {
            moveTrolleyDown(-deltaY);
        }
    }
}

void moveChessPiece(Move *move)
{
#ifdef PI
    // Move to the initial target square
    calculateMovement(currentX, currentY, move->startX, move->startY);
    magnetOn();

    calculateMovement(move->startX, move->startY, move->endX, move->endY);
    magnetOff();
#else
    calculateMovement(move->startX, move->startY, move->endX, move->endY);
#endif

    // Update current position
    currentX = move->endX;
    currentY = move->endY;
}

int socket_setup()
{
    int sock = 0;
    struct sockaddr_in serv_addr;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("\n Socket creation error \n");
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    // Convert IPv4 and IPv6 addresses from text to binary form
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0)
    {
        printf("\nInvalid address/ Address not supported \n");
        return -1;
    }

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {
        printf("\nConnection Failed \n");
        return -1;
    }

    return sock;
}

int main()
{
    int sock, len;
    char buffer[1024] = {0};

    currentX = 0;
    currentY = 0; // Assuming starting at a1

// Initialize GPIO setup
#ifdef PI
    gpio_setup();
#endif
    if ((sock = socket_setup()) < 0)
    {
        printf("Socket creation error \n");
        return -1;
    }

    // Run continuously until the user decides to exit
    while (1)
    {
        // Read the move from socket
        len = read(sock, buffer, 1024);
        
        if (len > 0)
        {
            if (buffer[0] == 'q')
            {
                break;
            }
            buffer[len] = '\0'; // Null-terminate the received string
            printf("Trolley: Move to make %s\n", buffer);

            Move move;
            chessToCartesian(buffer, &move);

            // Move the chess piece
            moveChessPiece(&move);
        }
        char message[] = "Done";
        write(sock, message, strlen(message));

    }

    // Return to starting position (a1)
    calculateMovement(currentX, currentY, 0, 0);

#ifdef PI
    gpioTerminate(); // Clean up GPIO resources
#endif

    return 0;
}
