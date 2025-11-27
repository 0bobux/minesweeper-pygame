import pygame
from settings import *
from sprites import *


class Game:
    """Главный игровой класс. Управляет окном, циклами, вводом и игрой."""
    def __init__(self):
        """
        Инициализирует окно, заголовок и игровой таймер.

        Creates:
            screen (pygame.Surface): главное окно игры.
            clock (pygame.time.Clock): используется для ограничения FPS.
        """
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

    def new(self):
        """
        Создаёт новое игровое поле.

        Создаёт объект Board и выводит его содержимое в консоль (для отладки).
        """
        self.board = Board()
        self.board.display_board()

    def run(self):
        """
        Основной игровой цикл.

        Управляет:
            обработкой событий
            перерисовкой экрана
            проверкой состояния (проигрыш/победа)

        Когда игра заканчивается — вызывает end_screen().
        """
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()
        else:
            self.end_screen()

    def draw(self):
        """
        Перерисовывает экран.

        Рисует:
            фон
            игровое поле

        После рисования обновляет экран с помощью pygame.display.flip().
        """
        self.screen.fill(BGCOLOUR)
        self.board.draw(self.screen)
        pygame.display.flip()

    def check_win(self):
        """
        Проверяет победу игрока.

        Returns:
            bool: True, если все незаминированные клетки открыты.
        """
        for row in self.board.board_list:
            for tile in row:
                if tile.type != "X" and not tile.revealed:
                    return False
        return True

    def events(self):
        """
        Обрабатывает все события pygame.

        Реагирует на:
            выход из игры (QUIT)
            левый клик (открытие клетки)
            правый клик (установка/снятие флага)
            завершение игры (проигрыш или победа)
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)

            if event.type == pygame.MOUSEBUTTONDOWN: # событие нажатия кнопки мыши
                mx, my = pygame.mouse.get_pos() # возвращает координаты мыши в пикселях
                mx //= TILESIZE
                my //= TILESIZE # получаем индексы клетки на поле

                if event.button == 1:
                    if not self.board.board_list[mx][my].flagged:
                        # функция открытия клетки, срабатывает при взрыве
                        if not self.board.dig(mx, my): # ==True
                            # обработка взрыва
                            # mx, my — координаты клетки, на которой взорвалась мина
                            for row in self.board.board_list:
                                for tile in row:
                                    if tile.type == "X":
                                        if tile.flagged:
                                            # правильно отмеченная мина — оставляем флаг
                                            continue
                                        elif tile == self.board.board_list[mx][my]:
                                            # мина, на которой взорвался клик
                                            tile.revealed = True
                                            tile.flagged = False
                                            tile.image = tile_exploded
                                        else:
                                            # остальные мины без флага
                                            tile.revealed = True
                                            tile.flagged = False
                                            tile.image = tile_mine
                                    elif tile.flagged:
                                        # неправильные флаги
                                        tile.revealed = True
                                        tile.flagged = False
                                        tile.image = tile_not_mine
                            # завершаем игру
                            self.playing = False

                if event.button == 3:
                    # переключает флаг, но только если тайл ещё не раскрыт
                    if not self.board.board_list[mx][my].revealed:
                        self.board.board_list[mx][my].flagged = not self.board.board_list[mx][my].flagged

                if self.check_win():
                    self.win = True
                    self.playing = False
                    for row in self.board.board_list:
                        for tile in row:
                            if not tile.revealed: # для всех нераскрытых ячеек
                                tile.flagged = True # показывает, что все оставшиеся — мины

    def end_screen(self):
        """
        Ждёт клика мыши перед перезапуском.

        Используется как простая "пауза после окончания игры".

        Выход:
            Клик мыши запускает новую игру.
            Закрытие окна завершает программу.
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    return


game = Game()
while True:
    game.new()
    game.run()



