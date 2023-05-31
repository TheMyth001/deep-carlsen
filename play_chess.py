class Piece:

    def __init__(self, color: str):
        if color == "white" or color == "black":
            self.color = color
        else:
            raise ValueError(f"Expected color to be `white` or `black`, got `{color}`")
        self.alive = True
        self.position = None

    def kill(self):
        self.alive = False
        self.position = None


class ChessBoard:

    def __init__(self, pieces: list):
        self.cell_grid = []
        for row in range(8):
            self.cell_grid.append([])
            for col in range(8):
                self.cell_grid[row].append(Cell(self))
        for piece in pieces:
            self[piece.position] = piece

    def __getitem__(self, call_code: str):
        letter, num = call_code[0], int(call_code[1])
        if (0 <= 8 - num <= 7) and (0 <= ord(letter) - 97 <= 7):
            return self.cell_grid[8 - num][ord(letter) - 97]
        else:
            return None

    def __setitem__(self, cell_code: str, piece: Piece):
        letter, num = cell_code[0], int(cell_code[1])
        self.cell_grid[8 - num][ord(letter) - 97].piece = piece

    def display(self):
        print(" " * 4, end="")
        print("+-----" * 8 + "+")
        for row_num, row in enumerate(self.cell_grid):
            print(f" {8 - row_num}  ", end="")
            for item in row:
                print(f"|  {item}  ", end="")
            print("|")
            print(" " * 4, end="")
            print("+-----" * 8 + "+")
        print(" " * 4, end="")
        print("   a     b     c     d     e     f     g     h")

    def piece_color(self, cell_code):
        if self[cell_code].piece is None:
            return None
        else:
            return self[cell_code].piece.color


class King(Piece):

    def __init__(self, color: str):
        Piece.__init__(self, color)
        if self.color == "white":
            self.position, self.notation = "e1", "K"
        else:
            self.position, self.notation = "e8", "k"

    def legal_moves(self, chess_board: ChessBoard):
        legal_moves = []
        for vertical in range(-1, 2):
            for horizontal in range(-1, 2):
                new_cell = chr(ord(self.position[0]) + horizontal) + str(int(self.position[1]) + vertical)
                if (chess_board[new_cell] is not None and
                        not (vertical == 0 and horizontal == 0) and
                        chess_board.piece_color(new_cell) != self.color):
                    legal_moves.append(new_cell)
        return legal_moves


class Queen(Piece):

    def __init__(self, color: str):
        Piece.__init__(self, color)
        if self.color == "white":
            self.position, self.notation = "d1", "Q"
        else:
            self.position, self.notation = "d8", "q"

    def legal_moves(self, chess_board: ChessBoard):
        legal_moves = []
        if not self.alive:
            return legal_moves
        for up in range(1, 9 - int(self.position[1])):
            new_cell = chr(ord(self.position[0])) + str(int(self.position[1]) + up)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for down in range(-1, -1 - int(self.position[1]), -1):
            new_cell = chr(ord(self.position[0])) + str(int(self.position[1]) + down)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for right in range(1, -ord(self.position[0]) + 105):
            new_cell = chr(ord(self.position[0]) + right) + self.position[1]
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for left in range(-1, -ord(self.position[0]) + 96, -1):
            new_cell = chr(ord(self.position[0]) + left) + self.position[1]
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for up_right in range(1, 1+min(104-ord(self.position[0]), 8-int(self.position[1]))):
            new_cell = chr(ord(self.position[0]) + up_right) + str(int(self.position[1]) + up_right)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for down_right in range(1, 1 + min(104 - ord(self.position[0]), int(self.position[1]))):
            new_cell = chr(ord(self.position[0]) + down_right) + str(int(self.position[1]) - down_right)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for up_left in range(1, 1 + min(ord(self.position[0]) - 97, 8 - int(self.position[1]))):
            new_cell = chr(ord(self.position[0]) - up_left) + str(int(self.position[1]) + up_left)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for down_left in range(1, 1+min(ord(self.position[0])-97, int(self.position[1]))):
            new_cell = chr(ord(self.position[0]) - down_left) + str(int(self.position[1]) - down_left)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        return legal_moves


