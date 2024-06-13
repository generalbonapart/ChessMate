class ChessBoard:
    def __init__(self):
        self.board_state = self.initialize_board()

    def initialize_board(self):
        return {
            'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K', 'f1': 'B', 'g1': 'N', 'h1': 'R',
            'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P',
            'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p',
            'a8': 'r', 'b8': 'n', 'c8': 'b', 'd8': 'q', 'e8': 'k', 'f8': 'b', 'g8': 'n', 'h8': 'r',
            'K': 'e1', 'Q': 'd1', 'R': ['a1', 'h1'], 'B': ['c1', 'f1'], 'N': ['b1', 'g1'], 'P': ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'],
            'k': 'e8', 'q': 'd8', 'r': ['a8', 'h8'], 'b': ['c8', 'f8'], 'n': ['b8', 'g8'], 'p': ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7']
        }

    def convert_move_to_board_notation(self, move):
        if move in ['O-O', 'O-O-O']:
            return move

        piece = ''
        from_square = ''
        to_square = ''

        if move[0] in 'KQRBN':
            piece = move[0]
            to_square = move[1:3]
        else:
            piece = 'P'
            to_square = move[:2]

        from_square = self.find_from_square(piece, to_square)
        self.update_board_state(piece, from_square, to_square)
        return f"{from_square}{to_square}"

    def find_from_square(self, piece, to_square):
        if piece == 'P':
            col = to_square[0]
            row = str(int(to_square[1]) - 1)
            from_square = col + row
            if from_square in self.board_state and self.board_state[from_square] == piece:
                return from_square
            row = str(int(to_square[1]) + 1)
            from_square = col + row
            return from_square

        possible_squares = self.get_possible_squares(piece)
        for square in possible_squares:
            if self.is_valid_move(piece, square, to_square):
                return square
        return ''

    def get_possible_squares(self, piece):
        if piece == 'N':
            return self.board_state['N']
        elif piece == 'B':
            return self.board_state['B']
        elif piece == 'R':
            return self.board_state['R']
        elif piece == 'Q':
            return [self.board_state['Q']]
        elif piece == 'K':
            return [self.board_state['K']]
        return []

    def is_valid_move(self, piece, from_square, to_square):
        row_diff = abs(int(from_square[1]) - int(to_square[1]))
        col_diff = abs(ord(from_square[0]) - ord(to_square[0]))

        if piece == 'N':
            return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
        elif piece == 'B':
            return row_diff == col_diff
        elif piece == 'R':
            return row_diff == 0 or col_diff == 0
        elif piece == 'Q':
            return row_diff == col_diff or row_diff == 0 or col_diff == 0
        elif piece == 'K':
            return row_diff <= 1 and col_diff <= 1
        return False

    def update_board_state(self, piece, from_square, to_square):
        self.board_state[to_square] = self.board_state[from_square]
        del self.board_state[from_square]

        if piece == 'N':
            self.board_state['N'] = [to_square if s == from_square else s for s in self.board_state['N']]
        elif piece == 'B':
            self.board_state['B'] = [to_square if s == from_square else s for s in self.board_state['B']]
        elif piece == 'R':
            self.board_state['R'] = [to_square if s == from_square else s for s in self.board_state['R']]
        elif piece == 'Q':
            self.board_state['Q'] = to_square
        elif piece == 'K':
            self.board_state['K'] = to_square


# Singleton instance of ChessBoard
chess_board_instance = ChessBoard()

def convert_move_to_board_notation(move):
    return chess_board_instance.convert_move_to_board_notation(move)
