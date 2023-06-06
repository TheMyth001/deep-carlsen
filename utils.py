def row_col_from(cell: str):
    row = 8 - int(cell[1])
    col = ord(cell[0]) - 97
    return row, col


def cell_name_from(rc_tuple: tuple):
    row, col = rc_tuple
    cell = f'{chr(col + 97)}{str(8 - row)}'
    return cell
