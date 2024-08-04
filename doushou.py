import sys
from enum import Enum
import pygame
from collections import namedtuple
from collections import deque
import random

FPS=20
SCREEN_SIZE = 610, 610
Position = namedtuple("Position", ["x", "y"])

class CompareResult(Enum):
    WIN = 0
    EQUAL = 1
    LOSE = 2


class Doushou:

    top, left, space, lines = (80, 80, 150, 4)  # 棋盘格子位置相关
    color = (0, 0, 0)  # 棋盘格子线颜色
    chess_width, chess_height = 100, 100

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

            self._draw_board()
            self._init_game()
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
        self._chessboard = pygame.image.load(self.chessboard_filename)
        self._chessboard = pygame.transform.scale(
            self._bg, SCREEN_SIZE
        )
        self._cover = _rescale_sprite(pygame.image.load(self.cover_filename).convert_alpha())
        self._focus_rect = _rescale_sprite(pygame.image.load(self.focus_rect_filename).convert_alpha(), self.chess_width+20, self.chess_height+20)

        self._blue_rat = _rescale_sprite(pygame.image.load(self.blue_rat_filename).convert_alpha())
        self._blue_cat = _rescale_sprite(pygame.image.load(self.blue_cat_filename).convert_alpha())
        self._blue_dog = _rescale_sprite(pygame.image.load(self.blue_dog_filename).convert_alpha())
        self._blue_wolf = _rescale_sprite(pygame.image.load(self.blue_wolf_filename).convert_alpha())
        self._blue_leopard = _rescale_sprite(pygame.image.load(self.blue_leopard_filename).convert_alpha())
        self._blue_tiger = _rescale_sprite(pygame.image.load(self.blue_tiger_filename).convert_alpha())
        self._blue_lion = _rescale_sprite(pygame.image.load(self.blue_lion_filename).convert_alpha())
        self._blue_elephant = _rescale_sprite(pygame.image.load(self.blue_elephant_filename).convert_alpha())

        self._red_rat = _rescale_sprite(pygame.image.load(self.red_rat_filename).convert_alpha())
        self._red_cat = _rescale_sprite(pygame.image.load(self.red_cat_filename).convert_alpha())
        self._red_dog = _rescale_sprite(pygame.image.load(self.red_dog_filename).convert_alpha())
        self._red_wolf = _rescale_sprite(pygame.image.load(self.red_wolf_filename).convert_alpha())
        self._red_leopard = _rescale_sprite(pygame.image.load(self.red_leopard_filename).convert_alpha())
        self._red_tiger = _rescale_sprite(pygame.image.load(self.red_tiger_filename).convert_alpha())
        self._red_lion = _rescale_sprite(pygame.image.load(self.red_lion_filename).convert_alpha())
        self._red_elephant = _rescale_sprite(pygame.image.load(self.red_elephant_filename).convert_alpha())

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
            self._red_elephant: 15
        }

        self.origin_chessboard = pygame.image.load(self.chessboard_filename)
        self.origin_chessboard = pygame.transform.scale(
            self._bg, SCREEN_SIZE
        )

    def _init_points(self):
        for i in range(self.lines):
            for j in range(self.lines):
                self.points[i].append(
                    Position(self.left + i * self.space, self.top + j * self.space)
                )

    # 画棋盘上的格子线，如果棋盘背景图做的足够精确，可省略此步骤
    def _draw_board(self):
        for x in range(self.lines):
            # 画横线
            pygame.draw.line(
                self._chessboard,
                self.color,
                self.points[0][x],
                self.points[self.lines - 1][x],
                width=5
            )
            # 画竖线
            pygame.draw.line(
                self._chessboard,
                self.color,
                self.points[x][0],
                self.points[x][self.lines - 1],
                width=5
            )

    def _init_game(self):
        random_animal_positions = [i for i in self.animal_map.keys()]
        random.shuffle(random_animal_positions)

        for i in range(self.lines):
            for j in range(self.lines):
                self._chessboard.blit(
                    self._cover,
                    (self.points[i][j].x - self.chess_width/2, self.points[i][j].y - self.chess_height/2),
                )
                self.__chess_board_logic[i].append(random_animal_positions[i*self.lines+j])

                self.__cover_board_logic[i].append(True)

    # 点击了棋盘(i,j)位置操作
    def click_at(self, i, j):
        pos_x = self.points[i][j].x - int(self.chess_width/2)
        pos_y = self.points[i][j].y - int(self.chess_height/2)
        cover_pos_x = self.points[i][j].x - int((self.chess_width+20)/2)
        cover_pos_y = self.points[i][j].y - int((self.chess_height+20)/2)
        
        if i == -1 or j == -1:
            if self.focus_pos_logic is not None:
                # 取消选中
                focus_pos = Position(cover_pos_x, cover_pos_y)
                self.recover_bg(focus_pos, self._focus_rect)
                self._chessboard.blit(self.__chess_board_logic[i][j], (pos_x, pos_y))
                self.focus_pos_logic = None
            return
        
        if self.focus_pos_logic is None:   # 如果之前没有选中棋子
            if self.blue_turn is True and self.animal_map[self.__chess_board_logic[i][j]] < 8:	# 若蓝方操作
                # 选中蓝方棋子
                print("选中蓝方")
                self.focus_pos_logic = Position(i, j)
                self._chessboard.blit(self._focus_rect, (cover_pos_x, cover_pos_y))
                self._chessboard.blit(self.__chess_board_logic[i][j], (pos_x, pos_y))
            elif self.blue_turn is not True and self.animal_map[self.__chess_board_logic[i][j]] >= 8: # 若红方操作
                # 选中红方棋子
                self.focus_pos_logic = Position(i, j)
                self._chessboard.blit(self._focus_rect, (cover_pos_x, cover_pos_y))
                self._chessboard.blit(self.__chess_board_logic[i][j], (pos_x, pos_y))

        # 翻开棋子
        if self.__cover_board_logic[i][j] is True:
            self._chessboard.blit(self.__chess_board_logic[i][j], (pos_x, pos_y))
        # else:
        #     if self.blue_turn:	# 若蓝方操作
        #         if self.__chess_board_logic[i][j] is None:   # 选择了空地
        #             if self.focus_pos_logic is not None and (
        #                     (
        #                         abs(self.focus_pos_logic.x - i) == 1
        #                         and abs(self.focus_pos_logic.y - j) == 0
        #                     )
        #                     or (
        #                         abs(self.focus_pos_logic.x - i) == 0
        #                         and abs(self.focus_pos_logic.y - j) == 1
        #                     )
        #                 ):
        #                 # 移动到该位置
        #                 self.__chess_board_logic[i][j] = self.__chess_board_logic[self.focus_pos_logic.x][self.focus_pos_logic.y]
        #                 focus_pos = Position(cover_pos_x, cover_pos_y)
        #                 self.recover_bg(focus_pos, self._focus_rect)
        #         else:    # 选择了棋子
        #             if self.animal_map[self.__chess_board_logic[i][j]] < 8:
        #                 # 选择己方棋子
        #                 self.focus_pos_logic = Position(i, j)
        #                 self._chessboard.blit(self._focus_rect, (cover_pos_x, cover_pos_y))
        #                 self._chessboard.blit(self.__chess_board_logic[i][j], (pos_x, pos_y))
        #             elif self.animal_map[self.__chess_board_logic[i][j]] >= 8:
        #                 # 选择对方棋子(如果上一步已选择己方棋子且在附近)
        #                 if self.focus_pos_logic is not None and (
        #                     (
        #                         abs(self.focus_pos_logic.x - i) == 1
        #                         and abs(self.focus_pos_logic.y - j) == 0
        #                     )
        #                     or (
        #                         abs(self.focus_pos_logic.x - i) == 0
        #                         and abs(self.focus_pos_logic.y - j) == 1
        #                     )
        #                 ):
        #                     focus_chess = self.__chess_board_logic[self.focus_pos_logic.x][self.focus_pos_logic.y]
        #                     compare_res = self.compare_chess(focus_chess, self.__chess_board_logic[i][j])
        #                     if compare_res == CompareResult.WIN:
        #                         # 吃掉对方棋子
        #                         self.__chess_board_logic[i][j] = self.__chess_board_logic[self.focus_pos_logic.x][self.focus_pos_logic.y]
        #                         self._chessboard.blit(self.__chess_board_logic[i][j], (pos_x, pos_y))
        #                         focus_pos = Position(cover_pos_x, cover_pos_y)
        #                         self.recover_bg(focus_pos, self._focus_rect)
        #                     elif compare_res == CompareResult.EQUAL:
        #                         # 双方棋子都消失
        #                         self.__chess_board_logic[i][j] = None
        #                         self.__chess_board_logic[self.focus_pos_logic.x][self.focus_pos_logic.y] = None
        #                         focus_pos = Position(cover_pos_x, cover_pos_y)
        #                         self.recover_bg(focus_pos, self._focus_rect)
        #                         chess_pos = Position(pos_x, pos_y)
        #                         self.recover_bg(chess_pos, self.__chess_board_logic[i][j])
        #                     elif compare_res == CompareResult.LOSE:
        #                         # 己方棋子消失
        #                         self.__chess_board_logic[self.focus_pos_logic.x][self.focus_pos_logic.y] = None
        #                         focus_pos = Position(cover_pos_x, cover_pos_y)
        #                         self.recover_bg(focus_pos, self._focus_rect)
        #                     self.focus_pos_logic = None
        #     else:   # 若红方操作
        #         pass

        # self.blue_turn = not self.blue_turn	# 切换蓝红方顺序

    # 通过物理坐标获取逻辑坐标
    def get_coord(self, pos):
        x, y = pos
        i, j = (-1, -1)
        oppo_x = x - self.left + self.chess_width // 2
        if oppo_x > 0 and oppo_x % self.space <= 100:
            i = int(oppo_x / self.space)	# 四舍五入取整
        oppo_y = y - self.top + self.chess_height // 2
        if oppo_y > 0 and oppo_y % self.space <= 100:
            j = int(oppo_y / self.space)
        return (i, j)

    def compare_chess(self, chess1, chess2):
        val1 = self.animal_map[chess1] if self.animal_map[chess1] < 8 else self.animal_map[chess1] - 8
        val2 = self.animal_map[chess2] if self.animal_map[chess2] < 8 else self.animal_map[chess2] - 8
        if val1 > val2:
            return CompareResult.WIN
        elif val1 == val2:
            return CompareResult.EQUAL
        else:
            return CompareResult.LOSE

    def recover_bg(self, pos: Position, suf: pygame.Surface):
        # 从背景图片中截取指定区域
        cover_image = self.origin_chessboard.subsurface((pos.x, pos.y, suf.get_width(), suf.get_height()))
        # 在要删除的图片位置绘制截取的背景区域
        self._chessboard.blit(cover_image, (pos.x, pos.y))

