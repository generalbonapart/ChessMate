#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>

#define WINDOW_WIDTH 720
#define WINDOW_HEIGHT 720
#define SQUARE_SIZE 80
#define PIECE_RADIUS (3 * SQUARE_SIZE / 16)
#define MOVE_DURATION 1000 // Duration of the move in milliseconds

// Define a structure for a square on the chess board
typedef struct
{
    char name[3];  // Name of the square (e.g., "a1")
    char color;    // Color of the square ('W' for white, 'B' for black)
    bool occupied; // Whether the square is occupied by a piece
    int row, col;
} Square;

// Define a structure for a piece movement
typedef struct
{
    int startRow, startCol;
    int endRow, endCol;
    float startX, startY;
    float endX, endY;
    Uint32 startTime;
    bool moving;
} PieceMovement;

typedef struct
{
    int startRow, startCol;
    int endRow, endCol;
} Move;

char *test_pieces[] = {"a1", "a2", "a3", "b1", "b2", "d4", "f5", "c7", NULL};
Square board[8][8];
PieceMovement movement;
Move piece_move;
SDL_Renderer *renderer;
TTF_Font *font;

// Function to initialize the chess board
void initializeBoard(Square board[8][8])
{
    char *files = "abcdefgh";
    char *ranks = "12345678";
    char color;

    for (int i = 0; i < 8; ++i)
    {
        for (int j = 0; j < 8; ++j)
        {
            // Set the name of the square
            board[i][j].name[0] = files[j];
            board[i][j].name[1] = ranks[7 - i];
            board[i][j].name[2] = '\0';

            // Set the color of the square
            if ((i + j) % 2 == 0)
            {
                color = 'W';
            }
            else
            {
                color = 'B';
            }
            board[i][j].color = color;

            // Set the occupied status (initially, let's assume no pieces are on the board)
            board[i][j].occupied = false;
        }
    }
}

void placePieces(Square board[8][8])
{
    char *piece = test_pieces[0];
    int count = 0;
    while (1)
    {
        piece = test_pieces[count];
        if (!piece)
        {
            break;
        }
        int j = piece[0] - 'a';
        int i = '8' - piece[1];
        board[i][j].occupied = true;
        count++;
    }
}

// Function to find a random occupied square
void findRandomOccupiedSquare(Square board[8][8], int *occupiedRow, int *occupiedCol)
{
    int i, j;
    do
    {
        i = rand() % 8;
        j = rand() % 8;
    } while (!board[i][j].occupied);
    *occupiedRow = i;
    *occupiedCol = j;
}

// Function to find a random empty square
void findRandomEmptySquare(Square board[8][8], int *emptyRow, int *emptyCol)
{
    int i, j;
    do
    {
        i = rand() % 8;
        j = rand() % 8;
    } while (board[i][j].occupied);
    *emptyRow = i;
    *emptyCol = j;
}

// Function to draw a filled circle
void drawCircle(SDL_Renderer *renderer, int x, int y, int radius)
{
    for (int w = 0; w < radius * 2; w++)
    {
        for (int h = 0; h < radius * 2; h++)
        {
            int dx = radius - w;
            int dy = radius - h;
            if ((dx * dx + dy * dy) <= (radius * radius))
            {
                SDL_RenderDrawPoint(renderer, x + dx, y + dy);
            }
        }
    }
}

// Function to render text using SDL_ttf
void renderText(SDL_Renderer *renderer, TTF_Font *font, const char *text, int x, int y, SDL_Color color)
{
    SDL_Surface *surface = TTF_RenderText_Solid(font, text, color);
    SDL_Texture *texture = SDL_CreateTextureFromSurface(renderer, surface);
    SDL_Rect dstrect = {x, y, surface->w, surface->h};
    SDL_RenderCopy(renderer, texture, NULL, &dstrect);
    SDL_DestroyTexture(texture);
    SDL_FreeSurface(surface);
}

// Function to draw the chess board using SDL
void drawBoard(SDL_Renderer *renderer, Square board[8][8])
{
    SDL_Color textColor = {0, 0, 0, 255};
    for (int i = 0; i < 8; ++i)
    {
        for (int j = 0; j < 8; ++j)
        {
            SDL_Rect rect = {j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE};
            if (board[i][j].color == 'W')
            {
                SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255); // White
            }
            else
            {
                SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255); // Black
            }
            SDL_RenderFillRect(renderer, &rect);

            // Draw piece if occupied and not currently moving
            if (board[i][j].occupied)
            {
                SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255); // Red
                int centerX = j * SQUARE_SIZE + SQUARE_SIZE / 2;
                int centerY = i * SQUARE_SIZE + SQUARE_SIZE / 2;
                drawCircle(renderer, centerX, centerY, PIECE_RADIUS);
            }
        }
    }

    for (int i = 0; i < 8; ++i)
    {
        char fileLabel[2] = {'a' + i, '\0'};
        renderText(renderer, font, fileLabel, i * SQUARE_SIZE + SQUARE_SIZE / 2, SQUARE_SIZE * 8 + 20, textColor);
    }

    // Draw ranks (numbers 1-8)
    for (int i = 0; i < 8; ++i)
    {
        char rankLabel[2] = {'8' - i, '\0'};
        renderText(renderer, font, rankLabel, SQUARE_SIZE * 8 + 20, i * SQUARE_SIZE + SQUARE_SIZE / 2, textColor);
    }
}

