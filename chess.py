import copy
from utils import *


class Piece:
    def __init__(self, color: str, row: int, col: int):
        self.color, self.row, self.col = color, row, col
        if color == 'white':
            self.enemy = 'black'
        else:
            self.enemy = 'white'

    def _set_notation(self, notation: str):
        if self.color == 'white':
            self.notation = notation.upper()
        else:
            self.notation = notation.lower()


class King(Piece):
    def __init__(self, color: str, row: int, col: int):
        Piece.__init__(self, color, row, col)
        self._set_notation('k')


class Queen(Piece):
    def __init__(self, color: str, row: int, col: int):
        Piece.__init__(self, color, row, col)
        self._set_notation('q')


class Rook(Piece):
    def __init__(self, color: str, row: int, col: int):
        Piece.__init__(self, color, row, col)
        self._set_notation('r')


class Knight(Piece):
    def __init__(self, color: str, row: int, col: int):
        Piece.__init__(self, color, row, col)
        self._set_notation('n')


class Bishop(Piece):
    def __init__(self, color: str, row: int, col: int):
        Piece.__init__(self, color, row, col)
        self._set_notation('b')


class Pawn(Piece):
    def __init__(self, color: str, row: int, col: int):
        Piece.__init__(self, color, row, col)
        self._set_notation('p')
        self.step = -1 if self.color == 'white' else 1


