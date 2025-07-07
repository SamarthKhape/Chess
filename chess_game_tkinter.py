import tkinter as tk
from tkinter import messagebox

# Unicode chess pieces
pieces_unicode = {
    'wp': '\u2659', 'wr': '\u2656', 'wn': '\u2658', 'wb': '\u2657', 'wq': '\u2655', 'wk': '\u2654',
    'bp': '\u265F', 'br': '\u265C', 'bn': '\u265E', 'bb': '\u265D', 'bq': '\u265B', 'bk': '\u265A',
    '': ''
}

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game - Tkinter GUI")
        self.turn = 'w'
        self.selected = None
        self.valid_moves = []
        self.buttons = {}
        self.board = [
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp'] * 8,
            [''] * 8,
            [''] * 8,
            [''] * 8,
            [''] * 8,
            ['wp'] * 8,
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
        ]
        self.create_widgets()
        self.update_board()

    def create_widgets(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        for row in range(8):
            for col in range(8):
                color = 'white' if (row + col) % 2 == 0 else 'gray'
                btn = tk.Button(self.frame, text='', font=('Arial', 24), width=2, height=1,
                                bg=color, command=lambda r=row, c=col: self.on_click(r, c))
                btn.grid(row=row, column=col)
                self.buttons[(row, col)] = btn

    def update_board(self):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                self.buttons[(row, col)].config(text=pieces_unicode[piece])
                # Reset button background color
                color = 'white' if (row + col) % 2 == 0 else 'gray'
                self.buttons[(row, col)].config(bg=color)
        # Highlight selected and valid moves
        if self.selected:
            r, c = self.selected
            self.buttons[(r, c)].config(bg='blue')
            for move in self.valid_moves:
                mr, mc = move
                self.buttons[(mr, mc)].config(bg='green')

    def on_click(self, row, col):
        if self.selected == (row, col):
            self.selected = None
            self.valid_moves = []
        else:
            piece = self.board[row][col]
            if piece != '' and piece[0] == self.turn:
                self.selected = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
            elif self.selected and (row, col) in self.valid_moves:
                self.move_piece(self.selected, (row, col))
                self.selected = None
                self.valid_moves = []
                self.turn = 'b' if self.turn == 'w' else 'w'
            else:
                # Invalid click, reset selection
                self.selected = None
                self.valid_moves = []
        self.update_board()

    def move_piece(self, start, end):
        sr, sc = start
        er, ec = end
        self.board[er][ec] = self.board[sr][sc]
        self.board[sr][sc] = ''
        # Check if king is captured (checkmate)
        if self.board[er][ec][1] == 'k':
            winner = 'White' if self.board[er][ec][0] == 'w' else 'Black'
            messagebox.showinfo("Checkmate", f"Checkmate! {winner} wins!")
            # Disable all buttons to end game
            for btn in self.buttons.values():
                btn.config(state='disabled')

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if piece == '':
            return []
        piece_type = piece[1]
        if piece_type == 'p':
            return self.pawn_moves(row, col, piece[0])
        elif piece_type == 'r':
            return self.rook_moves(row, col, piece[0])
        elif piece_type == 'n':
            return self.knight_moves(row, col, piece[0])
        elif piece_type == 'b':
            return self.bishop_moves(row, col, piece[0])
        elif piece_type == 'q':
            return self.queen_moves(row, col, piece[0])
        elif piece_type == 'k':
            return self.king_moves(row, col, piece[0])
        return []

    def pawn_moves(self, row, col, color):
        moves = []
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        # Move forward
        if self.is_empty(row + direction, col):
            moves.append((row + direction, col))
            # Double move from start
            if row == start_row and self.is_empty(row + 2 * direction, col):
                moves.append((row + 2 * direction, col))
        # Captures
        for dc in [-1, 1]:
            r, c = row + direction, col + dc
            if self.in_bounds(r, c) and self.is_enemy(r, c, color):
                moves.append((r, c))
        return moves

    def rook_moves(self, row, col, color):
        moves = []
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self.in_bounds(r, c):
                if self.is_empty(r, c):
                    moves.append((r, c))
                elif self.is_enemy(r, c, color):
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves

    def knight_moves(self, row, col, color):
        moves = []
        knight_steps = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
        for dr, dc in knight_steps:
            r, c = row + dr, col + dc
            if self.in_bounds(r, c) and not self.is_friendly(r, c, color):
                moves.append((r, c))
        return moves

    def bishop_moves(self, row, col, color):
        moves = []
        directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self.in_bounds(r, c):
                if self.is_empty(r, c):
                    moves.append((r, c))
                elif self.is_enemy(r, c, color):
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves

    def queen_moves(self, row, col, color):
        return self.rook_moves(row, col, color) + self.bishop_moves(row, col, color)

    def king_moves(self, row, col, color):
        moves = []
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if self.in_bounds(r, c) and not self.is_friendly(r, c, color):
                moves.append((r, c))
        return moves

    def in_bounds(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def is_empty(self, row, col):
        return self.board[row][col] == ''

    def is_enemy(self, row, col, color):
        piece = self.board[row][col]
        return piece != '' and piece[0] != color

    def is_friendly(self, row, col, color):
        piece = self.board[row][col]
        return piece != '' and piece[0] == color

def main():
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()

if __name__ == '__main__':
    main()