class Renju(object):

    background_filename = "chessboard.png"
    white_chessball_filename = "white_chessball.png"
    black_chessball_filename = "black_chessball.png"
    top, left, space, lines = (20, 20, 36, 15)  # 棋盘格子位置相关???
    color = (0, 0, 0)  # 棋盘格子线颜色

    black_turn = True  # 黑子先手
    ball_coord = []  # 记录黑子和白子逻辑位置

    def init(self):
        try:
            self._chessboard = pygame.image.load(self.background_filename)
            self._white_chessball = pygame.image.load(
                self.white_chessball_filename
            ).convert_alpha()
            self._black_chessball = pygame.image.load(
                self.black_chessball_filename
            ).convert_alpha()
            self.font = pygame.font.SysFont("arial", 16)
            self.ball_rect = self._white_chessball.get_rect()
            self.points = [[] for i in range(self.lines)]
            for i in range(self.lines):
                for j in range(self.lines):
                    self.points[i].append(
                        Position(self.left + i * self.space, self.top + j * self.space)
                    )
            self._draw_board()
        except pygame.error as e:
            print(e)
            sys.exit()

    def chessboard(self):
        return self._chessboard

    # 在(i,j)位置落子
    def drop_at(self, i, j):
        pos_x = self.points[i][j].x - int(self.ball_rect.width / 2)
        pos_y = self.points[i][j].y - int(self.ball_rect.height / 2)

        ball_pos = {"type": 0 if self.black_turn else 1, "coord": Position(i, j)}
        if self.black_turn:  # 轮到黑子下
            self._chessboard.blit(self._black_chessball, (pos_x, pos_y))
        else:
            self._chessboard.blit(self._white_chessball, (pos_x, pos_y))

        self.ball_coord.append(ball_pos)  # 记录已落子信息
        self.black_turn = not self.black_turn  # 切换黑白子顺序

    # 画棋盘上的格子线，如果棋盘背景图做的足够精确，可省略此步骤
    def _draw_board(self):
        # 画坐标数字
        for i in range(1, self.lines):
            coord_text = self.font.render(str(i), True, self.color)
            self._chessboard.blit(
                coord_text,
                (
                    self.points[i][0].x - round(coord_text.get_width() / 2),
                    self.points[i][0].y - coord_text.get_height(),
                ),
            )
            self._chessboard.blit(
                coord_text,
                (
                    self.points[0][i].x - coord_text.get_width(),
                    self.points[0][i].y - round(coord_text.get_height() / 2),
                ),
            )

        for x in range(self.lines):
            # 画横线
            pygame.draw.line(
                self._chessboard,
                self.color,
                self.points[0][x],
                self.points[self.lines - 1][x],
            )
            # 画竖线
            pygame.draw.line(
                self._chessboard,
                self.color,
                self.points[x][0],
                self.points[x][self.lines - 1],
            )

    # 判断是否已产生胜方
    def check_over(self):
        if len(self.ball_coord) > 8:  # 只有黑白子已下4枚以上才判断
            direct = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 横、竖、斜、反斜 四个方向检查
            for d in direct:
                if self._check_direct(d):
                    return True
        return False

    # 判断最后一个棋子某个方向是否连成5子，direct:(1,0),(0,1),(1,1),(1,-1)
    def _check_direct(self, direct):
        dt_x, dt_y = direct
        last = self.ball_coord[-1]
        line_ball = []  # 存放在一条线上的棋子
        for ball in self.ball_coord:
            if ball["type"] == last["type"]:
                x = ball["coord"].x - last["coord"].x
                y = ball["coord"].y - last["coord"].y
                if dt_x == 0:
                    if x == 0:
                        line_ball.append(ball["coord"])
                        continue
                if dt_y == 0:
                    if y == 0:
                        line_ball.append(ball["coord"])
                        continue
                if x * dt_y == y * dt_x:
                    line_ball.append(ball["coord"])

        if len(line_ball) >= 5:  # 只有5子及以上才继续判断
            sorted_line = sorted(line_ball)
            for i, item in enumerate(sorted_line):
                index = i + 4
                if index < len(sorted_line):
                    if dt_x == 0:
                        y1 = item.y
                        y2 = sorted_line[index].y
                        if (
                            abs(y1 - y2) == 4
                        ):  # 此点和第5个点比较y值，如相差为4则连成5子
                            return True
                    else:
                        x1 = item.x
                        x2 = sorted_line[index].x
                        if (
                            abs(x1 - x2) == 4
                        ):  # 此点和第5个点比较x值，如相差为4则连成5子
                            return True
                else:
                    break
        return False

    # 检查(i,j)位置是否已占用
    def check_at(self, i, j):
        for item in self.ball_coord:
            if (i, j) == item["coord"]:
                return False
        return True

    # 通过物理坐标获取逻辑坐标
    def get_coord(self, pos):
        x, y = pos
        i, j = (0, 0)
        oppo_x = x - self.left
        if oppo_x > 0:
            i = round(oppo_x / self.space)  # 四舍五入取整
        oppo_y = y - self.top
        if oppo_y > 0:
            j = round(oppo_y / self.space)
        return (i, j)


def main():
    pygame.init()

    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    pygame.display.set_caption("斗兽棋")
    font = pygame.font.Font("simhei.ttf", 48)
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
                    print(event.pos)
                    i, j = doushou.get_coord(event.pos)
                    doushou.click_at(i, j)

        if game_over is True:
            break
        screen.blit(doushou._chessboard, (0, 0))
        pygame.display.update()
    pygame.quit()
    sys.exit()


main()