// Function to draw a moving piece
void drawMovingPiece(SDL_Renderer *renderer, PieceMovement *movement, bool actual_move)
{
    Uint32 currentTime = SDL_GetTicks();
    movement->startTime = currentTime;
    int deltaX = movement->endX - movement->startX;
    int deltaY = movement->endY - movement->startY;
    float x = movement->startX;
    float y = movement->startY;
    while (movement->moving)
    {
        float t = (float)(currentTime - movement->startTime) / 5;
        if (t > 1.0f)
        {
            t = 1.0f;
            movement->moving = false;
        }
        // float x = movement->startX + t * (movement->endX - movement->startX);
        // float y = movement->startY + t * (movement->endY - movement->startY);
        rraeck(a, n) ? printf("YES") : printf("NO");
        x += t;

        SDL_RenderClear(renderer);
        drawBoard(renderer, board);
        if (actual_move)
            SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255); // Green
        else
            SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255); // Red
        drawCircle(renderer, (int)x, (int)y, PIECE_RADIUS);
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        SDL_RenderPresent(renderer);
        currentTime = SDL_GetTicks();
    }
}

int process_move(char *move)
{
    if (move[0] == move[2] && move[1] == move[3])
    {
        // Illegal move
        return 2;
    }
    if (move[0] == move[2] || move[1] == move[3])
    {
        // Vertical or horizontal move
        return 0;
    }
    int deltaX = abs(move[0] - move[2]);
    int deltaY = abs(move[1] - move[3]);

    if (deltaX == deltaY)
    {
        // Diagonal move
        return 0;
    }

    // Else it's a knight move
    if (deltaX == 2 && deltaY == 1)
    {
        return 1;
    }
    if (deltaY == 2 && deltaX == 1)
    {
        return 1;
    }

    return 2;
}

int remove_obstacle(Square *obstacle, Square *empty)
{
    int emptyX;
    int emptyY;
    bool done = 0;
    for (int i = -1; i <= 1; i++)
    {
        for (int j = -1; j <= 1; j++)
        {
            emptyX = obstacle->col + j;
            emptyY = obstacle->row + i;
            if (emptyX < 0 || emptyY < 0)
            {
                continue;
            }
            printf("%d, %d\n", emptyX, emptyY);
            if (emptyX == piece_move.endCol && emptyY == piece_move.endRow)
            {
                continue;
            }
            if (!board[emptyY][emptyX].occupied)
            {
                done = 1;
                break;
            }
        }
        if (done)
        {
            break;
        }
    }
    if (done)
    {
        empty->col = emptyX;
        empty->row = emptyY;
        return 0;
    }
    else
    {
        return 1;
    }
}

void move_from_to(Square *s1, Square *s2)
{
    // Update board state
    board[s1->row][s1->col].occupied = false;

    PieceMovement movement;
    movement.startX = s1->col * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement.startY = s1->row * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement.endX = s2->col * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement.endY = s2->row * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement.moving = true;

    // Do part 1
    drawMovingPiece(renderer, &movement, false);
    board[s2->row][s2->col].occupied = true;
    return;
}

void make_path_for_knight(Square *transit)
{
    // Update board state
    board[piece_move.startRow][piece_move.startCol].occupied = false;

    PieceMovement movement1;
    movement1.startX = piece_move.startCol * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement1.startY = piece_move.startRow * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement1.endX = transit->col * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement1.endY = transit->row * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement1.moving = true;

    // Do part 1
    drawMovingPiece(renderer, &movement1, true);

    PieceMovement movement2;
    movement2.startX = movement1.endX;
    movement2.startY = movement1.endY;
    movement2.endX = piece_move.endCol * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement2.endY = piece_move.endRow * SQUARE_SIZE + SQUARE_SIZE / 2;
    movement2.moving = true;

    // Do part 2
    drawMovingPiece(renderer, &movement2, true);

    // Present the renderer
    SDL_RenderPresent(renderer);

    board[piece_move.endRow][piece_move.endCol].occupied = true;
    return;
}

