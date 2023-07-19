class Piece:

    def __init__(self, color: str, row: int, col: int):
        """
        Initialize a piece
        :param color: white or black
        :param row: row number of the position of the piece on the reward
        :param col: column number of the position of the piece on the reward
        """
        self.color, self.row, self.col = color, row, col
        if color == 'white':
            self.enemy = 'black'
        else:
            self.enemy = 'white'

    def _set_notation(self, notation: str):
        """
        Set piece notation as uppercase or lowercase based on piece color
        :param notation: notation for piece
        """
        if self.color == 'white':
            self.notation = notation.upper()
        else:
            self.notation = notation.lower()


class King(Piece):
    def __init__(self, color: str, row: int, col: int):
        """
        Initialize a `King` object
        """
        Piece.__init__(self, color, row, col)
        self._set_notation('k')
        self.value = 15


class Queen(Piece):
    def __init__(self, color: str, row: int, col: int):
        """
        Initialize a `Queen` object
        """
        Piece.__init__(self, color, row, col)
        self._set_notation('q')
        self.value = 9


class Rook(Piece):
    def __init__(self, color: str, row: int, col: int):
        """
        Initialize a `Rook` object
        """
        Piece.__init__(self, color, row, col)
        self._set_notation('r')
        self.value = 5


class Knight(Piece):
    def __init__(self, color: str, row: int, col: int):
        """
        Initialize a `Knight` object
        """
        Piece.__init__(self, color, row, col)
        self._set_notation('n')
        self.value = 3


class Bishop(Piece):
    def __init__(self, color: str, row: int, col: int):
        """
        Initialize a `Bishop` object
        """
        Piece.__init__(self, color, row, col)
        self._set_notation('b')
        self.value = 3


class Pawn(Piece):
    def __init__(self, color: str, row: int, col: int):
        """
        Initialize a `Pawn` object
        """
        Piece.__init__(self, color, row, col)
        self._set_notation('p')
        self.step = -1 if self.color == 'white' else 1
        self.value = 1