class Position:

    def __init__(self, fen: str):

        self.pieces = {'white': {'king': [],
                                 'queen': [],
                                 'rook': [],
                                 'knight': [],
                                 'bishop': [],
                                 'pawn': []},
                       'black': {'king': [],
                                 'queen': [],
                                 'rook': [],
                                 'knight': [],
                                 'bishop': [],
                                 'pawn': []}
                       }
        self.castling_rights = {'white': {'short': False,
                                          'long': False},
                                'black': {'short': False,
                                          'long': False}
                                }
        self.army = {'white': [],
                     'black': []}

        piece_position, side, castling, enpassant_target, half_moves, full_moves = fen.split(' ')

        # piece position
        self.board = []
        rows = piece_position.split('/')
        for row in rows:
            board_row = []
            for char in row:
                if char.isdigit():
                    board_row.extend([None] * int(char))
                else:
                    row = len(self.board)
                    col = len(board_row)
                    if char.isupper():
                        color = 'white'
                    else:
                        color = 'black'
                    match char.lower():
                        case 'k':
                            self.army[color].append(King(color, row, col))
                            self.pieces[color]['king'].append(self.army[color][-1])
                        case 'q':
                            self.army[color].append(Queen(color, row, col))
                            self.pieces[color]['queen'].append(self.army[color][-1])
                        case 'r':
                            self.army[color].append(Rook(color, row, col))
                            self.pieces[color]['rook'].append(self.army[color][-1])
                        case 'n':
                            self.army[color].append(Knight(color, row, col))
                            self.pieces[color]['knight'].append(self.army[color][-1])
                        case 'b':
                            self.army[color].append(Bishop(color, row, col))
                            self.pieces[color]['bishop'].append(self.army[color][-1])
                        case 'p':
                            self.army[color].append(Pawn(color, row, col))
                            self.pieces[color]['pawn'].append(self.army[color][-1])
                    board_row.append(self.army[color][-1])
            self.board.append(board_row)

        # side to play
        if side == 'w':
            self.side_to_move = 'white'
        elif side == 'b':
            self.side_to_move = 'black'

        # castling
        if 'K' in castling:
            self.castling_rights['white']['short'] = True
        if 'Q' in castling:
            self.castling_rights['white']['long'] = True
        if 'k' in castling:
            self.castling_rights['black']['short'] = True
        if 'q' in castling:
            self.castling_rights['black']['long'] = True

        # enpassant target
        if enpassant_target == '-':
            self.enpassant_target = None
        else:
            self.enpassant_target = row_col_from(enpassant_target)

        # half moves
        self.half_moves = int(half_moves)

        # full moves
        self.full_moves = int(full_moves)

    def __getitem__(self, cell: tuple | str):
        if type(cell) == tuple:
            row, col = cell
        else:
            row, col = row_col_from(cell)
        return self.board[row][col]

    def __setitem__(self, cell: tuple | str, piece: Piece):
        if type(cell) == tuple:
            row, col = cell
        else:
            row, col = row_col_from(cell)
        self.board[row][col] = piece

    @staticmethod
    def _king_attacks(king: King):
        attacks = []
        for vertical in range(-1, 2):
            for horizontal in range(-1, 2):
                if vertical == 0 and horizontal == 0:
                    pass
                elif king.row+vertical > 7 or king.row+vertical < 0 or \
                        king.col+horizontal > 7 or king.col+horizontal < 0:
                    pass
                else:
                    attacks.append(tuple([king.row + vertical, king.col + horizontal]))
        return attacks

    def _queen_attacks(self, queen: Queen):
        attacks = []
        for up in range(1, queen.row + 1):
            if self.board[queen.row - up][queen.col] is None:
                attacks.append(tuple([queen.row - up, queen.col]))
            elif self.board[queen.row - up][queen.col] in self.army[queen.color]:
                attacks.append(tuple([queen.row - up, queen.col]))
                break
            else:
                attacks.append(tuple([queen.row - up, queen.col]))
                break
        for down in range(1, 8 - queen.row):
            if self.board[queen.row + down][queen.col] is None:
                attacks.append(tuple([queen.row + down, queen.col]))
            elif self.board[queen.row + down][queen.col] in self.army[queen.color]:
                attacks.append(tuple([queen.row + down, queen.col]))
                break
            else:
                attacks.append(tuple([queen.row + down, queen.col]))
                break
        for right in range(1, 8 - queen.col):
            if self.board[queen.row][queen.col + right] is None:
                attacks.append(tuple([queen.row, queen.col + right]))
            elif self.board[queen.row][queen.col + right] in self.army[queen.color]:
                attacks.append(tuple([queen.row, queen.col + right]))
                break
            else:
                attacks.append(tuple([queen.row, queen.col + right]))
                break
        for left in range(1, queen.col + 1):
            if self.board[queen.row][queen.col - left] is None:
                attacks.append(tuple([queen.row, queen.col - left]))
            elif self.board[queen.row][queen.col - left] in self.army[queen.color]:
                attacks.append(tuple([queen.row, queen.col - left]))
                break
            else:
                attacks.append(tuple([queen.row, queen.col - left]))
                break
        for up_right in range(1, min(queen.row + 1, 8 - queen.col)):
            if self.board[queen.row - up_right][queen.col + up_right] is None:
                attacks.append(tuple([queen.row - up_right, queen.col + up_right]))
            elif self.board[queen.row - up_right][queen.col + up_right] in self.army[queen.color]:
                attacks.append(tuple([queen.row - up_right, queen.col + up_right]))
                break
            else:
                attacks.append(tuple([queen.row - up_right, queen.col + up_right]))
                break
        for up_left in range(1, min(queen.row + 1, queen.col + 1)):
            if self.board[queen.row - up_left][queen.col - up_left] is None:
                attacks.append(tuple([queen.row - up_left, queen.col - up_left]))
            elif self.board[queen.row - up_left][queen.col - up_left] in self.army[queen.color]:
                attacks.append(tuple([queen.row - up_left, queen.col - up_left]))
                break
            else:
                attacks.append(tuple([queen.row - up_left, queen.col - up_left]))
                break
        for down_right in range(1, min(8 - queen.row, 8 - queen.col)):
            if self.board[queen.row + down_right][queen.col + down_right] is None:
                attacks.append(tuple([queen.row + down_right, queen.col + down_right]))
            elif self.board[queen.row + down_right][queen.col + down_right] in self.army[queen.color]:
                attacks.append(tuple([queen.row + down_right, queen.col + down_right]))
                break
            else:
                attacks.append(tuple([queen.row + down_right, queen.col + down_right]))
                break
        for down_left in range(1, min(8 - queen.row, queen.col + 1)):
            if self.board[queen.row + down_left][queen.col - down_left] is None:
                attacks.append(tuple([queen.row + down_left, queen.col - down_left]))
            elif self.board[queen.row + down_left][queen.col - down_left] in self.army[queen.color]:
                attacks.append(tuple([queen.row + down_left, queen.col - down_left]))
                break
            else:
                attacks.append(tuple([queen.row + down_left, queen.col - down_left]))
                break
        return attacks

    def _rook_attacks(self, rook: Rook):
        attacks = []
        for up in range(1, rook.row + 1):
            if self.board[rook.row - up][rook.col] is None:
                attacks.append(tuple([rook.row - up, rook.col]))
            elif self.board[rook.row - up][rook.col] in self.army[rook.color]:
                attacks.append(tuple([rook.row - up, rook.col]))
                break
            else:
                attacks.append(tuple([rook.row - up, rook.col]))
                break
        for down in range(1, 8 - rook.row):
            if self.board[rook.row + down][rook.col] is None:
                attacks.append(tuple([rook.row + down, rook.col]))
            elif self.board[rook.row + down][rook.col] in self.army[rook.color]:
                attacks.append(tuple([rook.row + down, rook.col]))
                break
            else:
                attacks.append(tuple([rook.row + down, rook.col]))
                break
        for right in range(1, 8 - rook.col):
            if self.board[rook.row][rook.col + right] is None:
                attacks.append(tuple([rook.row, rook.col + right]))
            elif self.board[rook.row][rook.col + right] in self.army[rook.color]:
                attacks.append(tuple([rook.row, rook.col + right]))
                break
            else:
                attacks.append(tuple([rook.row, rook.col + right]))
                break
        for left in range(1, rook.col + 1):
            if self.board[rook.row][rook.col - left] is None:
                attacks.append(tuple([rook.row, rook.col - left]))
            elif self.board[rook.row][rook.col - left] in self.army[rook.color]:
                attacks.append(tuple([rook.row, rook.col - left]))
                break
            else:
                attacks.append(tuple([rook.row, rook.col - left]))
                break
        return attacks

    @staticmethod
    def _knight_attacks(knight: Knight):
        attacks = []
        for move1 in [-2, 2]:
            for move2 in [-1, 1]:
                if knight.row+move1 < 0 or knight.row+move1 > 7 or knight.col+move2 < 0 or knight.col+move2 > 7:
                    pass
                else:
                    attacks.append(tuple([knight.row + move1, knight.col + move2]))
                if knight.row+move2 < 0 or knight.row+move2 > 7 or knight.col+move1 < 0 or knight.col+move1 > 7:
                    pass
                else:
                    attacks.append(tuple([knight.row + move2, knight.col + move1]))
        return attacks

    def _bishop_attacks(self, bishop: Bishop):
        attacks = []
        for up_right in range(1, min(bishop.row + 1, 8 - bishop.col)):
            if self.board[bishop.row - up_right][bishop.col + up_right] is None:
                attacks.append(tuple([bishop.row - up_right, bishop.col + up_right]))
            elif self.board[bishop.row - up_right][bishop.col + up_right] in self.army[bishop.color]:
                attacks.append(tuple([bishop.row - up_right, bishop.col + up_right]))
                break
            else:
                attacks.append(tuple([bishop.row - up_right, bishop.col + up_right]))
                break
        for up_left in range(1, min(bishop.row + 1, bishop.col + 1)):
            if self.board[bishop.row - up_left][bishop.col - up_left] is None:
                attacks.append(tuple([bishop.row - up_left, bishop.col - up_left]))
            elif self.board[bishop.row - up_left][bishop.col - up_left] in self.army[bishop.color]:
                attacks.append(tuple([bishop.row - up_left, bishop.col - up_left]))
                break
            else:
                attacks.append(tuple([bishop.row - up_left, bishop.col - up_left]))
                break
        for down_right in range(1, min(8 - bishop.row, 8 - bishop.col)):
            if self.board[bishop.row + down_right][bishop.col + down_right] is None:
                attacks.append(tuple([bishop.row + down_right, bishop.col + down_right]))
            elif self.board[bishop.row + down_right][bishop.col + down_right] in self.army[bishop.color]:
                attacks.append(tuple([bishop.row + down_right, bishop.col + down_right]))
                break
            else:
                attacks.append(tuple([bishop.row + down_right, bishop.col + down_right]))
                break
        for down_left in range(1, min(8 - bishop.row, bishop.col + 1)):
            if self.board[bishop.row + down_left][bishop.col - down_left] is None:
                attacks.append(tuple([bishop.row + down_left, bishop.col - down_left]))
            elif self.board[bishop.row + down_left][bishop.col - down_left] in self.army[bishop.color]:
                attacks.append(tuple([bishop.row + down_left, bishop.col - down_left]))
                break
            else:
                attacks.append(tuple([bishop.row + down_left, bishop.col - down_left]))
                break
        return attacks

    @staticmethod
    def _pawn_attacks(pawn: Pawn):
        attacks = []
        if pawn.col - 1 >= 0:
            attacks.append(tuple([pawn.row + pawn.step, pawn.col - 1]))
        if pawn.col + 1 <= 7:
            attacks.append(tuple([pawn.row + pawn.step, pawn.col + 1]))
        return attacks

    def _king_legal_moves(self, king: King):
        attacks = self.cells_attacked_by(king)
        legal = attacks.copy()
        for attack in attacks:
            row, col = attack
            if self.board[row][col] in self.army[king.color]:
                legal.remove(attack)
            else:
                for piece in self.army[king.enemy]:
                    if (row, col) in self.cells_attacked_by(piece):
                        legal.remove(attack)
                        break
        if self.castling_rights[king.color]['short']:
            if self.board[king.row][5] is not None:
                pass
            elif self.board[king.row][6] is not None:
                pass
            else:
                legal.append(tuple([king.row, 6]))
                for piece in self.army[king.enemy]:
                    if (king.row, 5) in self.cells_attacked_by(piece) or (king.row, 6) in self.cells_attacked_by(piece):
                        legal.remove(tuple([king.row, 6]))
                        continue
        if self.castling_rights[king.color]['long']:
            if self.board[king.row][3] is not None:
                pass
            elif self.board[king.row][2] is not None:
                pass
            elif self.board[king.row][1] is not None:
                pass
            else:
                legal.append(tuple([king.row, 2]))
                for piece in self.army[king.enemy]:
                    if (king.row, 3) in self.cells_attacked_by(piece) or \
                            (king.row, 2) in self.cells_attacked_by(piece) or \
                            (king.row, 1) in self.cells_attacked_by(piece):
                        legal.remove(tuple([king.row, 2]))
                        continue
        return legal

    def _qrnb_legal_moves(self, piece: Piece):
        attacks = self.cells_attacked_by(piece)
        legal = attacks.copy()
        for attack in attacks:
            row, col = attack
            if self.board[row][col] in self.army[piece.color]:
                legal.remove(attack)
            else:
                piece_on_attacked_cell = self.board[row][col]
                self.board[piece.row][piece.col] = None
                self.board[row][col] = piece
                for enemy_piece in self.army[piece.enemy]:
                    if (self.pieces[piece.color]['king'][0].row, self.pieces[piece.color]['king'][0].col) in \
                            self.cells_attacked_by(enemy_piece):
                        legal.remove(attack)
                self.board[piece.row][piece.col] = piece
                self.board[row][col] = piece_on_attacked_cell
        return legal

    def _pawn_legal_moves(self, pawn: Pawn):
        attacks = self.cells_attacked_by(pawn)
        legal = attacks.copy()
        for attack in attacks:
            row, col = attack
            if (self.board[row][col] is None or self.board[row][col] in self.army[pawn.color]) and \
                    (self.enpassant_target != attack):
                legal.remove(attack)
        temp_legal = legal.copy()
        if self.board[pawn.row + pawn.step][pawn.col] is None:
            temp_legal.append(tuple([pawn.row + pawn.step, pawn.col]))
        if pawn.row == 3.5 - 2.5 * pawn.step:
            if self.board[pawn.row + pawn.step][pawn.col] is None and \
                    self.board[pawn.row + 2*pawn.step][pawn.col] is None:
                temp_legal.append(tuple([pawn.row + 2*pawn.step, pawn.col]))
        legal = temp_legal.copy()
        for l_move in temp_legal:
            row, col = l_move
            piece_on_attacked_cell = self.board[row][col]
            self.board[pawn.row][pawn.col] = None
            self.board[row][col] = pawn
            for piece in self.army[pawn.enemy]:
                if (self.pieces[pawn.color]['king'][0].row, self.pieces[pawn.color]['king'][0].col) \
                        in self.cells_attacked_by(piece):
                    legal.remove(l_move)
                    break
            self.board[pawn.row][pawn.col] = pawn
            self.board[row][col] = piece_on_attacked_cell
        if pawn.row == int(3.5+2.5*pawn.step):
            temp_legal = []
            for move in legal:
                row, col = move
                for promote_to in ['queen', 'bishop', 'rook', 'knight']:
                    temp_legal.append((row, col, promote_to))
            legal = temp_legal
        return legal

    def _kill_piece(self, piece: Piece):
        self.army[piece.color].remove(piece)
        self[(piece.row, piece.col)] = None
        for name, piece_list in self.pieces[piece.color].items():
            if piece in piece_list:
                piece_list.remove(piece)

    def _castle(self, king: King, side: str):
        rook_col = 7 if side == 'short' else 0
        rook = self[tuple([king.row, rook_col])]
        self[tuple([king.row, rook_col])] = None
        self[tuple([king.row, int(4+rook_col/7)])] = rook
        rook.row, rook.col = king.row, int(4+rook_col/7)
        self.castling_rights[king.color]['short'] = False
        self.castling_rights[king.color]['long'] = False

    def _promote_pawn(self, pawn: Pawn, end_cell: tuple, promote_to: str):
        self._kill_piece(pawn)
        row, col = end_cell
        match promote_to:
            case 'queen':
                self[end_cell] = Queen(pawn.color, row, col)
            case 'rook':
                self[end_cell] = Rook(pawn.color, row, col)
            case 'bishop':
                self[end_cell] = Bishop(pawn.color, row, col)
            case 'knight':
                self[end_cell] = Knight(pawn.color, row, col)
        self.pieces[pawn.color][promote_to].append(self[end_cell])
        self.army[pawn.color].append(self[end_cell])

    def display(self):
        print(" " * 4, end="")
        print("+-----" * 8 + "+")
        for row_num, row in enumerate(self.board):
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

    def cells_attacked_by(self, piece: Piece):
        match piece.notation.lower():
            case 'k':
                return self._king_attacks(piece)
            case 'q':
                return self._queen_attacks(piece)
            case 'r':
                return self._rook_attacks(piece)
            case 'n':
                return self._knight_attacks(piece)
            case 'b':
                return self._bishop_attacks(piece)
            case 'p':
                return self._pawn_attacks(piece)

    def legal_moves(self, piece: Piece):
        match piece.notation.lower():
            case 'p':
                return self._pawn_legal_moves(piece)
            case 'k':
                return self._king_legal_moves(piece)
        return self._qrnb_legal_moves(piece)

    def all_legal_moves(self, color: str):
        all_legal_moves = []
        for piece in self.army[color]:
            for move in self.legal_moves(piece):
                all_legal_moves.append(tuple([piece, move]))
        return all_legal_moves

    def apply_move(self, move: tuple):
        self_copy = copy.deepcopy(self)
        # unpacking the prom_move tuple
        piece, end_cell = move
        piece = self_copy[(piece.row, piece.col)]
        is_double_push = False
        # non promotion moves
        if len(end_cell) == 2:
            # takes
            if self_copy[end_cell] is not None:
                self_copy.half_moves = -1
                self_copy._kill_piece(self_copy[end_cell])
            # pawn moves
            if type(piece) == Pawn:
                self_copy.half_moves = -1
                # en passant
                if end_cell == self_copy.enpassant_target:
                    self_copy._kill_piece(self_copy[(end_cell[0] - piece.step, end_cell[1])])
                # double prom_move
                if abs(end_cell[0]-piece.row) == 2:
                    is_double_push = True
                    self_copy.enpassant_target = (end_cell[0] - piece.step, end_cell[1])
            # castling
            if (type(piece) == King) and (abs(end_cell[1] - piece.col) == 2):
                side = 'short' if end_cell[1] == 6 else 'long'
                self_copy._castle(piece, side)
            # king prom_move
            if self_copy.castling_rights[piece.color]['short'] and \
                    self_copy.castling_rights[piece.color]['long'] and \
                    type(piece) == King:
                self_copy.castling_rights[piece.color]['short'] = False
                self_copy.castling_rights[piece.color]['long'] = False
            # rook prom_move
            if self_copy.castling_rights[piece.color]['short'] and \
                    type(piece) == Rook and \
                    piece.col == 7:
                self_copy.castling_rights[piece.color]['short'] = False
            if self_copy.castling_rights[piece.color]['long'] and \
                    type(piece) == Rook and \
                    piece.col == 0:
                self_copy.castling_rights[piece.color]['long'] = False
            # replacing the piece
            self_copy[tuple([piece.row, piece.col])] = None
            self_copy[end_cell] = piece
            piece.row, piece.col = end_cell
        # promotion prom_move
        else:
            promote_to = end_cell[2]
            end_cell = (end_cell[0], end_cell[1])
            self_copy._promote_pawn(piece, end_cell, promote_to)
            self_copy.half_moves = -1
        self_copy.half_moves += 1
        if not is_double_push:
            self_copy.enpassant_target = None
        return self_copy

    def is_check(self, color):
        king = self.pieces[color]['king'][0]
        for enemy in self.army[king.enemy]:
            if (king.row, king.col) in self.legal_moves(enemy):
                return True
        return False

    def is_checkmate(self, color):
        checkmate = False
        if self.is_check(color):
            checkmate = True
            for soldier in self.army[color]:
                if self.legal_moves(soldier):
                    checkmate = False
        return checkmate

    def is_stalemate(self, color):
        for soldier in self.army[color]:
            if self.legal_moves(soldier):
                return False
        return True

    def is_fifty_move_draw(self):
        if self.half_moves >= 50:
            return True
        return False


