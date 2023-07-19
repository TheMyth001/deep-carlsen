import copy
from utils import *
from DeepCarlsen.piece import *


class Position:
    """
    Class representing the chess reward and its pieces.

    Attributes:
        pieces: `dict` containing pieces classified based on color and type
        castling_rights: `dict` representing the short and long castling rights for either side
        army: `dict` containing pieces of each color
        board: 2D `list` for all the cells and their pieces
        side_to_move: white or black based on which side is to move
        enpassant_target: (row, col) tuple of the enpassant square
        half_moves: number of half moves since last capture or pawn push
        full_moves: total number of moves played in the game
    """

    def __init__(self, fen: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
        """
        Initialize a position based on the provided fen notation.
        Initializes the standard starting position if fen is not passed.
        :param fen: `string` with the fen notation of the position to be initialized.
        """
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
        """
        Getter method to get the `Piece` corresponding to a cell
        :param cell: can be (row, col) `tuple` or cell code
        :return: `Piece` on the reward corresponding to the cell
        """
        if type(cell) == tuple:
            row, col = cell
        else:
            row, col = row_col_from(cell)
        return self.board[row][col]

    def __setitem__(self, cell: tuple | str, piece: Piece):
        """
        Setter method to set a `Piece` on a cell
        :param cell: can be (row, col) `tuple` or cell code
        :param piece: `Piece` to be placed on the cell
        """
        if type(cell) == tuple:
            row, col = cell
        else:
            row, col = row_col_from(cell)
        self.board[row][col] = piece

    @staticmethod
    def _king_attacks(king: King):
        """
        :param king: required `King` object
        :return: `list` containing (row, col) `tuples` of all cells attacked by the king
        """
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
        """
        :param queen: required `Queen` object
        :return: `list` containing (row, col) `tuples` of all cells attacked by the queen
        """
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
        """
        :param rook: required `Rook` object
        :return: `list` containing (row, col) `tuples` of all cells attacked by the rook
        """
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
        """
        :param knight: required `Knight` object
        :return: `list` containing (row, col) `tuples` of all cells attacked by the knight
        """
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
        """
        :param bishop: required `Bishop` object
        :return: `list` containing (row, col) `tuples` of all cells attacked by the bishop
        """
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
        """
        :param pawn: required `Pawn` object
        :return: `list` containing (row, col) `tuples` of all cells attacked by the pawn
        """
        attacks = []
        if pawn.col - 1 >= 0:
            attacks.append(tuple([pawn.row + pawn.step, pawn.col - 1]))
        if pawn.col + 1 <= 7:
            attacks.append(tuple([pawn.row + pawn.step, pawn.col + 1]))
        return attacks

    def _king_legal_moves(self, king: King):
        """
        :param king: required `King` object
        :return: `list` containing (row, col) `tuples` of all legal moves of the king
        """
        attacks = self._cells_attacked_by(king)
        legal = attacks.copy()
        for attack in attacks:
            row, col = attack
            if self.board[row][col] in self.army[king.color]:
                legal.remove(attack)
            else:
                for piece in self.army[king.enemy]:
                    if (row, col) in self._cells_attacked_by(piece):
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
                    if (king.row, 5) in self._cells_attacked_by(piece) or (king.row, 6) in self._cells_attacked_by(
                            piece):
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
                    if (king.row, 3) in self._cells_attacked_by(piece) or \
                            (king.row, 2) in self._cells_attacked_by(piece) or \
                            (king.row, 1) in self._cells_attacked_by(piece):
                        legal.remove(tuple([king.row, 2]))
                        continue
        return legal

    def _qrnb_legal_moves(self, piece: Piece):
        """
        :param piece: required `Queen`/`Rook`/`Knight`/`Bishop` object
        :return: `list` containing (row, col) `tuples` of all legal moves of the piece
        """
        attacks = self._cells_attacked_by(piece)
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
                            self._cells_attacked_by(enemy_piece):
                        legal.remove(attack)
                self.board[piece.row][piece.col] = piece
                self.board[row][col] = piece_on_attacked_cell
        return legal

    def _pawn_legal_moves(self, pawn: Pawn):
        """
        :param pawn: required `Pawn` object
        :return: `list` containing (row, col) or (row, col, promote_to) `tuples` of all legal moves of the pawn
        """
        attacks = self._cells_attacked_by(pawn)
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
                        in self._cells_attacked_by(piece):
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
        """
        :param piece: the `Piece` to be killed
        """
        self.army[piece.color].remove(piece)
        self[(piece.row, piece.col)] = None
        for name, piece_list in self.pieces[piece.color].items():
            if piece in piece_list:
                piece_list.remove(piece)

    def _castle(self, king: King, side: str):
        """
        Apply castling on the reward and update the `Position` accordingly.
        :param king: `King` to be castled
        :param side: long or short
        """
        rook_col = 7 if side == 'short' else 0
        rook = self[tuple([king.row, rook_col])]
        self[tuple([king.row, rook_col])] = None
        self[tuple([king.row, int(4+rook_col/7)])] = rook
        rook.row, rook.col = king.row, int(4+rook_col/7)
        self.castling_rights[king.color]['short'] = False
        self.castling_rights[king.color]['long'] = False

    def _promote_pawn(self, pawn: Pawn, end_cell: tuple, promote_to: str):
        """
        Apply pawn promotion on the reward and update the `Position` accordingly.
        :param pawn: `Pawn` to be promoted
        :param end_cell: cell where the promotion is happening
        :param promote_to: 'queen' or 'rook' or 'knight' or 'bishop'
        """
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

    def _cells_attacked_by(self, piece: Piece):
        """
        Return the cells attacked by a piece.
        :param piece: required `Piece` object
        :return: `list` containing (row, col) `tuples` of the cells attacked by the piece
        """
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

    def _all_attacks(self, color: str):
        attacks = []
        for piece in self.army[color]:
            for cell in self._cells_attacked_by(piece):
                attacks.append(tuple([piece, cell]))
        return attacks

    def _lowest_attacker_defender(self, piece: Piece):
        enemy = 'white'
        if piece.color == 'white':
            enemy = 'black'
        attacker = 25
        defender = 25
        for attack in self._all_attacks(piece.color):
            if attack[1][0] == piece.row and attack[1][1] == piece.col:
                defender = min(defender, attack[0].value)
        for attack in self._all_attacks(enemy):
            if attack[1][0] == piece.row and attack[1][1] == piece.col:
                attacker = min(attacker, attack[0].value)
        return [attacker, defender]

    def _get_attack_map(self, color: str):
        attack_map = [[25, 25, 25, 25, 25, 25, 25, 25],
                      [25, 25, 25, 25, 25, 25, 25, 25],
                      [25, 25, 25, 25, 25, 25, 25, 25],
                      [25, 25, 25, 25, 25, 25, 25, 25],
                      [25, 25, 25, 25, 25, 25, 25, 25],
                      [25, 25, 25, 25, 25, 25, 25, 25],
                      [25, 25, 25, 25, 25, 25, 25, 25],
                      [25, 25, 25, 25, 25, 25, 25, 25],
                      ]

        for attack in self._all_attacks(color):
            attack_map[attack[1][0]][attack[1][1]] = min(attack_map[attack[1][0]][attack[1][1]], attack[0].value)
        attack_map_flat = []
        for i in range(8):
            attack_map_flat = attack_map_flat + attack_map[i]

        return attack_map_flat

    def _get_material_conf(self):
        """
        :return: list containing count of each piece and piece info
        """
        white_queens = len(self.pieces['white']['queen'])
        white_rooks = len(self.pieces['white']['rook'])
        white_knights = len(self.pieces['white']['knight'])
        white_bishops = len(self.pieces['white']['bishop'])
        white_pawns = len(self.pieces['white']['pawn'])
        black_queens = len(self.pieces['black']['queen'])
        black_rooks = len(self.pieces['black']['rook'])
        black_knights = len(self.pieces['black']['knight'])
        black_bishops = len(self.pieces['black']['bishop'])
        black_pawns = len(self.pieces['black']['pawn'])

        # slot: alive, row, col, attacker, defender
        white_king_slot = [self.pieces['white']['king'][0].row - 3.5,
                           self.pieces['white']['king'][0].col - 3.5,
                           len(self.legal_moves(self.pieces['white']['king'][0])),
                           ] + self._lowest_attacker_defender(self.pieces['white']['king'][0])

        white_queen_slot = [white_queens]
        rest_slot = [None, None, None, None, None] if (white_queens == 0) else \
            [self.pieces['white']['queen'][0].row - 3.5,
             self.pieces['white']['queen'][0].col - 3.5,
             len(self.legal_moves(self.pieces['white']['queen'][0])),
             ] + self._lowest_attacker_defender(self.pieces['white']['queen'][0])
        white_queen_slot += rest_slot

        white_rook1_slot = [1 * (white_rooks > 0)]
        rest_slot = [None, None, None, None, None] if (white_rooks < 1) else \
            [self.pieces['white']['rook'][0].row - 3.5,
             self.pieces['white']['rook'][0].col - 3.5,
             len(self.legal_moves(self.pieces['white']['rook'][0])),
             ] + self._lowest_attacker_defender(self.pieces['white']['rook'][0])
        white_rook1_slot += rest_slot
        white_rook2_slot = [1 * (white_rooks > 1)]
        rest_slot = [None, None, None, None, None] if (white_rooks < 2) else \
            [self.pieces['white']['rook'][1].row - 3.5,
             self.pieces['white']['rook'][1].col - 3.5,
             len(self.legal_moves(self.pieces['white']['rook'][1])),
             ] + self._lowest_attacker_defender(self.pieces['white']['rook'][1])
        white_rook2_slot += rest_slot

        white_bishop1_slot = [1 * (white_bishops > 0)]
        rest_slot = [None, None, None, None, None] if (white_bishops < 1) else \
            [self.pieces['white']['bishop'][0].row - 3.5,
             self.pieces['white']['bishop'][0].col - 3.5,
             len(self.legal_moves(self.pieces['white']['bishop'][0])),
             ] + self._lowest_attacker_defender(self.pieces['white']['bishop'][0])
        white_bishop1_slot += rest_slot
        white_bishop2_slot = [1 * (white_bishops > 1)]
        rest_slot = [None, None, None, None, None] if (white_bishops < 2) else \
            [self.pieces['white']['bishop'][1].row - 3.5,
             self.pieces['white']['bishop'][1].col - 3.5,
             len(self.legal_moves(self.pieces['white']['bishop'][1])),
             ] + self._lowest_attacker_defender(self.pieces['white']['bishop'][1])
        white_bishop2_slot += rest_slot

        white_knight1_slot = [1 * (white_knights > 0)]
        rest_slot = [None, None, None, None, None] if (white_knights < 1) else \
            [self.pieces['white']['knight'][0].row - 3.5,
             self.pieces['white']['knight'][0].col - 3.5,
             len(self.legal_moves(self.pieces['white']['knight'][0])),
             ] + self._lowest_attacker_defender(self.pieces['white']['knight'][0])
        white_knight1_slot += rest_slot
        white_knight2_slot = [1 * (white_knights > 1)]
        rest_slot = [None, None, None, None, None] if (white_knights < 2) else \
            [self.pieces['white']['knight'][1].row - 3.5,
             self.pieces['white']['knight'][1].col - 3.5,
             len(self.legal_moves(self.pieces['white']['knight'][1])),
             ] + self._lowest_attacker_defender(self.pieces['white']['knight'][1])
        white_knight2_slot += rest_slot

        white_pawn1_slot = [1 * (white_pawns > 0)]
        rest_slot = [None, None, None, None, None] if (white_pawns < 1) else \
            [self.pieces['white']['pawn'][0].row - 3.5,
             self.pieces['white']['pawn'][0].col - 3.5,
             len(self.legal_moves(self.pieces['white']['pawn'][0]))
             ] + self._lowest_attacker_defender(self.pieces['white']['pawn'][0])
        white_pawn1_slot += rest_slot

        white_pawn2_slot = [1 * (white_pawns > 1)]
        rest_slot = [None, None, None, None, None] if (white_pawns < 2) else \
            [self.pieces['white']['pawn'][1].row - 3.5,
             self.pieces['white']['pawn'][1].col - 3.5,
             len(self.legal_moves(self.pieces['white']['pawn'][1]))
             ] + self._lowest_attacker_defender(self.pieces['white']['pawn'][1])
        white_pawn2_slot += rest_slot

        white_pawn3_slot = [1 * (white_pawns > 2)]
        rest_slot = [None, None, None, None, None] if (white_pawns < 3) else \
            [self.pieces['white']['pawn'][2].row - 3.5,
             self.pieces['white']['pawn'][2].col - 3.5,
             len(self.legal_moves(self.pieces['white']['pawn'][2]))
             ] + self._lowest_attacker_defender(self.pieces['white']['pawn'][2])
        white_pawn3_slot += rest_slot

        white_pawn4_slot = [1 * (white_pawns > 3)]
        rest_slot = [None, None, None, None, None] if (white_pawns < 4) else \
            [self.pieces['white']['pawn'][3].row - 3.5,
             self.pieces['white']['pawn'][3].col - 3.5,
             len(self.legal_moves(self.pieces['white']['pawn'][3]))
             ] + self._lowest_attacker_defender(self.pieces['white']['pawn'][3])
        white_pawn4_slot += rest_slot

        white_pawn5_slot = [1 * (white_pawns > 4)]
        rest_slot = [None, None, None, None, None] if (white_pawns < 5) else \
            [self.pieces['white']['pawn'][4].row - 3.5,
             self.pieces['white']['pawn'][4].col - 3.5,
             len(self.legal_moves(self.pieces['white']['pawn'][4]))
             ] + self._lowest_attacker_defender(self.pieces['white']['pawn'][4])
        white_pawn5_slot += rest_slot

        white_pawn6_slot = [1 * (white_pawns > 5)]
        rest_slot = [None, None, None, None, None] if (white_pawns < 6) else \
            [self.pieces['white']['pawn'][5].row - 3.5,
             self.pieces['white']['pawn'][5].col - 3.5,
             len(self.legal_moves(self.pieces['white']['pawn'][5]))
             ] + self._lowest_attacker_defender(self.pieces['white']['pawn'][5])
        white_pawn6_slot += rest_slot

        white_pawn7_slot = [1 * (white_pawns > 6)]
        rest_slot = [None, None, None, None, None] if (white_pawns < 7) else \
            [self.pieces['white']['pawn'][6].row - 3.5,
             self.pieces['white']['pawn'][6].col - 3.5,
             len(self.legal_moves(self.pieces['white']['pawn'][6]))
             ] + self._lowest_attacker_defender(self.pieces['white']['pawn'][6])
        white_pawn7_slot += rest_slot

        white_pawn8_slot = [1 * (white_pawns > 7)]
        rest_slot = [None, None, None, None, None] if (white_pawns < 8) else \
            [self.pieces['white']['pawn'][7].row - 3.5,
             self.pieces['white']['pawn'][7].col - 3.5,
             len(self.legal_moves(self.pieces['white']['pawn'][7]))
             ] + self._lowest_attacker_defender(self.pieces['white']['pawn'][7])
        white_pawn8_slot += rest_slot

        black_king_slot = [self.pieces['black']['king'][0].row - 3.5,
                           self.pieces['black']['king'][0].col - 3.5,
                           len(self.legal_moves(self.pieces['black']['king'][0])),
                           ] + self._lowest_attacker_defender(self.pieces['black']['king'][0])

        black_queen_slot = [black_queens]
        rest_slot = [None, None, None, None, None] if (black_queens == 0) else \
            [self.pieces['black']['queen'][0].row - 3.5,
             self.pieces['black']['queen'][0].col - 3.5,
             len(self.legal_moves(self.pieces['black']['queen'][0])),
             ] + self._lowest_attacker_defender(self.pieces['black']['queen'][0])
        black_queen_slot += rest_slot

        black_rook1_slot = [1 * (black_rooks > 0)]
        rest_slot = [None, None, None, None, None] if (black_rooks < 1) else \
            [self.pieces['black']['rook'][0].row - 3.5,
             self.pieces['black']['rook'][0].col - 3.5,
             len(self.legal_moves(self.pieces['black']['rook'][0])),
             ] + self._lowest_attacker_defender(self.pieces['black']['rook'][0])
        black_rook1_slot += rest_slot
        black_rook2_slot = [1 * (black_rooks > 1)]
        rest_slot = [None, None, None, None, None] if (black_rooks < 2) else \
            [self.pieces['black']['rook'][1].row - 3.5,
             self.pieces['black']['rook'][1].col - 3.5,
             len(self.legal_moves(self.pieces['black']['rook'][1])),
             ] + self._lowest_attacker_defender(self.pieces['black']['rook'][1])
        black_rook2_slot += rest_slot

        black_bishop1_slot = [1 * (black_bishops > 0)]
        rest_slot = [None, None, None, None, None] if (black_bishops < 1) else \
            [self.pieces['black']['bishop'][0].row - 3.5,
             self.pieces['black']['bishop'][0].col - 3.5,
             len(self.legal_moves(self.pieces['black']['bishop'][0])),
             ] + self._lowest_attacker_defender(self.pieces['black']['bishop'][0])
        black_bishop1_slot += rest_slot
        black_bishop2_slot = [1 * (black_bishops > 1)]
        rest_slot = [None, None, None, None, None] if (black_bishops < 2) else \
            [self.pieces['black']['bishop'][1].row - 3.5,
             self.pieces['black']['bishop'][1].col - 3.5,
             len(self.legal_moves(self.pieces['black']['bishop'][1])),
             ] + self._lowest_attacker_defender(self.pieces['black']['bishop'][1])
        black_bishop2_slot += rest_slot

        black_knight1_slot = [1 * (black_knights > 0)]
        rest_slot = [None, None, None, None, None] if (black_knights < 1) else \
            [self.pieces['black']['knight'][0].row - 3.5,
             self.pieces['black']['knight'][0].col - 3.5,
             len(self.legal_moves(self.pieces['black']['knight'][0])),
             ] + self._lowest_attacker_defender(self.pieces['black']['knight'][0])
        black_knight1_slot += rest_slot
        black_knight2_slot = [1 * (black_knights > 1)]
        rest_slot = [None, None, None, None, None] if (black_knights < 2) else \
            [self.pieces['black']['knight'][1].row - 3.5,
             self.pieces['black']['knight'][1].col - 3.5,
             len(self.legal_moves(self.pieces['black']['knight'][1])),
             ] + self._lowest_attacker_defender(self.pieces['black']['knight'][1])
        black_knight2_slot += rest_slot

        black_pawn1_slot = [1 * (black_pawns > 0)]
        rest_slot = [None, None, None, None, None] if (black_pawns < 1) else \
            [self.pieces['black']['pawn'][0].row - 3.5,
             self.pieces['black']['pawn'][0].col - 3.5,
             len(self.legal_moves(self.pieces['black']['pawn'][0]))
             ] + self._lowest_attacker_defender(self.pieces['black']['pawn'][0])
        black_pawn1_slot += rest_slot

        black_pawn2_slot = [1 * (black_pawns > 1)]
        rest_slot = [None, None, None, None, None] if (black_pawns < 2) else \
            [self.pieces['black']['pawn'][1].row - 3.5,
             self.pieces['black']['pawn'][1].col - 3.5,
             len(self.legal_moves(self.pieces['black']['pawn'][1]))
             ] + self._lowest_attacker_defender(self.pieces['black']['pawn'][1])
        black_pawn2_slot += rest_slot

        black_pawn3_slot = [1 * (black_pawns > 2)]
        rest_slot = [None, None, None, None, None] if (black_pawns < 3) else \
            [self.pieces['black']['pawn'][2].row - 3.5,
             self.pieces['black']['pawn'][2].col - 3.5,
             len(self.legal_moves(self.pieces['black']['pawn'][2]))
             ] + self._lowest_attacker_defender(self.pieces['black']['pawn'][2])
        black_pawn3_slot += rest_slot

        black_pawn4_slot = [1 * (black_pawns > 3)]
        rest_slot = [None, None, None, None, None] if (black_pawns < 4) else \
            [self.pieces['black']['pawn'][3].row - 3.5,
             self.pieces['black']['pawn'][3].col - 3.5,
             len(self.legal_moves(self.pieces['black']['pawn'][3]))
             ] + self._lowest_attacker_defender(self.pieces['black']['pawn'][3])
        black_pawn4_slot += rest_slot

        black_pawn5_slot = [1 * (black_pawns > 4)]
        rest_slot = [None, None, None, None, None] if (black_pawns < 5) else \
            [self.pieces['black']['pawn'][4].row - 3.5,
             self.pieces['black']['pawn'][4].col - 3.5,
             len(self.legal_moves(self.pieces['black']['pawn'][4]))
             ] + self._lowest_attacker_defender(self.pieces['black']['pawn'][4])
        black_pawn5_slot += rest_slot

        black_pawn6_slot = [1 * (black_pawns > 5)]
        rest_slot = [None, None, None, None, None] if (black_pawns < 6) else \
            [self.pieces['black']['pawn'][5].row - 3.5,
             self.pieces['black']['pawn'][5].col - 3.5,
             len(self.legal_moves(self.pieces['black']['pawn'][5]))
             ] + self._lowest_attacker_defender(self.pieces['black']['pawn'][5])
        black_pawn6_slot += rest_slot

        black_pawn7_slot = [1 * (black_pawns > 6)]
        rest_slot = [None, None, None, None, None] if (black_pawns < 7) else \
            [self.pieces['black']['pawn'][6].row - 3.5,
             self.pieces['black']['pawn'][6].col - 3.5,
             len(self.legal_moves(self.pieces['black']['pawn'][6]))
             ] + self._lowest_attacker_defender(self.pieces['black']['pawn'][6])
        black_pawn7_slot += rest_slot

        black_pawn8_slot = [1 * (black_pawns > 7)]
        rest_slot = [None, None, None, None, None] if (black_pawns < 8) else \
            [self.pieces['black']['pawn'][7].row - 3.5,
             self.pieces['black']['pawn'][7].col - 3.5,
             len(self.legal_moves(self.pieces['black']['pawn'][7]))
             ] + self._lowest_attacker_defender(self.pieces['black']['pawn'][7])
        black_pawn8_slot += rest_slot

        material_config = [white_queens, white_rooks, white_knights, white_bishops, white_pawns,
                           black_queens, black_rooks, black_knights, black_bishops, black_pawns]

        piece_list = white_king_slot + white_queen_slot + white_rook1_slot + white_rook2_slot + \
            white_knight1_slot + white_knight2_slot + white_bishop1_slot + white_bishop2_slot + \
            white_pawn1_slot + white_pawn2_slot + white_pawn3_slot + white_pawn4_slot + \
            white_pawn5_slot + white_pawn6_slot + white_pawn7_slot + white_pawn8_slot + \
            black_king_slot + black_queen_slot + black_rook1_slot + black_rook2_slot + \
            black_knight1_slot + black_knight2_slot + black_bishop1_slot + black_bishop2_slot + \
            black_pawn1_slot + black_pawn2_slot + black_pawn3_slot + black_pawn4_slot + \
            black_pawn5_slot + black_pawn6_slot + black_pawn7_slot + black_pawn8_slot

        return material_config + piece_list

    def _get_castling_rights(self):
        """
        :return: list containing castling rights
        """
        white_short = 1 * self.castling_rights['white']['short']
        white_long = 1 * self.castling_rights['white']['long']
        black_short = 1 * self.castling_rights['black']['short']
        black_long = 1 * self.castling_rights['black']['long']
        return [white_short, white_long, black_short, black_long]

    def get_state(self):
        """
        :return: state feature vector
        """
        side_to_move = 0
        if self.side_to_move == 'black':
            side_to_move = 1
        castling = self._get_castling_rights()
        pieces = self._get_material_conf()
        white_attack_map = self._get_attack_map('white')
        black_attack_map = self._get_attack_map('black')

        state = [side_to_move] + castling + pieces + white_attack_map + black_attack_map
        return state

    def display(self):
        """
        Print the position to view it.
        """
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

    def legal_moves(self, piece: Piece):
        """
        Return all the legal moves of a piece.
        :param piece: required `Piece` object
        :return: `list` containing (row, col) or (row, col, promote_to) `tuples` of the legal moves of the piece
        """
        match piece.notation.lower():
            case 'p':
                return self._pawn_legal_moves(piece)
            case 'k':
                return self._king_legal_moves(piece)
        return self._qrnb_legal_moves(piece)

    def all_legal_moves(self, color: str):
        """
        Returns all move tuples (piece, (row, col)) or (piece, (row, col, promote_to)) possible.
        """
        all_legal_moves = []
        for piece in self.army[color]:
            for move in self.legal_moves(piece):
                all_legal_moves.append(tuple([piece, move]))
        return all_legal_moves

    def apply_move(self, move: tuple):
        """
        Apply a specified move on the reward and return a copy of the new `Position`.
        :param move: move `tuple` (piece, (row, col)) or (piece, (row, col, promote_to))
        """
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

        # update side to move
        if self_copy.side_to_move == 'white':
            self_copy.side_to_move = 'black'
        else:
            self_copy.side_to_move = 'white'
        return self_copy

    def is_check(self, color):
        """
        Whether specified side is under check.
        """
        king = self.pieces[color]['king'][0]
        for enemy in self.army[king.enemy]:
            if (king.row, king.col) in self.legal_moves(enemy):
                return True
        return False

    def is_checkmate(self, color):
        """
        Whether specified side has been checkmated.
        """
        checkmate = False
        if self.is_check(color):
            checkmate = True
            for soldier in self.army[color]:
                if self.legal_moves(soldier):
                    checkmate = False
        return checkmate

    def is_stalemate(self, color):
        """
        Whether position is drawn by stalemate.
        """
        for soldier in self.army[color]:
            if self.legal_moves(soldier):
                return False
        return True

    def is_fifty_move_draw(self):
        """
        Whether position is drawn by 50 move draw rule.
        """
        if self.half_moves >= 50:
            return True
        return False


if __name__ == '__main__':
    pos = Position()
    pos.display()
