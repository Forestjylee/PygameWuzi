import sys
import json
import time
from enum import Enum
import pygame
from client import Client
from collections import namedtuple
from collections import deque
import random

GRID_LINE_COLOR = (0, 0, 0)  # 棋盘格子线颜色

FPS = 60
SCREEN_SIZE = 610, 650

CHESS_WIDTH = 100
CHESS_HEIGHT = 100
Position = namedtuple("Position", ["x", "y"])


class CompareResult(Enum):
    WIN = 0
    EQUAL = 1
    LOSE = 2


class GameResult(Enum):
    BLUE_WIN = 0
    RED_WIN = 1
    DRAW = 2
    NOT_OVER = 3


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
        self._chessboard.blit(turn_text, (self.left // 3, self.top // 6))

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
            return

        # 翻开棋子
        if self.__cover_board_logic[i][j] is True:
            self.__cover_board_logic[i][j] = False
            self.blue_turn = not self.blue_turn  # 切换蓝红方顺序
            self.focus_pos_logic = None
            return

        if self.focus_pos_logic is None:
            if (
                self.__chess_board_logic[i][j] is not None
                and self.__is_own_chess(self.__chess_board_logic[i][j]) is True
            ):
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
                    if self.focus_pos_logic.x == i and self.focus_pos_logic.y == j:
                        # 选择同一个棋子，取消聚焦
                        self.focus_pos_logic = None
                    else:
                        # 选择己方其他棋子，重新聚焦
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

    def check_over(self):
        blue_chess_amount = 0
        red_chess_amount = 0
        for i in range(self.lines):
            for j in range(self.lines):
                if self.__chess_board_logic[i][j] is None:
                    continue
                if self.animal_map[self.__chess_board_logic[i][j]] < 8:
                    blue_chess_amount += 1
                else:
                    red_chess_amount += 1

        if blue_chess_amount == 0 and red_chess_amount == 0:
            return GameResult.DRAW
        elif blue_chess_amount == 0 and red_chess_amount >= 0:
            return GameResult.RED_WIN
        elif blue_chess_amount >= 0 and red_chess_amount == 0:
            return GameResult.BLUE_WIN
        else:
            return GameResult.NOT_OVER

    def __is_own_chess(self, chess: pygame.Surface) -> bool:
        return (self.blue_turn is True and self.animal_map[chess] < 8) or (
            self.blue_turn is not True and self.animal_map[chess] >= 8
        )


def has_empty_room(rooms):
    for room in rooms:
        if room["nb_players"] < room["capacity"]:
            return True
    return False


def is_my_room_ready(client: Client):
    rooms = client.get_rooms()
    for room in rooms:
        if room["id"] == client.room_id:
            return room["nb_players"] == room["capacity"]


def main():
    pygame.init()

    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    pygame.display.set_caption("斗兽棋")
    font = pygame.font.Font("assets/simhei.ttf", 26)
    gameover_font = pygame.font.Font("assets/simhei.ttf", 48)
    font.set_bold(True)
    clock = pygame.time.Clock()  # 设置时钟

    # 开始游戏按钮
    text_color = (0, 0, 0)
    button_font = pygame.font.Font("assets/simhei.ttf", 60)
    button_text = button_font.render("开始游戏", True, text_color)
    bt_width, bt_height = button_text.get_width()+25, button_text.get_height()+15
    button_rect = pygame.Rect(
        round(SCREEN_SIZE[0] / 2 - bt_width / 2),
        round(SCREEN_SIZE[1] / 2 - bt_height / 2),
        bt_width,
        bt_height,
    )
    button_color = (205, 136, 75)

    # 创建用户端对象
    client1 = Client("127.0.0.1", 12344, 12344, random.randint(1235, 10000))

    try:
        is_in_room = False
        my_turn = True
        show_start_menu = True
        game_over = False
        doushou = Doushou()
        while True:
            clock.tick(FPS)  # 设置帧率

            if show_start_menu is True:
                # 绘制按钮
                pygame.draw.rect(doushou._chessboard, button_color, button_rect, border_radius=10)
                doushou._chessboard.blit(
                    button_text,
                    (
                        round(SCREEN_SIZE[0] / 2 - button_text.get_width() / 2),
                        round(SCREEN_SIZE[1] / 2 - button_text.get_height() / 2),
                    ),
                )
                screen.blit(doushou._chessboard, (0, 0))

                # 监听事件
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button_rect.collidepoint(event.pos):
                            # 在这里执行点击开始游戏按钮后的操作
                            doushou = Doushou()
                            if is_in_room is False:
                                rooms = client1.get_rooms()
                                if not has_empty_room(rooms):
                                    client1.create_room("XXX's room")
                                else:
                                    for room in rooms:
                                        try:
                                            if room["nb_players"] < room["capacity"]:
                                                client1.join_room(room["id"])
                                                print("加入现有房间成功")
                                                break
                                        except Exception as e:
                                            print(f"加入房间失败，错误信息：", repr(e))
                                            time.sleep(0.5)
                                rooms = client1.get_rooms()
                                for room in rooms:
                                    if room["id"] == client1.room_id:
                                        if room["nb_players"] == 2:
                                            # 后进房，已满员，后手
                                            my_turn = False
                                        else:
                                            while not is_my_room_ready(client1):
                                                time.sleep(0.5)
                                                print("等待对手")
                                            print("对手已到位，开始对局")
                                is_in_room = True

                            show_start_menu = False
                            game_over = False
            else:
                if my_turn is False and game_over is False:
                    # 若不是本人回合,查看对手操作
                    messages = client1.get_messages()
                    if len(messages) != 0:
                        for message in messages:
                            last_message = json.loads(message)
                            sender, message_value = last_message.popitem()
                            doushou.click_at(message_value["i"], message_value["j"])

                            doushou.draw_board()
                            doushou.draw_turn_text(font)
                            doushou.draw_chesses()
                            if message_value["gameover_text"] != "":
                                # 一局游戏结束
                                gameover_text = gameover_font.render(message_value["gameover_text"], True, (255, 0, 0))
                                doushou._chessboard.blit(
                                    gameover_text,
                                    (
                                        round(
                                            SCREEN_SIZE[0] / 2
                                            - gameover_text.get_width() / 2
                                        ),
                                        round(
                                            SCREEN_SIZE[1] / 2
                                            - gameover_text.get_height() / 2
                                            - button_text.get_height()
                                            - 10
                                        ),
                                    ),
                                )
                                button_text = button_font.render("再来一局", True, text_color)
                                show_start_menu = True
                            screen.blit(doushou._chessboard, (0, 0))
                            if message_value["switch"] == "True":
                                my_turn = True
                else:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:  # 按下的是鼠标左键
                                i, j = doushou.get_coord(event.pos)
                                old_turn = doushou.blue_turn
                                doushou.click_at(i, j)
                                val_to_send = {
                                    "i": i,
                                    "j": j,
                                    "switch": "True" if old_turn != doushou.blue_turn else "",
                                    "gameover_text": "",
                                }
                                if doushou.check_over() != GameResult.NOT_OVER:
                                    gameover_text = ""
                                    if doushou.check_over() == GameResult.BLUE_WIN:
                                        gameover_text = "蓝方获胜!"
                                    elif doushou.check_over() == GameResult.RED_WIN:
                                        gameover_text = "红方获胜!"
                                    else:
                                        gameover_text = "平局!"
                                    val_to_send["gameover_text"] = gameover_text
                                    gameover_text = gameover_font.render(gameover_text, True, (255, 0, 0))
                                    game_over = True
                                else:
                                    my_turn = False
                                client1.send(val_to_send)

                        doushou.draw_board()
                        doushou.draw_turn_text(font)
                        doushou.draw_chesses()
                        if game_over is True:
                            # 一局游戏结束
                            doushou._chessboard.blit(
                                gameover_text,
                                (
                                    round(SCREEN_SIZE[0] / 2 - gameover_text.get_width() / 2),
                                    round(SCREEN_SIZE[1] / 2 - gameover_text.get_height() / 2 - button_text.get_height() - 10),
                                ),
                            )
                            button_text = button_font.render("再来一局", True, text_color)
                            show_start_menu = True
                        screen.blit(doushou._chessboard, (0, 0))
            pygame.display.update()
    except:
        client1.leave_room()


main()