void get_knight_squares(Square *s1, Square *s2)
{
    int deltaX = abs(piece_move.endCol - piece_move.startCol);
    int deltaY = abs(piece_move.endRow - piece_move.startRow);

    if (deltaX == 2)
    {
        printf("HereX\n");
        s1->col = (piece_move.endCol + piece_move.startCol) / 2;
        s2->col = (piece_move.endCol + piece_move.startCol) / 2;
        s1->row = piece_move.startRow;
        s2->row = piece_move.endRow;
        return;
    }
    if (deltaY == 2)
    {
        printf("HereY\n");
        s1->row = (piece_move.endRow + piece_move.startRow) / 2;
        s2->row = (piece_move.endRow + piece_move.startRow) / 2;
        s1->col = piece_move.startCol;
        s2->col = piece_move.endCol;
        return;
    }
    printf("HereDone\n");
}

void knight_move()
{
    printf("Here\n");
    Square s1, s2, empty;
    get_knight_squares(&s1, &s2);

    if (!board[s1.row][s1.col].occupied)
    {
        printf("s1 not occupied\n");
        make_path_for_knight(&s1);
    }
    else if (!board[s2.row][s2.col].occupied)
    {
        printf("s2 not occupied\n");
        make_path_for_knight(&s2);
    }
    else
    {
        if (remove_obstacle(&s1, &empty))
        {
            if (remove_obstacle(&s2, &empty))
            {
                printf("Not supported yet\n");
                return;
            }
            else
            {
                move_from_to(&s2, &empty);
                make_path_for_knight(&s2);
                move_from_to(&empty, &s2);
                return;
            }
        }
        else
        {
            move_from_to(&s1, &empty);
            make_path_for_knight(&s1);
            move_from_to(&empty, &s1);
            return;
        }
    }

    return;
}

int main(int argc, char *argv[])
{
    // Initialize SDL
    if (SDL_Init(SDL_INIT_VIDEO) != 0)
    {
        printf("SDL_Init Error: %s\n", SDL_GetError());
        return 1;
    }

    // Initialize SDL_ttf
    if (TTF_Init() != 0)
    {
        printf("TTF_Init Error: %s\n", TTF_GetError());
        SDL_Quit();
        return 1;
    }

    // Create a window
    SDL_Window *win = SDL_CreateWindow("Chess Board", 100, 100, WINDOW_WIDTH, WINDOW_HEIGHT, SDL_WINDOW_SHOWN);
    if (win == NULL)
    {
        printf("SDL_CreateWindow Error: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    // Create a renderer
    renderer = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (renderer == NULL)
    {
        SDL_DestroyWindow(win);
        printf("SDL_CreateRenderer Error: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }
    font = TTF_OpenFont("arial.ttf", 24);

    // Create and initialize the chess board
    initializeBoard(board);
    placePieces(board);

    // Main loop
    bool quit = false;
    SDL_Event e;
    char input[5];
    while (!quit)
    {
        // Clear the screen
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        SDL_RenderClear(renderer);
        drawBoard(renderer, board);
        SDL_RenderPresent(renderer);

        printf("Enter move command (e.g., a2a4): ");
        scanf("%s", input);
        if (input[0] == 'q')
        {
            break;
        }
        int move_type = process_move(input);
        piece_move.startCol = input[0] - 'a';
        piece_move.startRow = '8' - input[1];
        piece_move.endCol = input[2] - 'a';
        piece_move.endRow = '8' - input[3];
        if (move_type == 2)
        {
            printf("Illegal move! \n");
            continue;
        }
        if (move_type == 1)
        {
            knight_move();
            printf("Knight move! \n");
            continue;
        }

        // Event handling
        while (SDL_PollEvent(&e))
        {
            if (e.type == SDL_QUIT)
            {
                quit = true;
            }
        }

        movement.startX = piece_move.startCol * SQUARE_SIZE + SQUARE_SIZE / 2;
        movement.startY = piece_move.startRow * SQUARE_SIZE + SQUARE_SIZE / 2;
        movement.endX = piece_move.endCol * SQUARE_SIZE + SQUARE_SIZE / 2;
        movement.endY = piece_move.endRow * SQUARE_SIZE + SQUARE_SIZE / 2;
        movement.moving = true;

        // Update board state
        board[piece_move.startRow][piece_move.startCol].occupied = false;

        // Draw the moving piece
        drawMovingPiece(renderer, &movement, true);

        // Present the renderer
        SDL_RenderPresent(renderer);

        board[piece_move.endRow][piece_move.endCol].occupied = true;
    }

    // Cleanup
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(win);
    SDL_Quit();

    return 0;
}
