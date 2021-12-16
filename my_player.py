#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import DEBUG, debug, getLogger
import copy


""" 
 To do:
 - Функція, яка парсить поле (Приймає через інпут строку, повертає список списків)
 - Функція, яка парсить фігуру (Приймає через інпут фігуру, повертає список списків)
 - Функція, яка ставить фігуру на поле - приймає поле, фігуру, повертає список з кортежів з 2 елементів
                                                                 (координати розташування фігури)
 - Функція, яка рахує хевристичну дистанцію - приймає 2 кортежі (координати крайньої нашої і крайньої точки противника),
                                             повертає число
 - Функція, яка обирає найкращий варіант постановки фігури, базуючись на хевристичній дистанції
         приймає список з кортежів з 2 елементів (координати розташування фігури), кортеж з 2 елементів (координат)
 - Функція, яка робить хід
 - Мейн цикл
"""

# We use the debugger to print messages to stderr
# You cannot use print as you usually do, the vm would intercept it
# You can hovever do the following:
#
# import sys
# print("HEHEY", file=sys.stderr)

getLogger().setLevel(DEBUG)


def parse_field_info():
    """
    Parse the info about the field.

    However, the function doesn't do anything with it. Since the height of the field is
    hard-coded later, this bot won't work with maps of different height.

    The input may look like this:

    Plateau 15 17:
    """
    l = input()
    height, width = map(int, l[8:-1].split(' '))
    debug(f"Height: {height}, width {width}")
    return height


def parse_field(height):
    """
    Parse the field.

    First of all, this function is also responsible for determining the next
    move. Actually, this function should rather only parse the field, and return
    it to another function, where the logic for choosing the move will be.

    Also, the algorithm for choosing the right move is wrong. This function
    finds the first position of _our_ character, and outputs it. However, it
    doesn't guarantee that the figure will be connected to only one cell of our
    territory. It can not be connected at all (for example, when the figure has
    empty cells), or it can be connected with multiple cells of our territory.
    That's definitely what you should address.

    Also, it might be useful to distinguish between lowecase (the most recent piece)
    and uppercase letters to determine where the enemy is moving etc.

    The input may look like this:

        01234567890123456
    000 .................
    001 .................
    002 .................
    003 .................
    004 .................
    005 .................
    006 .................
    007 ..O..............
    008 ..OOO............
    009 .................
    010 .................
    011 .................
    012 ..............X..
    013 .................
    014 .................

    :param player int: Represents whether we're the first or second player
    """
    table = []
    for i in range(height+1):
        row_input = input().strip()
        if not row_input.startswith('0123'):
            row = list(row_input[4:])
        else:
            continue
        table.append(row)
        #debug(row)
    return table

def parse_figure(player):
    """
    Parse the figure.

    The function parses the height and the width of the figure, and then reads it.
    Also it replaces *`s with player`s chips (O`s or X`s)
    It would be nice to save it and return for further usage.

    The input may look like this:

    Piece 2 2:
    **
    ..

    :param player: 1 if player is playing first (O`s), 2 if second (X`s)
    """
    l = input().strip()
    height, width = map(int, l[6:-1].split(' '))
    debug(f"Figure height: {height}")
    debug(f"Figure width: {width}")
    figure = []
    for _ in range(height):
        l = input()
        if int(player) == 1:
            l = l.replace('*', 'o')
        else:
            l = l.replace('*', 'x')
        row = list(l)
        figure.append(row)
    debug(f"Figure: {figure}")
    return figure

def all_placements_by_rules(table, figure, player):
    """
    Function that find and return all possible places by rules for given figure and field
    :param table: two-dimensional massive. Example: [['X','.','.'],['.','.','.'], ['.','.','O']]
    :param figure: two-dimensional massive. Example: [['.', 'O'], ['O', 'O']]
    :param player: 1 if player is playing first (O`s), 2 if second (X`s)
    :return: list of tuples of 2 elements (coords of figure). Example: (y,x)
    """
    possible_variants = []
    chip_count = ''.join(str(item) for ls in table for item in ls).count('O' if player == 1 else 'X')
    enemy_chip_count = ''.join(str(item) for ls in table for item in ls).count('X' if player == 1 else 'O')
    figure_chip_count = ''.join(str(item) for ls in figure for item in ls).count('O' if player == 1 else 'X')
    figure_enemy_chip_count = ''.join(str(item) for ls in figure for item in ls).count('X' if player == 1 else 'O')
    for y in range(len(table)):
        for x in range(len(table[y])):
            new_table = copy.deepcopy(table)
            not_broken = True
            for y_f in range(len(figure)):
                for x_f in range(len(figure[y_f])):
                    try:
                        new_table[y+y_f][x+x_f] = figure[y_f][x_f]
                    except IndexError:
                        not_broken = False
                        break
            new_chip_count = ''.join(str(item) for ls in new_table for item in ls).count('O' if player == 1 else 'X')
            new_enemy_chip_count = ''.join(str(item) for ls in new_table for item in ls).count('X' if player == 1 else 'O')
            if (chip_count + figure_chip_count - 1) == new_chip_count and \
                    enemy_chip_count == new_enemy_chip_count and not_broken:
                possible_variants.append((y,x))
    return possible_variants

def step(player: int):
    """
    Perform one step of the game.

    :param player int: Represents whether we're the first or second player
    """
    move = None
    height = parse_field_info()
    move = parse_field(height)
    parse_figure(player)
    return move
#
#
def play(player: int):
    """
    Main game loop.

    :param player int: Represents whether we're the first or second player
    """
    while True:
        move = step(player)
        print(*move)


def parse_info_about_player():
    """
    This function parses the info about the player

    It can look like this:

    $$$ exec p2 : [./player1]
    """
    i = input()
    debug(f"Info about the player: {i}")
    return 1 if "p1 :" in i else 2


def main():
    player = parse_info_about_player()
    try:
        play(player)
    except EOFError:
        debug("Cannot get input. Seems that we've lost ):")


if __name__ == "__main__":
    print(all_placements_by_rules([['X','.','.'],['.','.','.'], ['.','.','O']], [['.', 'O'], ['O', 'O']], 1))
    main()