class Rook(Piece):

    def __init__(self, color: str, col: str):
        Piece.__init__(self, color)
        if col != "a" and col != "h":
            raise ValueError(f"Expected column to be `a` or `h`, got `{col}`")
        if self.color == "white":
            self.position, self.notation = f"{col}1", "R"
        else:
            self.position, self.notation = f"{col}8", "r"

    def legal_moves(self, chess_board: ChessBoard):
        legal_moves = []
        if not self.alive:
            return legal_moves
        for up in range(1, 9 - int(self.position[1])):
            new_cell = chr(ord(self.position[0])) + str(int(self.position[1]) + up)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for down in range(-1, -1 - int(self.position[1]), -1):
            new_cell = chr(ord(self.position[0])) + str(int(self.position[1]) + down)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for right in range(1, -ord(self.position[0]) + 105):
            new_cell = chr(ord(self.position[0]) + right) + self.position[1]
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for left in range(-1, -ord(self.position[0]) + 96, -1):
            new_cell = chr(ord(self.position[0]) + left) + self.position[1]
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        return legal_moves


class Bishop(Piece):

    def __init__(self, color: str, col: str):
        Piece.__init__(self, color)
        if col != "c" and col != "f":
            raise ValueError(f"Expected column to be `c` or `f`, got `{col}`")
        if self.color == "white":
            self.position, self.notation = f"{col}1", "B"
        else:
            self.position, self.notation = f"{col}8", "b"

    def legal_moves(self, chess_board: ChessBoard):
        legal_moves = []
        if not self.alive:
            return legal_moves
        for up_right in range(1, 1+min(104-ord(self.position[0]), 8-int(self.position[1]))):
            new_cell = chr(ord(self.position[0]) + up_right) + str(int(self.position[1]) + up_right)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for down_right in range(1, 1 + min(104 - ord(self.position[0]), int(self.position[1]))):
            new_cell = chr(ord(self.position[0]) + down_right) + str(int(self.position[1]) - down_right)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for up_left in range(1, 1 + min(ord(self.position[0]) - 97, 8 - int(self.position[1]))):
            new_cell = chr(ord(self.position[0]) - up_left) + str(int(self.position[1]) + up_left)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        for down_left in range(1, 1+min(ord(self.position[0])-97, int(self.position[1]))):
            new_cell = chr(ord(self.position[0]) - down_left) + str(int(self.position[1]) - down_left)
            if chess_board[new_cell] is not None:
                if chess_board.piece_color(new_cell) == self.color:
                    break
                else:
                    legal_moves.append(new_cell)
                    if chess_board.piece_color(new_cell) is not None:
                        break
        return legal_moves


class Knight(Piece):

    def __init__(self, color: str, col: str):
        Piece.__init__(self, color)
        if col != "b" and col != "g":
            raise ValueError(f"Expected column to be `b` or `g`, got `{col}`")
        if self.color == "white":
            self.position, self.notation = f"{col}1", "N"
        else:
            self.position, self.notation = f"{col}8", "n"

    def legal_moves(self, chess_board: ChessBoard):
        legal_moves = []
        if not self.alive:
            return legal_moves
        for move1 in [-2, 2]:
            for move2 in [-1, 1]:
                new_cell = chr(ord(self.position[0]) + move1) + str(int(self.position[1]) + move2)
                if chess_board[new_cell] is not None:
                    if chess_board.piece_color(new_cell) != self.color:
                        legal_moves.append(new_cell)
                new_cell = chr(ord(self.position[0]) + move2) + str(int(self.position[1]) + move1)
                if chess_board[new_cell] is not None:
                    if chess_board.piece_color(new_cell) != self.color:
                        legal_moves.append(new_cell)
        return legal_moves


# class Pawn(Piece):
#
#     def __init__(self, color: str, col: str):
#         self.position = color


class Cell:

    def __init__(self, chess_board: ChessBoard):
        self.piece = None
        self.board = chess_board

    def __str__(self):
        if self.piece is not None:
            return self.piece.notation
        else:
            return " "


wk = King("white")
wq = Queen("white")
wr1 = Rook("white", "a")
wr2 = Rook("white", "h")
wn1 = Knight("white", "b")
wn2 = Knight("white", "g")
wb1 = Bishop("white", "c")
wb2 = Bishop("white", "f")
bk = King("black")
bq = Queen("black")
br1 = Rook("black", "a")
br2 = Rook("black", "h")
bn1 = Knight("black", "b")
bn2 = Knight("black", "g")
bb1 = Bishop("black", "c")
bb2 = Bishop("black", "f")

piece_list = [wk, wq, wr1, wr2, wn1, wn2, wb1, wb2,
              bk, bq, br1, br2, bn1, bn2, bb1, bb2]

board = ChessBoard(piece_list)
board.display()

print(wn1.legal_moves(board))
