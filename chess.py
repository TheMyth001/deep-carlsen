white_pieces = []
black_pieces = []


class Piece:

    def __init__(self, color):
        self.color = color
        self.row, self.col = None, None
        if color == 'white':
            self.army = white_pieces
            self.enemy = black_pieces
        else:
            self.army = black_pieces
            self.enemy = white_pieces

    def kill(self):
        del self

    def attacks(self):
        return []

    def legal_moves(self):
        attacks = self.attacks()
        legal = attacks.copy()
        for attack in attacks:
            row, col = attack
            if board[row][col] in self.army:
                legal.remove(attack)
            else:
                piece_on_attacked_cell = board[row][col]
                board[self.row][self.col] = None
                board[row][col] = self
                for piece in self.enemy:
                    if (self.army[0].row, self.army[0].col) in piece.attacks():
                        legal.remove(attack)
                board[self.row][self.col] = self
                board[row][col] = piece_on_attacked_cell
        return legal


class King(Piece):

    def __init__(self, color):
        Piece.__init__(self, color)
        self.col = 4
        self.long_castle = True
        self.short_castle = True
        if self.color == "white":
            self.notation, self.row = "K", 7
        else:
            self.notation, self.row = "k", 0

    def attacks(self):
        attacks = []
        for vertical in range(-1, 2):
            for horizontal in range(-1, 2):
                if vertical == 0 and horizontal == 0:
                    pass
                elif self.row+vertical > 7 or self.row+vertical < 0 or \
                        self.col+horizontal > 7 or self.col+horizontal < 0:
                    pass
                else:
                    attacks.append(tuple([self.row + vertical, self.col + horizontal]))
        return attacks

    def legal_moves(self):
        attacks = self.attacks()
        legal = attacks.copy()
        for attack in attacks:
            row, col = attack
            if board[row][col] in self.army:
                legal.remove(attack)
            else:
                for piece in self.enemy:
                    if (row, col) in piece.attacks():
                        legal.remove(attack)
        if self.short_castle:
            if board[self.row][5] is not None:
                pass
            elif board[self.row][6] is not None:
                pass
            else:
                legal.append(tuple([self.row, 6]))
            for piece in self.enemy:
                if (self.row, 5) in piece.attacks() or (self.row, 6) in piece.attacks():
                    legal.remove(tuple([self.row, 6]))
                    continue
        if self.long_castle:
            if board[self.row][3] is not None:
                pass
            elif board[self.row][2] is not None:
                pass
            elif board[self.row][1] is not None:
                pass
            else:
                legal.append(tuple([self.row, 2]))
            for piece in self.enemy:
                if (self.row, 3) in piece.attacks() or \
                        (self.row, 2) in piece.attacks() or \
                        (self.row, 1) in piece.attacks():
                    legal.remove(tuple([self.row, 2]))
                    continue
        return legal

    def play_short_castle(self):
        board[self.row][6] = self
        board[self.row][self.col] = None
        board[self.row][5] = self.army[3]
        self.army[3].row = self.row
        self.army[3].col = 5
        board[self.row][7] = None
        self.short_castle = False
        self.long_castle = False

    def play_long_castle(self):
        board[self.row][2] = self
        board[self.row][self.col] = None
        board[self.row][3] = self.army[2]
        self.army[2].row = self.row
        self.army[2].col = 3
        board[self.row][0] = None
        self.short_castle = False
        self.long_castle = False

    def is_check_checkmate(self):
        checkmate = False
        for piece in self.enemy:
            if (self.row, self.col) in piece.attacks():
                checkmate = True
                for soldier in self.army:
                    if soldier.legal_moves():
                        checkmate = False
                if checkmate:
                    print(f'{self.color} loses!'.upper())
                else:
                    print('\t\t\t\tcheck!')
        return checkmate

    def is_stalemate(self):
        stalemate = True
        for soldier in self.army:
            if soldier.legal_moves():
                stalemate = False
                break
        if stalemate:
            print('draw by stalemate!')
        return stalemate


