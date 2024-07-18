import json

class BoardStateTracker:

    def __init__(self):
        self.previous_file = 'images/previous_board'
        self.current_file = 'images/current_board'

    @staticmethod
    def load_board_state(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return [[0 for _ in range(8)] for _ in range(8)]
        
    @staticmethod
    def compare_board_state(previous_state, current_state):
        differences = []
        for row in range(8):
            for col in range(8):
                if previous_state[row][col] != current_state[row][col]:
                    differences.append((row, col, previous_state[row][col], current_state[row][col]))
        return differences

    def find_piece_movement(self):
        previous_state = self.load_board_state(self.previous_file)
        current_state = self.load_board_state(self.current_file)
        differences = self.compare_board_state(previous_state, current_state)

        if len(differences) != 2:
            return None  # If there aren't exactly two differences, something went wrong.

        start_pos = None
        end_pos = None

        for diff in differences:
            row, col, prev_value, curr_value = diff
            if prev_value == 1 and curr_value == 0:
                start_pos = (row, col)
            elif prev_value == 0 and curr_value == 1:
                end_pos = (row, col)

        if start_pos is None or end_pos is None:
            return None  # If start or end positions are not properly detected.

        # Convert row, col indices to chess notation
        start_notation = chr(start_pos[1] + ord('a')) + str(8 - start_pos[0])
        end_notation = chr(end_pos[1] + ord('a')) + str(8 - end_pos[0])

        move = start_notation + end_notation
        return move

if __name__ == "__main__":
    tracker = BoardStateTracker()
    movement = tracker.find_piece_movement()
    if movement:
        print(f"Detected move: {movement}")
    else:
        print("No valid move detected.")