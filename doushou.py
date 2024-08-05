import sys
from enum import Enum
import pygame
from collections import namedtuple
from collections import deque
import random

GRID_LINE_COLOR = (0, 0, 0)   # 棋盘格子线颜色

FPS = 20
SCREEN_SIZE = 610, 650

CHESS_WIDTH = 100
CHESS_HEIGHT = 100
Position = namedtuple("Position", ["x", "y"])


class CompareResult(Enum):
    WIN = 0
    EQUAL = 1
    LOSE = 2


class Doushou:

    top, left, space, lines = (120, 80, 150, 4)  # 棋盘格子位置相关
    chess_width, chess_height = CHESS_WIDTH, CHESS_HEIGHT

    animal_map = {}

    def __init__(self):
        try:
            self.blue_turn = True
            self.focus_pos_logic = None

            self._init_resources()
            self._init_sprites()

            self.font = pygame.font.SysFont("arial", 16)

            self.points = [[] for i in range(self.lines)]
            self._init_points()

            # 逻辑棋盘，当前棋子的位置
            self.__chess_board_logic = [[] for i in range(self.lines)]
            self.__cover_board_logic = [[] for i in range(self.lines)]

            self._init_game()
            self.draw_board()
        except pygame.error as e:
            print(e)

    def _init_resources(self):
        self.background_filename = "assets/bg.png"
        self.chessboard_filename = "assets/chessboard.png"
        self.cover_filename = "assets/cover.png"
        self.focus_rect_filename = "assets/focus_rect.png"

        self.blue_rat_filename = "assets/blue_rat.png"
        self.blue_cat_filename = "assets/blue_cat.png"
        self.blue_dog_filename = "assets/blue_dog.png"
        self.blue_wolf_filename = "assets/blue_wolf.png"
        self.blue_leopard_filename = "assets/blue_leopard.png"
        self.blue_tiger_filename = "assets/blue_tiger.png"
        self.blue_lion_filename = "assets/blue_lion.png"
        self.blue_elephant_filename = "assets/blue_elephant.png"

        self.red_rat_filename = "assets/red_rat.png"
        self.red_cat_filename = "assets/red_cat.png"
        self.red_dog_filename = "assets/red_dog.png"
        self.red_wolf_filename = "assets/red_wolf.png"
        self.red_leopard_filename = "assets/red_leopard.png"
        self.red_tiger_filename = "assets/red_tiger.png"
        self.red_lion_filename = "assets/red_lion.png"
        self.red_elephant_filename = "assets/red_elephant.png"

    def _init_sprites(self):
        def _rescale_sprite(sprite, width=self.chess_width, height=self.chess_height):
            return pygame.transform.scale(sprite, (width, height))

        self._bg = pygame.image.load(self.background_filename)
        self._origin_chessboard = pygame.image.load(self.chessboard_filename)
        self._origin_chessboard = pygame.transform.scale(self._bg, SCREEN_SIZE)
        self._chessboard = self._origin_chessboard.copy()

        self._cover = _rescale_sprite(
            pygame.image.load(self.cover_filename).convert_alpha()
        )
        self._focus_rect = _rescale_sprite(
            pygame.image.load(self.focus_rect_filename).convert_alpha(),
            self.chess_width + 20,
            self.chess_height + 20,
        )

        self._blue_rat = _rescale_sprite(
            pygame.image.load(self.blue_rat_filename).convert_alpha()
        )
        self._blue_cat = _rescale_sprite(
            pygame.image.load(self.blue_cat_filename).convert_alpha()
        )
        self._blue_dog = _rescale_sprite(
            pygame.image.load(self.blue_dog_filename).convert_alpha()
        )
        self._blue_wolf = _rescale_sprite(
            pygame.image.load(self.blue_wolf_filename).convert_alpha()
        )
        self._blue_leopard = _rescale_sprite(
            pygame.image.load(self.blue_leopard_filename).convert_alpha()
        )
        self._blue_tiger = _rescale_sprite(
            pygame.image.load(self.blue_tiger_filename).convert_alpha()
        )
        self._blue_lion = _rescale_sprite(
            pygame.image.load(self.blue_lion_filename).convert_alpha()
        )
        self._blue_elephant = _rescale_sprite(
            pygame.image.load(self.blue_elephant_filename).convert_alpha()
        )

        self._red_rat = _rescale_sprite(
            pygame.image.load(self.red_rat_filename).convert_alpha()
        )
        self._red_cat = _rescale_sprite(
            pygame.image.load(self.red_cat_filename).convert_alpha()
        )
        self._red_dog = _rescale_sprite(
            pygame.image.load(self.red_dog_filename).convert_alpha()
        )
        self._red_wolf = _rescale_sprite(
            pygame.image.load(self.red_wolf_filename).convert_alpha()
        )
        self._red_leopard = _rescale_sprite(
            pygame.image.load(self.red_leopard_filename).convert_alpha()
        )
        self._red_tiger = _rescale_sprite(
            pygame.image.load(self.red_tiger_filename).convert_alpha()
        )
        self._red_lion = _rescale_sprite(
            pygame.image.load(self.red_lion_filename).convert_alpha()
        )
        self._red_elephant = _rescale_sprite(
            pygame.image.load(self.red_elephant_filename).convert_alpha()
        )

        self.animal_map = {
            self._blue_rat: 0,
            self._blue_cat: 1,
            self._blue_dog: 2,
            self._blue_wolf: 3,
            self._blue_leopard: 4,
            self._blue_tiger: 5,
            self._blue_lion: 6,
            self._blue_elephant: 7,
            self._red_rat: 8,
            self._red_cat: 9,
            self._red_dog: 10,
            self._red_wolf: 11,
            self._red_leopard: 12,
            self._red_tiger: 13,
            self._red_lion: 14,
            self._red_elephant: 15,
        }

    def _init_points(self):
        for i in range(self.lines):
            for j in range(self.lines):
                self.points[i].append(
                    Position(self.left + i * self.space, self.top + j * self.space)
                )

    # 画棋盘上的格子线
    def draw_board(self):
        self._chessboard = self._origin_chessboard.copy()
        for x in range(self.lines):
            # 画横线
            pygame.draw.line(
                self._chessboard,
                GRID_LINE_COLOR,
                self.points[0][x],
                self.points[self.lines - 1][x],
                width=5,
            )
            # 画竖线
            pygame.draw.line(
                self._chessboard,
                GRID_LINE_COLOR,
                self.points[x][0],
                self.points[x][self.lines - 1],
                width=5,
            )

    def draw_chesses(self):
        for i in range(self.lines):
            for j in range(self.lines):
                pos_x = self.points[i][j].x - int(self.chess_width / 2)
                pos_y = self.points[i][j].y - int(self.chess_height / 2)
                if self.__cover_board_logic[i][j] is True:  # 未翻开
                    self._chessboard.blit(self._cover, (pos_x, pos_y))
                elif (
                    self.focus_pos_logic is not None
                    and self.focus_pos_logic.x == i
                    and self.focus_pos_logic.y == j
                ):
                    # 有被选中的棋子
                    cover_pos_x = self.points[i][j].x - int((self.chess_width + 20) / 2)
                    cover_pos_y = self.points[i][j].y - int(
                        (self.chess_height + 20) / 2
                    )
                    self._chessboard.blit(self._focus_rect, (cover_pos_x, cover_pos_y))
                    self._chessboard.blit(
                        self.__chess_board_logic[i][j], (pos_x, pos_y)
                    )
                elif self.__chess_board_logic[i][j] is not None:
                    # 未选中但有棋子
                    self._chessboard.blit(
                        self.__chess_board_logic[i][j], (pos_x, pos_y)
                    )

    def draw_turn_text(self, font_obj: pygame.font.Font):
        turn_text = font_obj.render(
            f"现在是 <{'蓝' if self.blue_turn else '红'}> 方回合", True, (0, 0, 0)
        )
        self._chessboard.blit(turn_text, (self.left//3, self.top//6))

    def _init_game(self):
        random_animal_positions = [i for i in self.animal_map.keys()]
        random.shuffle(random_animal_positions)

        for i in range(self.lines):
            for j in range(self.lines):
                self.__chess_board_logic[i].append(
                    random_animal_positions[i * self.lines + j]
                )
                self.__cover_board_logic[i].append(True)

    # 点击了棋盘(i,j)位置操作
    def click_at(self, i, j):
        if i == -1 or j == -1:
            if self.focus_pos_logic is not None:
                # 取消选中
                self.focus_pos_logic = None
            return

        # 翻开棋子
        if self.__cover_board_logic[i][j] is True:
            self.__cover_board_logic[i][j] = False
            self.blue_turn = not self.blue_turn  # 切换蓝红方顺序
            return

        if self.focus_pos_logic is None:
            if self.__chess_board_logic[i][j] is not None and self.__is_own_chess(self.__chess_board_logic[i][j]) is True:
                # 如果之前没有选中，现点击了自己的棋子，则选中自己的棋子
                self.focus_pos_logic = Position(i, j)
        else:  # 如果之前选中了棋子
            if self.__chess_board_logic[i][j] is None:  # 选择了空地
                if self.focus_pos_logic is not None and (
                    (
                        abs(self.focus_pos_logic.x - i) == 1
                        and abs(self.focus_pos_logic.y - j) == 0
                    )
                    or (
                        abs(self.focus_pos_logic.x - i) == 0
                        and abs(self.focus_pos_logic.y - j) == 1
                    )
                ):  # 如果是附近的空地
                    # 移动到该位置
                    self.__chess_board_logic[i][j] = self.__chess_board_logic[
                        self.focus_pos_logic.x
                    ][self.focus_pos_logic.y]
                    self.__chess_board_logic[self.focus_pos_logic.x][
                        self.focus_pos_logic.y
                    ] = None
                    self.focus_pos_logic = None
                    self.blue_turn = not self.blue_turn  # 切换蓝红方顺序
            else:  # 选择了棋子
                if (
                    self.__is_own_chess(self.__chess_board_logic[i][j]) is True
                ):  # 如果是己方棋子
                    # 选择己方棋子，重新聚焦
                    self.focus_pos_logic = Position(i, j)
                else:  # 如果是对方棋子
                    if (
                        abs(self.focus_pos_logic.x - i) == 1
                        and abs(self.focus_pos_logic.y - j) == 0
                    ) or (
                        abs(self.focus_pos_logic.x - i) == 0
                        and abs(self.focus_pos_logic.y - j) == 1
                    ):  # 如果在附近
                        focus_chess = self.__chess_board_logic[self.focus_pos_logic.x][
                            self.focus_pos_logic.y
                        ]
                        compare_res = self.compare_chess(
                            focus_chess, self.__chess_board_logic[i][j]
                        )
                        if compare_res == CompareResult.WIN:
                            # 移动并吃掉对方棋子
                            self.__chess_board_logic[i][j] = self.__chess_board_logic[
                                self.focus_pos_logic.x
                            ][self.focus_pos_logic.y]
                            self.__chess_board_logic[self.focus_pos_logic.x][
                                self.focus_pos_logic.y
                            ] = None
                        elif compare_res == CompareResult.EQUAL:
                            # 双方棋子都消失
                            self.__chess_board_logic[i][j] = None
                            self.__chess_board_logic[self.focus_pos_logic.x][
                                self.focus_pos_logic.y
                            ] = None
                        elif compare_res == CompareResult.LOSE:
                            # 己方棋子消失
                            self.__chess_board_logic[self.focus_pos_logic.x][
                                self.focus_pos_logic.y
                            ] = None
                        self.focus_pos_logic = None
                        self.blue_turn = not self.blue_turn  # 切换蓝红方顺序

    # 通过物理坐标获取逻辑坐标
    def get_coord(self, pos):
        x, y = pos
        i, j = (-1, -1)
        oppo_x = x - self.left + self.chess_width // 2
        if oppo_x > 0 and oppo_x % self.space <= 100:
            i = int(oppo_x / self.space)  # 四舍五入取整
        oppo_y = y - self.top + self.chess_height // 2
        if oppo_y > 0 and oppo_y % self.space <= 100:
            j = int(oppo_y / self.space)
        return (i, j)

    def compare_chess(self, chess1, chess2):
        val1 = (
            self.animal_map[chess1]
            if self.animal_map[chess1] < 8
            else self.animal_map[chess1] - 8
        )
        val2 = (
            self.animal_map[chess2]
            if self.animal_map[chess2] < 8
            else self.animal_map[chess2] - 8
        )
        # 老鼠和大象
        if val1 == 0 and val2 == 7:
            return CompareResult.WIN
        elif val1 == 7 and val2 == 0:
            return CompareResult.LOSE

        if val1 > val2:
            return CompareResult.WIN
        elif val1 == val2:
            return CompareResult.EQUAL
        else:
            return CompareResult.LOSE

    def __is_own_chess(self, chess: pygame.Surface) -> bool:
        return (self.blue_turn is True and self.animal_map[chess] < 8) or (
            self.blue_turn is not True and self.animal_map[chess] >= 8
        )


def main():
    pygame.init()

    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    pygame.display.set_caption("斗兽棋")
    font = pygame.font.Font("simhei.ttf", 26)
    font.set_bold(True)
    clock = pygame.time.Clock()  # 设置时钟

    game_over = False
    doushou = Doushou()

    while True:
        clock.tick(FPS)  # 设置帧率
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                break
            if event.type == pygame.MOUSEBUTTONDOWN and (not game_over):
                if event.button == 1:  # 按下的是鼠标左键
                    i, j = doushou.get_coord(event.pos)
                    doushou.click_at(i, j)
                    print(f"现在是 <{'蓝' if doushou.blue_turn else '红'}> 方回合")

        if game_over is True:
            break
        doushou.draw_board()
        doushou.draw_turn_text(font)
        doushou.draw_chesses()
        screen.blit(doushou._chessboard, (0, 0))
        pygame.display.update()
    pygame.quit()
    sys.exit()


main()