class Queen(Piece):

    def __init__(self, color):
        Piece.__init__(self, color)
        self.col = 3
        if self.color == "white":
            self.notation, self.row = "Q", 7
        else:
            self.notation, self.row = "q", 0

    def attacks(self):
        attacks = []
        for up in range(1, self.row + 1):
            if board[self.row - up][self.col] is None:
                attacks.append(tuple([self.row - up, self.col]))
            elif board[self.row - up][self.col] in self.army:
                attacks.append(tuple([self.row - up, self.col]))
                break
            else:
                attacks.append(tuple([self.row - up, self.col]))
                break
        for down in range(1, 8 - self.row):
            if board[self.row + down][self.col] is None:
                attacks.append(tuple([self.row + down, self.col]))
            elif board[self.row + down][self.col] in self.army:
                attacks.append(tuple([self.row + down, self.col]))
                break
            else:
                attacks.append(tuple([self.row + down, self.col]))
                break
        for right in range(1, 8 - self.col):
            if board[self.row][self.col + right] is None:
                attacks.append(tuple([self.row, self.col + right]))
            elif board[self.row][self.col + right] in self.army:
                attacks.append(tuple([self.row, self.col + right]))
                break
            else:
                attacks.append(tuple([self.row, self.col + right]))
                break
        for left in range(1, self.col + 1):
            if board[self.row][self.col - left] is None:
                attacks.append(tuple([self.row, self.col - left]))
            elif board[self.row][self.col - left] in self.army:
                attacks.append(tuple([self.row, self.col - left]))
                break
            else:
                attacks.append(tuple([self.row, self.col - left]))
                break
        for up_right in range(1, min(self.row + 1, 8 - self.col)):
            if board[self.row - up_right][self.col + up_right] is None:
                attacks.append(tuple([self.row - up_right, self.col + up_right]))
            elif board[self.row - up_right][self.col + up_right] in self.army:
                attacks.append(tuple([self.row - up_right, self.col + up_right]))
                break
            else:
                attacks.append(tuple([self.row - up_right, self.col + up_right]))
                break
        for up_left in range(1, min(self.row + 1, self.col + 1)):
            if board[self.row - up_left][self.col - up_left] is None:
                attacks.append(tuple([self.row - up_left, self.col - up_left]))
            elif board[self.row - up_left][self.col - up_left] in self.army:
                attacks.append(tuple([self.row - up_left, self.col - up_left]))
                break
            else:
                attacks.append(tuple([self.row - up_left, self.col - up_left]))
                break
        for down_right in range(1, min(8 - self.row, 8 - self.col)):
            if board[self.row + down_right][self.col + down_right] is None:
                attacks.append(tuple([self.row + down_right, self.col + down_right]))
            elif board[self.row + down_right][self.col + down_right] in self.army:
                attacks.append(tuple([self.row + down_right, self.col + down_right]))
                break
            else:
                attacks.append(tuple([self.row + down_right, self.col + down_right]))
                break
        for down_left in range(1, min(8 - self.row, self.col + 1)):
            if board[self.row + down_left][self.col - down_left] is None:
                attacks.append(tuple([self.row + down_left, self.col - down_left]))
            elif board[self.row + down_left][self.col - down_left] in self.army:
                attacks.append(tuple([self.row + down_left, self.col - down_left]))
                break
            else:
                attacks.append(tuple([self.row + down_left, self.col - down_left]))
                break
        return attacks


class Rook(Piece):

    def __init__(self, color, col):
        Piece.__init__(self, color)
        self.col = ord(col) - 97
        if self.color == "white":
            self.notation, self.row = "R", 7
        else:
            self.notation, self.row = "r", 0
        self.has_moved = False

    def attacks(self):
        attacks = []
        for up in range(1, self.row + 1):
            if board[self.row - up][self.col] is None:
                attacks.append(tuple([self.row - up, self.col]))
            elif board[self.row - up][self.col] in self.army:
                attacks.append(tuple([self.row - up, self.col]))
                break
            else:
                attacks.append(tuple([self.row - up, self.col]))
                break
        for down in range(1, 8 - self.row):
            if board[self.row + down][self.col] is None:
                attacks.append(tuple([self.row + down, self.col]))
            elif board[self.row + down][self.col] in self.army:
                attacks.append(tuple([self.row + down, self.col]))
                break
            else:
                attacks.append(tuple([self.row + down, self.col]))
                break
        for right in range(1, 8 - self.col):
            if board[self.row][self.col + right] is None:
                attacks.append(tuple([self.row, self.col + right]))
            elif board[self.row][self.col + right] in self.army:
                attacks.append(tuple([self.row, self.col + right]))
                break
            else:
                attacks.append(tuple([self.row, self.col + right]))
                break
        for left in range(1, self.col + 1):
            if board[self.row][self.col - left] is None:
                attacks.append(tuple([self.row, self.col - left]))
            elif board[self.row][self.col - left] in self.army:
                attacks.append(tuple([self.row, self.col - left]))
                break
            else:
                attacks.append(tuple([self.row, self.col - left]))
                break
        return attacks


