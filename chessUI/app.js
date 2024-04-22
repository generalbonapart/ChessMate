// app.js

// Function to create and place chess pieces on the board
function setupChessboard() {
    // Array of initial chess piece positions
    const initialChessboard = {
        'a8': '♜', 'b8': '♞', 'c8': '♝', 'd8': '♛', 'e8': '♚', 'f8': '♝', 'g8': '♞', 'h8': '♜',
        'a7': '♟', 'b7': '♟', 'c7': '♟', 'd7': '♟', 'e7': '♟', 'f7': '♟', 'g7': '♟', 'h7': '♟',
        // Add more pieces as needed...
        'a2': '♙', 'b2': '♙', 'c2': '♙', 'd2': '♙', 'e2': '♙', 'f2': '♙', 'g2': '♙', 'h2': '♙',
        'a1': '♖', 'b1': '♘', 'c1': '♗', 'd1': '♕', 'e1': '♔', 'f1': '♗', 'g1': '♘', 'h1': '♖'
    };

    // Loop through each square on the chessboard
    for (let squareId in initialChessboard) {
        // Get the square element corresponding to the squareId
        const square = document.getElementById(squareId);
        // Set the piece as the inner text of the square
        square.innerText = initialChessboard[squareId];
    }
}

// Call the setupChessboard function when the DOM content is loaded
document.addEventListener('DOMContentLoaded', setupChessboard);
