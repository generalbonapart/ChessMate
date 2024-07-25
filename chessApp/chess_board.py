class Move:
    def __init__(self, startX, startY, endX, endY):
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY
            
class ChessBoard:
    def __init__(self):
        # Initialize the board with pieces in their starting positions
        self.board = self.create_starting_board()
    
    def create_starting_board(self):
        # Set up the board with the standard initial positions
        starting_board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        return starting_board

    def display_board(self):
        for row in self.board:
            print(' '.join(row))
        print()

    def move_piece(self, move: Move):
        start_col, start_row = (move.startX, 7 - move.startY)
        end_col, end_row = (move.endX, 7 - move.endY)
        print(start_col, start_row)
        print(end_col, end_row)
        # Perform the move
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = '.'
    
    def get_piece(self, x, y):
        return self.board[7-y][x]



chess_board_inst = ChessBoard()
# board.display_board()
# move = Move(3, 1, 3, 3)
# board.move_piece(move)
# board.display_board()
# print(board.get_piece(3,7))