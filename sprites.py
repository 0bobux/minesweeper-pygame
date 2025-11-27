import random

import pygame
from settings import *

class Tile:
    """
    Класс одной клетки игрового поля.

    Attributes:
        x (int): позиция клетки по X в пикселях.
        y (int): позиция клетки по Y в пикселях.
        image (pygame.Surface): текущее изображение клетки.
        type (str): тип клетки:
            "." — неизвестная (пустая до генерации)
            "X" — мина
            "C" — цифра (подсказка)
        revealed (bool): открыта ли клетка.
        flagged (bool): помечена ли флажком.
    """
    def __init__(self, x, y, image, type, revealed=False, flagged=False):
        """
        Инициализирует клетку.

        Args:
            x (int): координата по X в клетках.
            y (int): координата по Y в клетках.
            image (pygame.Surface): картинка клетки.
            type (str): тип клетки ("X", ".", "C").
            revealed (bool): открыта ли клетка.
            flagged (bool): помечена ли флажком.
        """
        self.x, self.y = x * TILESIZE, y * TILESIZE # позиция в пикселях
        self.image = image # текущее изображение
        self.type = type # логическое значение тайла
        self.revealed = revealed # раскрыт ли тайл
        self.flagged = flagged # поставлен ли флаг

    def draw(self, board_surface):
        """
        Рисует клетку на поверхности игрового поля.

        Отображение зависит от состояния клетки:
            закрытая → TileUnknown
            открытая → своё изображение
            флажок → TileFlag
        """
        if not self.flagged and self.revealed:
            board_surface.blit(self.image, (self.x, self.y))
        elif self.flagged and not self.revealed:
            board_surface.blit(tile_flag, (self.x, self.y))
        elif not self.revealed:
            board_surface.blit(tile_unknown, (self.x, self.y))

    def __repr__(self):
        """
        Возвращает символ типа клетки для удобного вывода в консоль.

        Returns:
            str: строковое обозначение типа клетки.
        """
        return self.type


class Board:
    """
    Класс логики игрового поля.

    Управляет:
        генерацией мин
        расчётом подсказок
        открытием клеток
        рекурсивным открытием пустых областей
        отрисовкой поля
    """
    def __init__(self):
        """
        Создаёт пустое поле, размещает мины и вычисляет подсказки.

        Creates:
            board_surface (pygame.Surface): поверхность для рисования поля.
            board_list (list[list[Tile]]): матрица клеток.
            dug (list[tuple]): список уже открытых клеток (для защиты от бесконечной рекурсии).
        """
        self.board_surface = pygame.Surface((WIDTH, HEIGHT)) # вспомогательная поверхность, на ней рисуются все тайлы
        self.board_list = [[Tile(col, row, tile_empty, ".") for row in range(ROWS)] for col in range(COLS)] # двоичный список: внешний цикл по колонкам, внутренний — по строкам
        self.place_mines()
        self.place_clues() # для заполнения поля
        self.dug = [] # список уже «вскрытых» координат

    def place_mines(self):
        """
        Размещает мины случайным образом на поле.

        Гарантирует:
            не кладёт мину на уже занятую клетку
            общее число мин = AMOUNT_MINES
        """
        for _ in range(AMOUNT_MINES):
            while True:
                x = random.randint(0, COLS-1)
                y = random.randint(0, ROWS-1)

                if self.board_list[x][y].type == ".":
                    self.board_list[x][y].image = tile_mine
                    self.board_list[x][y].type = "X"
                    break

    def place_clues(self):
        """
        Вычисляет число мин вокруг каждой клетки.

        Если рядом ≥ 1 мины:
            клетка становится подсказкой "C"
            выбирается нужная картинка с цифрой
        """
        for x in range(COLS):
            for y in range(ROWS):
                if self.board_list[x][y].type != "X":
                    total_mines = self.check_neighbours(x, y)
                    if total_mines > 0:
                        self.board_list[x][y].image = tile_numbers[total_mines-1]
                        self.board_list[x][y].type = "C"


    @staticmethod
    def is_inside(x, y):
        """
        Проверяет, находится ли клетка в пределах поля.

        Args:
            x (int): координата по X.
            y (int): координата по Y.

        Returns:
            bool: True если клетка внутри поля.
        """
        return 0 <= x < COLS and 0 <= y < ROWS

    def check_neighbours(self, x, y):
        """
        Считает количество мин вокруг данной клетки.

        Args:
            x (int): координата клетки.
            y (int): координата клетки.

        Returns:
            int: число мин рядом.
        """
        total_mines = 0
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                neighbour_x = x + x_offset
                neighbour_y = y + y_offset
                if self.is_inside(neighbour_x, neighbour_y) and self.board_list[neighbour_x][neighbour_y].type == "X":
                    total_mines += 1

        return total_mines

    def draw(self, screen):
        """
        Рисует всё игровое поле на экран.

        Args:
            screen (pygame.Surface): главное окно игры.
        """
        self.board_surface.fill(DARKGREY) # Очищает board_surface фоном

        for row in self.board_list:
            for tile in row:
                tile.draw(self.board_surface)
        screen.blit(self.board_surface, (0, 0)) # Копирует финальную поверхность на экран.

    def dig(self, x, y):
        """
        Открывает клетку и управляет рекурсивным открытием пустых областей.

        Args:
            x (int): координата по X.
            y (int): координата по Y.

        Returns:
            bool:
                True — если всё нормально.
                False — если игрок попал на мину (проигрыш).
        """
        self.dug.append((x, y)) # отмечает, что клетка вскрыта
        if self.board_list[x][y].type == "X": # Если это мина
            self.board_list[x][y].revealed = True
            self.board_list[x][y].image = tile_exploded
            return False # произошёл взрыв
        elif self.board_list[x][y].type == "C": # Если это подсказка
            self.board_list[x][y].revealed = True
            return True

        self.board_list[x][y].revealed = True # пустая клетка

        # рекурсивно вызывает dig для всех соседних клеток в квадрате 3×3
        # при клике по пустому месту раскрываются все прилегающие пустые клетки и подсказки
        for nx in range(max(0, x-1), min(COLS-1, x+1) + 1):
            for ny in range(max(0, y-1), min(ROWS-1, y+1) + 1):
                if (nx, ny) not in self.dug:
                    self.dig(nx, ny)
        return True

    def display_board(self):
        """
        Выводит поле в консоль для отладки.

        Использует __repr__() у Tile.
        """
        for row in self.board_list:
            print(row)

