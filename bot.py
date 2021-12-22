#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is an example of a bot for the 3rd project.
    ...a pretty bad bot to be honest -_-
"""
import copy
import random
import math
from typing import List
from logging import DEBUG, debug, getLogger
import time

# We use the debugger to print messages to stderr
# You cannot use print as you usually do, the vm would intercept it
# You can hovever do the following:
#
# import sys
# print("HEHEY", file=sys.stderr)

getLogger().setLevel(DEBUG)

# WORKING WITH FIELD


def get_field_info():
    """
    Parse the info about the field.

    However, the function doesn't do anything with it. Since the height of the field is
    hard-coded later, this bot won't work with maps of different height.

    The input may look like this:

    Plateau 15 17:
    """
    field_info = input()
    debug(f"Description of the field: {field_info}")
    field_info = field_info.split()[1:]
    field_info[-1] = field_info[-1][:-1]
    field_info = [int(elem) for elem in field_info]
    return field_info


def get_field(field_size: list):
    """
    Parse the field.
    The input may look like this:

        01234567890123456
    000 .................
    001 .................
    002 .................
    003 .................
    004 .................
    005 .................
    006 .................
    007 .................
    008 ..O..............
    009 .................
    010 .................
    011 .................
    012 ..............X..
    013 .................
    014 .................

    :param player int: Represents whether we're the first or second player
    """
    field = []
    for i in range(field_size[0] + 1):
        row = input()
        # To be sure that the length of the field is appropriate.
        assert len(row) == field_size[1] + 4
        # debug(f"Field: {row}")
        if i != 0:
            field.append(row[4:])
    return field


def parse_info_about_player():
    """
    This function parses the info about the player

    It can look like this:

    $$$ exec p2 : [./player1.py]
    """
    i = input()
    debug(f"Info about the player: {i}")
    return 1 if "p1 :" in i else 2


# WORKING WITH FIGURE
def get_figure(player: int):
    """
    Parses the figure.

    The function parses the height of the figure (maybe the width would be
    useful as well), and then reads it.
    It would be nice to save it and return for further usage.

    The input may look like this:

    Piece 2 2:
    **
    ..
    """
    figure = []
    line = input()
    debug(f"Piece: {line}")
    height = int(line.split()[1])
    for _ in range(height):
        line = input()
        #debug(f"Piece: {line}")
        figure.append(line)
    return process_figure(figure, player)


def process_figure(figure: List[str], player: int):
    # Replaces '*' by the corresponding symbol
    for idx, each in enumerate(figure):
        figure[idx] = each.replace(
            '*', 'o') if player == 1 else each.replace('*', 'x')
    # Cuts the figure to the minimal size
    figure, offset = cut_figure_iterative(figure)
    return figure, offset


def cut_figure_iterative(figure: List[str]):
    offset = [0, 0]
    # Top
    while True:
        if figure[0] == '.' * len(figure[0]):
            figure = figure[1:]
            flag_top = True
            offset[0] += 1
        else:
            break
    # Bottom
    while True:
        if figure[-1] == '.' * len(figure[0]):
            figure = figure[:-1]
            flag_bottom = True
        else:
            break
    # Left
    while True:
        if ''.join([elem[0] for elem in figure]) == '.' * len(figure):
            for idx, line in enumerate(figure):
                figure[idx] = line[1:]
            flag_left = True
            offset[1] += 1
        else:
            break
    # Right
    while True:
        if ''.join([elem[-1] for elem in figure]) == '.' * len(figure):
            for idx, line in enumerate(figure):
                figure[idx] = line[:-1]
            flag_right = True
        else:
            break
    return (figure, offset)

# MAKING MOVE


def step(player: int):
    """
    Performs one step of the game.
    :param player int: Represents whether we're the first or second player
    """
    move = None
    field_size = get_field_info()
    field = get_field(field_size)
    figure, offset = get_figure(player)
    move = make_move(field, figure, offset, player)
    return move


def make_move(field: List[str], figure: List[str], offset: list, player: int):
    # TODO: Виправити обрізання на count
    move = None
    suitable_points = find_suitable_points(field, figure, offset, player)
    debug(f"Mr.Demchuk: {suitable_points}")
    if len(suitable_points) != 0:
        move = None
        priority_points = nearest_to_enemy(field, [(point[0] - offset[0], point[1] - offset[1]) for point in suitable_points], player)
        best_distance = min(priority_points.values())
        best_moves = []
        for point, dst in priority_points.items():
            debug(dst)
            if dst == best_distance:
                # move = point
                best_moves.append(point)
        move = random.choice(best_moves)
        if not move is None:
            debug(f'best_move: {move}, {best_distance}')
        if move is None:
            debug('Unable to choose best')
            move = random.choice(suitable_points)
        debug(offset)
        move = (move[0], move[1])
    else:
        move = (-1, -1)
    assert move is not None
    return move

# ALGORITHM


def find_suitable_points(field: List[str], figure: List[str], offset:List[int], player: int):
    suitable_points = []
    symbol = 'o' if player == 1 else 'x'
    for row, line in enumerate(field):
        for column, char in enumerate(line.lower()):
            if char == symbol:
                for f_row in range(len(figure)):
                    for f_col in range(len(figure[0])):
                        if (can_be_pasted(field, figure, [row - f_row, column - f_col], symbol)):
                            suitable_points.append(
                                (row - f_row, column - f_col))
    return list(set(suitable_points))


def can_be_pasted(field: List[str], figure: List[str], coords: List[int], symbol: str):
    if coords[0] < 0 or coords[1] < 0:
        return False
    if coords[0] + len(figure) > len(field) or \
            coords[1] + len(figure[0]) > len(field[0]):
        return False

    enemy_symbol = 'x' if symbol == 'o' else 'o'
    # Then checking for suitability
    before = []
    for line in field[coords[0]: coords[0] + len(figure)]:
        line = line.lower()
        before.append(line[coords[1]: coords[1] + len(figure[0])])

    after = copy.copy(before)
    for row, line in enumerate(figure):
        lst = list(after[row])
        for col, char in enumerate(line):
            if char != '.':
                lst[col] = char
        after[row] = ''.join(lst)

    symbol_counter_figure = 0
    for line in figure:
        symbol_counter_figure += line.count(symbol)

    symbol_counter_before = 0
    symbol_counter_after = 0
    for row, line in enumerate(before):
        symbol_counter_before += line.count(symbol)
        symbol_counter_after += after[row].count(symbol)
        for col, char in enumerate(line):
            if char == enemy_symbol and after[row][col] != enemy_symbol:
                return False
    if symbol_counter_after - symbol_counter_before == symbol_counter_figure - 1:
        return True
    return False


def nearest_to_enemy(field: List[str], points: List[int], player: int):
    radiuses = {}
    for point in points:
        radiuses[point] = find_square_radius(field, point, player)
    return radiuses


def find_square_radius(field: List[str], point: tuple, player: int):
    enemy_symbol = 'x' if player == 1 else 'o'
    top_left_bound = [point[0], point[1]]
    bottom_right_bound = [point[0], point[1]]
    closest_enemies = set()
    while len(closest_enemies) == 0:
        if top_left_bound[0] - 1 >= 0:
            top_left_bound[0] -= 1
        if top_left_bound[1] - 1 >= 0:
            top_left_bound[1] -= 1
        if bottom_right_bound[0] + 1 < len(field):
            bottom_right_bound[0] += 1
        if bottom_right_bound[1] + 1 < len(field[0]):
            bottom_right_bound[1] += 1
        closest_enemies |= points_in_square(
            field, top_left_bound, bottom_right_bound, enemy_symbol)

    closest_enemy = closest_enemies.pop()
    while len(closest_enemies) != 0:
        tmp_point = closest_enemies.pop()
        if distance(closest_enemy, point) > distance(tmp_point, point):
            closest_enemy = tmp_point
    return distance(closest_enemy, point)


def points_in_square(field: List[str], top_left_bound: List[int], bottom_right_bound: List[int], char: str):
    points = set()
    for row in range(top_left_bound[0], bottom_right_bound[0] + 1):
        for col in range(top_left_bound[1], bottom_right_bound[1] + 1):
            if field[row][col].lower() == char:
                points.add((row, col))
    return points


def distance(pointA: tuple, pointB: tuple):
    return math.sqrt((pointA[0] - pointB[0])**2 + (pointA[1] - pointB[1])**2)


def play(player: int):
    """
    Main game loop.

    :param player int: Represents whether we're the first or second player
    """
    while True:
        move = step(player)
        print(*move)


def main():
    player = parse_info_about_player()
    try:
        play(player)
    except EOFError:
        debug("Cannot get input. Seems that we've lost ):")


if __name__ == "__main__":
    main()