class Knight(Piece):

    def __init__(self, color, col):
        Piece.__init__(self, color)
        self.col = ord(col) - 97
        if self.color == "white":
            self.notation, self.row = "N", 7
        else:
            self.notation, self.row = "n", 0

    def attacks(self):
        attacks = []
        for move1 in [-2, 2]:
            for move2 in [-1, 1]:
                if self.row+move1 < 0 or self.row+move1 > 7 or self.col+move2 < 0 or self.col+move2 > 7:
                    pass
                else:
                    attacks.append(tuple([self.row + move1, self.col + move2]))
                if self.row+move2 < 0 or self.row+move2 > 7 or self.col+move1 < 0 or self.col+move1 > 7:
                    pass
                else:
                    attacks.append(tuple([self.row + move2, self.col + move1]))
        return attacks


class Bishop(Piece):

    def __init__(self, color, col):
        Piece.__init__(self, color)
        self.col = ord(col) - 97
        if self.color == "white":
            self.notation, self.row = "B", 7
        else:
            self.notation, self.row = "b", 0

    def attacks(self):
        attacks = []
        for up_right in range(1, min(self.row + 1, 8 - self.col)):
            if board[self.row - up_right][self.col + up_right] is None:
                attacks.append(tuple([self.row - up_right, self.col + up_right]))
            elif board[self.row - up_right][self.col + up_right] in self.army:
                attacks.append(tuple([self.row - up_right, self.col + up_right]))
                break
            else:
                attacks.append(tuple([self.row - up_right, self.col + up_right]))
                break
        for up_left in range(1, min(self.row + 1, self.col + 1)):
            if board[self.row - up_left][self.col - up_left] is None:
                attacks.append(tuple([self.row - up_left, self.col - up_left]))
            elif board[self.row - up_left][self.col - up_left] in self.army:
                attacks.append(tuple([self.row - up_left, self.col - up_left]))
                break
            else:
                attacks.append(tuple([self.row - up_left, self.col - up_left]))
                break
        for down_right in range(1, min(8 - self.row, 8 - self.col)):
            if board[self.row + down_right][self.col + down_right] is None:
                attacks.append(tuple([self.row + down_right, self.col + down_right]))
            elif board[self.row + down_right][self.col + down_right] in self.army:
                attacks.append(tuple([self.row + down_right, self.col + down_right]))
                break
            else:
                attacks.append(tuple([self.row + down_right, self.col + down_right]))
                break
        for down_left in range(1, min(8 - self.row, self.col + 1)):
            if board[self.row + down_left][self.col - down_left] is None:
                attacks.append(tuple([self.row + down_left, self.col - down_left]))
            elif board[self.row + down_left][self.col - down_left] in self.army:
                attacks.append(tuple([self.row + down_left, self.col - down_left]))
                break
            else:
                attacks.append(tuple([self.row + down_left, self.col - down_left]))
                break
        return attacks


class Pawn(Piece):

    def __init__(self, color, col):
        Piece.__init__(self, color)
        self.col = ord(col) - 97
        if self.color == "white":
            self.notation, self.row, self.step = "P", 6, -1
        else:
            self.notation, self.row, self.step = "p", 1, 1

    def attacks(self):
        attacks = []
        if self.col - 1 >= 0:
            attacks.append(tuple([self.row + self.step, self.col - 1]))
        if self.col + 1 <= 7:
            attacks.append(tuple([self.row + self.step, self.col + 1]))
        return attacks

    def legal_moves(self):
        attacks = self.attacks()
        legal = attacks.copy()
        for attack in attacks:
            row, col = attack
            if board[row][col] is None or board[row][col] in self.army:
                legal.remove(attack)
        temp_legal = legal.copy()
        if board[self.row + self.step][self.col] is None:
            temp_legal.append(tuple([self.row + self.step, self.col]))
        if self.row == 3.5 - 2.5 * self.step:
            if board[self.row + self.step][self.col] is None and board[self.row + 2*self.step][self.col] is None:
                temp_legal.append(tuple([self.row + 2*self.step, self.col]))
        # todo: en passant
        legal = temp_legal.copy()
        for l_move in temp_legal:
            row, col = l_move
            piece_on_attacked_cell = board[row][col]
            board[self.row][self.col] = None
            board[row][col] = self
            for piece in self.enemy:
                if (self.army[0].row, self.army[0].col) in piece.attacks():
                    legal.remove(l_move)
                    break
            board[self.row][self.col] = self
            board[row][col] = piece_on_attacked_cell
        return legal

    def promote(self):
        # todo: write this code
        return self


