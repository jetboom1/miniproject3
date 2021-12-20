#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import DEBUG, debug, getLogger
import copy
import math

""" 
 To do:
 - Функція, яка парсить поле (Приймає через інпут строку, повертає список списків)
 - Функція, яка парсить фігуру (Приймає через інпут фігуру, повертає список списків)
 - Функція, яка ставить фігуру на поле - приймає поле, фігуру, стартову точку, повертає список з кортежів з 2 елементів
                                                                 (координати розташування фігури)
 - Функція, яка рахує хевристичну дистанцію - приймає 2 кортежі (координати крайньої нашої і крайньої точки противника),
                                             повертає число
 - Функція, яка обирає найкращу точку як стартову для наступної фігури, базуючись на хевристичній дистанції
    Приймає поле, та номер гравця. Повертає список кортежів [(y,x), (y,x)], де 1 елемент - своя базісна точка,
    2 елемент - базісна точка супротивника
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


def place_figure(figure_coords, figure, table):
    """
    Returns table with right-placed figure
    :param figure_coords: (y,x)
    :param figure: two-dimensional massive. Example: [['.', 'O'], ['O', 'O']]
    :param table: two-dimensional massive. Example: [['X','.','.'],['.','.','.'], ['.','.','O']]
    :return: table: two-dimensional massive. Example: [['X','X','.'],['X','.','.'], ['.','.','O']]
    """
    new_table = copy.deepcopy(table)
    y, x = figure_coords
    for y_f in range(len(figure)):
        for x_f in range(len(figure[y_f])):
            try:
                new_table[y+y_f][x+x_f] = figure[y_f][x_f]
            except IndexError:
                break
    return new_table

def all_placements_by_rules(table, figure, point, player):
    """
    Function that find and return all possible places by rules for given figure and field
    :param table: two-dimensional massive. Example: [['X','.','.'],['.','.','.'], ['.','.','O']]
    :param figure: two-dimensional massive. Example: [['.', 'O'], ['O', 'O']]
    :param point: 2-elements tuple with coordinates of the starting point. Example: (y,x)
    :param player: 1 if player is playing first (O`s), 2 if second (X`s)
    :return: list of tuples of 2 elements (coords of figure). Example: (y,x)
    """
    possible_variants = []
    chip = 'O' if player == 1 else 'X'
    enemy_chip = 'X' if player == 1 else 'O'
    my_chips = set([(row, x_chip) for row in range(len(table)) for x_chip in range(len(table[row]))
                               if table[row][x_chip] == chip])
    enemy_chips = set([(row, x_chip) for row in range(len(table)) for x_chip in range(len(table[row]))
                               if table[row][x_chip] == enemy_chip])
    chip_count = len(my_chips)
    enemy_chip_count = len(enemy_chips)
    figure_chip_count = ''.join(str(item) for ls in figure for item in ls).count(chip)
    # figure_enemy_chip_count = ''.join(str(item) for ls in figure for item in ls).count(enemy_chip)
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
            new_my_chips = set([(row, x_chip) for row in range(len(new_table)) for x_chip in range(len(new_table[row]))
                               if new_table[row][x_chip] == chip])
            new_enemy_chips = set([(row, x_chip) for row in range(len(new_table)) for x_chip in range(len(new_table[row]))
                               if new_table[row][x_chip] == enemy_chip])
            new_chip_count = len(new_my_chips)
            new_enemy_chip_count = len(new_enemy_chips)
            is_starting_chip_left = True if new_table[point[0]][point[1]] == chip else False
            if (chip_count + figure_chip_count - 1) == new_chip_count and \
                    my_chips.issubset(new_my_chips) and enemy_chips.issubset(new_enemy_chips) \
                    and not_broken and is_starting_chip_left:
                possible_variants.append((y,x))
    return possible_variants

def heuristic_distance(start_point, finish_point):
    """
    - Function that calculates the heuristic distance - takes 2 tuples
    (coordinates of our extreme and extreme point of the enemy),
    :param start_point: (y,x)
    :param finish_point: (y,x)
    :return: float - distance between two points
    """
    return math.sqrt((finish_point[0]-start_point[0])**2 + (finish_point[1]-start_point[1])**2)

def choose_base_point(table, player):
    """
    - Function that selects the best point as the starting point for the next figure, based on the heuristic distance
     Accepts the field and the player's number. Returns a tuple (y, x)
    :param table: list of lists
    :param player: 1 if player is playing first (O`s), 2 if second (X`s)
    :return: list of tuples [(y,x),(y,x)] - 1 element: coordinates of the basis point for the next figure
                                            2 element: coordinates of the enemy basis point
    """
    enemy_chips = []
    chips = []
    min_h_dist = False
    chip = 'O' if player == 1 else 'X'
    en_chip = 'X' if player == 1 else 'O'
    for y in range(len(table)):
        for x in range(len(table[y])):
            if table[y][x] == chip:
                chips.append((y, x))
            elif table[y][x] == en_chip:
                enemy_chips.append((y, x))
    for my_chip in chips:
        for enemy_chip in enemy_chips:
            h_dist = heuristic_distance(my_chip, enemy_chip)
            if not min_h_dist:
                min_h_dist = [h_dist, [my_chip, enemy_chip]]
            if h_dist < min_h_dist[0]:
                min_h_dist = [h_dist, [my_chip, enemy_chip]]
    return min_h_dist[1]

def choose_placement(table, figure, player):
    """
    - A function that selects the best shape for the figure based on the heuristic distance
     takes a table, list of tuples of 2 elements (coordinates of the location of the figure),
     a tuple of 2 elements (coordinates)
     :param table: list of lists
     :param figure: two-dimensional massive. Example: [['.', 'O'], ['O', 'O']]
     :param player: 1 if player is playing first (O`s), 2 if second (X`s)
     :return: table: list of lists
    """
    min_h_dist = False
    base_point = choose_base_point(table, player)[0]
    variants = all_placements_by_rules(table, figure, base_point, player)
    for figure_coords in variants:
        new_table = place_figure(figure_coords, figure, table)
        h_dist = choose_base_point(new_table, player)
        if not min_h_dist or min_h_dist[0] < choose_base_point(new_table, player)[0]:
            min_h_dist = h_dist
            min_h_dist.append(figure_coords)
    if not min_h_dist:
        return -1
    #result_table = place_figure(min_h_dist[-1], figure, table)
    return min_h_dist[-1]


def step(player: int):
    """
    Perform one step of the game.

    :param player:
    :param player int: Represents whether we're the first or second player
    """
    move = None
    height = parse_field_info()
    table = parse_field(height)
    figure = parse_figure(player)
    placement_coords = choose_placement(table, figure, player)
    if placement_coords == -1:
        debug("Error! There is no way to place this figure right!")
        return [0, 0]
    return list(placement_coords)
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
    # print(all_placements_by_rules([['.','X','.','.','.',],
    #                                ['.','.','.','O','.',],
    #                                ['.','O','O','O','.',],
    #                                ['.','.','.','.','.',],
    #                                ['.','.','.','.','.',]], [['.', 'O'],
    #                                                          ['.', 'O']], (2,2), 1))
    # print(heuristic_distance((2,2), (0,2)))
    # print(choose_base_point([['.','X','.','.','.',],
    #                          ['.','.','.','O','.',],
    #                          ['.','O','O','O','.',],
    #                          ['.','.','.','.','.',],
    #                          ['.','.','.','.','.',]], 1))
    # print(place_figure((3,0), [['.', '.', 'X'],
    #                           ['X', 'X', 'X']], [['.','.','X','.','.',],
    #                                              ['.','.','.','.','.',],
    #                                              ['.','.','O','.','.',],
    #                                              ['.','.','.','.','.',],
    #                                              ['.','.','.','.','.',]]))
    # print(choose_placement( [['.','X','.','.','.',],
    #                          ['.','.','.','O','.',],
    #                          ['.','O','O','O','.',],
    #                          ['.','.','.','.','.',],
    #                          ['.','.','.','.','.',]], [['.', 'O', '.'],
    #                                                    ['.', 'O', '.']], 1))
    main()