if __name__ == '__main__':

    def play_move(current_position, current_side_to_play):
        new_position = None
        print(f'{current_side_to_play} to move:', end='\t')
        start = input('select start square: ')
        piece = current_position[row_col_from(start)]
        if piece not in current_position.army[current_side_to_play]:
            print('\t\t\t\tinvalid square!')
            play_move(current_position, current_side_to_play)
        end = input('\t\t\t\tselect final square: ')
        end = row_col_from(end)
        if end in current_position.legal_moves(piece):
            new_position = current_position.apply_move((piece, end))
        elif type(piece) == Pawn:
            for move in current_position.legal_moves(piece):
                if end == (move[0], move[1]):
                    promote_to = input('\t\t\t\tpromote to: ')
                    new_position = current_position.apply_move((piece, (*end, promote_to)))
        else:
            print('\t\t\t\tinvalid move')
        if current_side_to_play == 'white':
            new_side_to_play = 'black'
        else:
            new_side_to_play = 'white'
        return new_position, new_side_to_play

    position = Position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    side_to_move = position.side_to_move

    while True:
        position.display()
        position, side_to_move = play_move(position, side_to_move)
        print(position.half_moves, position.full_moves)
        if position.is_checkmate(side_to_move):
            print('CHECKMATE!')
            print(f'{side_to_move.upper()} LOSES!')
            break
        elif position.is_check(side_to_move):
            print('CHECK!')
        elif position.is_stalemate(side_to_move):
            print('DRAW BY STALEMATE!')
            break
        elif position.is_fifty_move_draw():
            print('DRAW BY FIFTY MOVE RULE!')
            break
