from enum import Enum


class Action(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    CONFIRM = 4
    BACK = 5

    NEXT = 10
    PREVIOUS = 11

    SPEAK = 20

    DEBUG = 100
    SAVE = 101