def display():
    print(" " * 4, end="")
    print("+-----" * 8 + "+")
    for row_num, row in enumerate(board):
        print(f" {8 - row_num}  ", end="")
        for item in row:
            if item is None:
                notation = " "
            else:
                notation = item.notation
            print(f"|  {notation}  ", end="")
        print("|")
        print(" " * 4, end="")
        print("+-----" * 8 + "+")
    print(" " * 4, end="")
    print("   a     b     c     d     e     f     g     h")


def make_move(start, end):
    start = str_to_rc(start)
    end = str_to_rc(end)
    piece = board[start[0]][start[1]]
    if tuple([end[0], end[1]]) in piece.legal_moves():
        if board[end[0]][end[1]] is not None:
            board[end[0]][end[1]].kill()
        if type(board[start[0]][start[1]]) == King:
            if board[start[0]][start[1]].short_castle and end[1] == 6:
                board[start[0]][start[1]].play_short_castle()
            elif board[start[0]][start[1]].long_castle and end[1] == 2:
                board[start[0]][start[1]].play_long_castle()
            else:
                board[start[0]][start[1]].short_castle = False
                board[start[0]][start[1]].long_castle = False
        if type(board[start[0]][start[1]]) == Rook:
            if not board[start[0]][start[1]].has_moved and start[1] == 7:
                board[start[0]][start[1]].army[0].short_castle = False
                board[start[0]][start[1]].has_moved = True
            if not board[start[0]][start[1]].has_moved and start[1] == 0:
                board[start[0]][start[1]].army[0].long_castle = False
                board[start[0]][start[1]].has_moved = True
        board[start[0]][start[1]] = None
        board[end[0]][end[1]] = piece
        piece.row = end[0]
        piece.col = end[1]
    else:
        print('Invalid Move!')


def rc_to_str(rc_tuple):
    row, col = rc_tuple
    cell = f'{chr(col + 97)}{str(8 - row)}'
    return cell


def str_to_rc(cell):
    row = 8 - int(cell[1])
    col = ord(cell[0]) - 97
    return row, col


def select_and_move(color_pieces):
    color = color_pieces[0].color
    print(f'{color} to move: ', end='\t')
    start = input(f'select starting square:\t')
    piece = board[str_to_rc(start)[0]][str_to_rc(start)[1]]
    if piece is None or piece.color != color:
        print('\t\t\t\tinvalid square!')
        select_and_move(color_pieces)
    else:
        end = input('\t\t\t\tselect end position:\t')
        make_move(start, end)


wk = King('white')
wq = Queen('white')
wr1 = Rook('white', 'a')
wr2 = Rook('white', 'h')
wn1 = Knight('white', 'b')
wn2 = Knight('white', 'g')
wb1 = Bishop('white', 'c')
wb2 = Bishop('white', 'f')
wpa = Pawn('white', 'a')
wpb = Pawn('white', 'b')
wpc = Pawn('white', 'c')
wpd = Pawn('white', 'd')
wpe = Pawn('white', 'e')
wpf = Pawn('white', 'f')
wpg = Pawn('white', 'g')
wph = Pawn('white', 'h')

bk = King('black')
bq = Queen('black')
br1 = Rook('black', 'a')
br2 = Rook('black', 'h')
bn1 = Knight('black', 'b')
bn2 = Knight('black', 'g')
bb1 = Bishop('black', 'c')
bb2 = Bishop('black', 'f')
bpa = Pawn('black', 'a')
bpb = Pawn('black', 'b')
bpc = Pawn('black', 'c')
bpd = Pawn('black', 'd')
bpe = Pawn('black', 'e')
bpf = Pawn('black', 'f')
bpg = Pawn('black', 'g')
bph = Pawn('black', 'h')

white_pieces += [wk, wq, wr1, wr2, wn1, wn2, wb1, wb2, wpa, wpb, wpc, wpd, wpe, wpf, wpg, wph]
black_pieces += [bk, bq, br1, br2, bn1, bn2, bb1, bb2, bpa, bpb, bpc, bpd, bpe, bpf, bpg, bph]

board = [[br1, bn1, bb1, bq, bk, bb2, bn2, br2],
         [bpa, bpb, bpc, bpd, bpe, bpf, bpg, bph],
         [None, None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None, None],
         [wpa, wpb, wpc, wpd, wpe, wpf, wpg, wph],
         [wr1, wn1, wb1, wq, wk, wb2, wn2, wr2]]


while True:
    display()
    select_and_move(white_pieces)
    if bk.is_check_checkmate():
        display()
        break
    if bk.is_stalemate():
        display()
        break
    display()
    select_and_move(black_pieces)
    if wk.is_check_checkmate():
        display()
        break
    if wk.is_stalemate():
        display()
        break
