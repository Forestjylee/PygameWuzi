import os
import sys
import json
import time
import loguru
from loguru import logger
import traceback
from enum import Enum
import pygame
import PySimpleGUI as sg
from client import Client
from collections import namedtuple
from collections import deque
import random

SERVER_IP = "192.168.200.114"

GRID_LINE_COLOR = (0, 0, 0)  # 棋盘格子线颜色

FPS = 60
SCREEN_SIZE = 610, 650

CHESS_WIDTH = 100
CHESS_HEIGHT = 100
Position = namedtuple("Position", ["x", "y"])

logger.add("log.txt", rotation="1 MB", retention="10 days")


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

    def __init__(self, seed=None):
        try:
            self.seed = seed if seed is not None else random.randint(0, 1000000)
            self.blue_turn = True
            self.focus_pos_logic = None

            self._init_resources()
            self._init_sprites()

            self.font = pygame.font.SysFont("arial", 16)

            self.points = [[] for i in range(self.lines)]
            self._init_points()

            # 逻辑棋盘，当前棋子的位置
            self._chess_board_logic = []
            self._cover_board_logic = []

            self.draw_board()
        except pygame.error as e:
            print(e)

    def _init_resources(self):
        self.loading_filename = "assets/loading.jpg"
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

        # music
        self._eat_sound = pygame.mixer.Sound("assets/music/eat.mp3")
        self._be_eatten_sound = pygame.mixer.Sound("assets/music/be_eat.mp3")
        self._elephant_sound = pygame.mixer.Sound("assets/music/elephant.mp3")
        self._lion_sound = pygame.mixer.Sound("assets/music/lion.mp3")
        self._tiger_sound = pygame.mixer.Sound("assets/music/tiger.mp3")
        self._leopard_sound = pygame.mixer.Sound("assets/music/leopard.mp3")
        self._wolf_sound = pygame.mixer.Sound("assets/music/wolf.mp3")
        self._dog_sound = pygame.mixer.Sound("assets/music/dog.mp3")
        self._cat_sound = pygame.mixer.Sound("assets/music/cat.mp3")
        self._rat_sound = pygame.mixer.Sound("assets/music/rat.mp3")

    def _init_sprites(self):
        def _rescale_sprite(sprite, width=self.chess_width, height=self.chess_height):
            return pygame.transform.scale(sprite, (width, height))

        self._loading = _rescale_sprite(
            pygame.image.load(self.loading_filename).convert_alpha()
        )
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
        
        self._animal_music_map = {
            self._blue_rat: self._rat_sound,
            self._blue_cat: self._cat_sound,
            self._blue_dog: self._dog_sound,
            self._blue_wolf: self._wolf_sound,
            self._blue_leopard: self._leopard_sound,
            self._blue_tiger: self._tiger_sound,
            self._blue_lion: self._lion_sound,
            self._blue_elephant: self._elephant_sound,
            self._red_rat: self._rat_sound,
            self._red_cat: self._cat_sound,
            self._red_dog: self._dog_sound,
            self._red_wolf: self._wolf_sound,
            self._red_leopard: self._leopard_sound,
            self._red_tiger: self._tiger_sound,
            self._red_lion: self._lion_sound,
            self._red_elephant: self._elephant_sound,
        }

    def _init_points(self):
        for i in range(self.lines):
            for j in range(self.lines):
                self.points[i].append(
                    Position(self.left + i * self.space, self.top + j * self.space)
                )

    def reset_seed(self):
        self.seed = random.randint(0, 1000000)

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
                if self._cover_board_logic[i][j] is True:  # 未翻开
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
                    self._chessboard.blit(self._chess_board_logic[i][j], (pos_x, pos_y))
                elif self._chess_board_logic[i][j] is not None:
                    # 未选中但有棋子
                    self._chessboard.blit(self._chess_board_logic[i][j], (pos_x, pos_y))

    def draw_turn_text(self, font_obj: pygame.font.Font, my_color: str):
        if (my_color == "蓝" and self.blue_turn is True) or (
            my_color == "红" and self.blue_turn is False
        ):
            text = f"您是<{my_color}>方，现在是您的回合"
        else:
            text = f"您是<{my_color}>方，现在是对方的回合"
        turn_text = font_obj.render(text, True, (0, 0, 0))
        self._chessboard.blit(turn_text, (self.left // 3, self.top // 6))

    def init_new_game(self):
        random_animal_positions = [i for i in self.animal_map.keys()]
        random.seed(self.seed)
        random.shuffle(random_animal_positions)
        self._chess_board_logic = [[] for i in range(self.lines)]
        self._cover_board_logic = [[] for i in range(self.lines)]

        self.focus_pos_logic = None
        self.blue_turn = True

        for i in range(self.lines):
            for j in range(self.lines):
                self._chess_board_logic[i].append(
                    random_animal_positions[i * self.lines + j]
                )
                self._cover_board_logic[i].append(True)

    # 点击了棋盘(i,j)位置操作
    def click_at(self, i, j):
        if i == -1 or j == -1:
            return

        # 翻开棋子
        if self._cover_board_logic[i][j] is True:
            self._animal_music_map[self._chess_board_logic[i][j]].play()
            self._cover_board_logic[i][j] = False
            self.blue_turn = not self.blue_turn  # 切换蓝红方顺序
            self.focus_pos_logic = None
            return

        if self.focus_pos_logic is None:
            if (
                self._chess_board_logic[i][j] is not None
                and self.__is_own_chess(self._chess_board_logic[i][j]) is True
            ):
                # 如果之前没有选中，现点击了自己的棋子，则选中自己的棋子
                self.focus_pos_logic = Position(i, j)
        else:  # 如果之前选中了棋子
            if self._chess_board_logic[i][j] is None:  # 选择了空地
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
                    self._chess_board_logic[i][j] = self._chess_board_logic[
                        self.focus_pos_logic.x
                    ][self.focus_pos_logic.y]
                    self._chess_board_logic[self.focus_pos_logic.x][
                        self.focus_pos_logic.y
                    ] = None
                    self.focus_pos_logic = None
                    self.blue_turn = not self.blue_turn  # 切换蓝红方顺序
            else:  # 选择了棋子
                if (
                    self.__is_own_chess(self._chess_board_logic[i][j]) is True
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
                        focus_chess = self._chess_board_logic[self.focus_pos_logic.x][
                            self.focus_pos_logic.y
                        ]
                        compare_res = self.compare_chess(
                            focus_chess, self._chess_board_logic[i][j]
                        )
                        if compare_res == CompareResult.WIN:
                            # 移动并吃掉对方棋子
                            self._animal_music_map[
                                self._chess_board_logic[self.focus_pos_logic.x][
                                    self.focus_pos_logic.y
                                ]
                            ].play()
                            self._chess_board_logic[i][j] = self._chess_board_logic[
                                self.focus_pos_logic.x
                            ][self.focus_pos_logic.y]
                            self._chess_board_logic[self.focus_pos_logic.x][
                                self.focus_pos_logic.y
                            ] = None
                        elif compare_res == CompareResult.EQUAL:
                            # 双方棋子都消失
                            self._animal_music_map[
                                self._chess_board_logic[self.focus_pos_logic.x][
                                    self.focus_pos_logic.y
                                ]
                            ].play()
                            self._chess_board_logic[i][j] = None
                            self._chess_board_logic[self.focus_pos_logic.x][
                                self.focus_pos_logic.y
                            ] = None
                        elif compare_res == CompareResult.LOSE:
                            # 己方棋子消失
                            self._chess_board_logic[self.focus_pos_logic.x][
                                self.focus_pos_logic.y
                            ] = None
                            self._be_eatten_sound.play()
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
        max_blue_chess = -1
        max_red_chess = -1
        for i in range(self.lines):
            for j in range(self.lines):
                if self._chess_board_logic[i][j] is None:
                    continue
                if self.animal_map[self._chess_board_logic[i][j]] < 8:
                    blue_chess_amount += 1
                    max_blue_chess = max(max_blue_chess, self.animal_map[self._chess_board_logic[i][j]])
                else:
                    red_chess_amount += 1
                    max_red_chess = max(max_red_chess, self.animal_map[self._chess_board_logic[i][j]]-8)

        if blue_chess_amount == 0 and red_chess_amount == 0:
            return GameResult.DRAW
        elif blue_chess_amount == 0 and red_chess_amount >= 0:
            return GameResult.RED_WIN
        elif blue_chess_amount >= 0 and red_chess_amount == 0:
            return GameResult.BLUE_WIN
        elif blue_chess_amount == 1 and red_chess_amount == 1:
            if max_blue_chess == max_red_chess:
                return GameResult.DRAW
            elif max_blue_chess > max_red_chess:
                return GameResult.BLUE_WIN
            else:
                return GameResult.RED_WIN
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


def render_screen(doushou: Doushou, turn_font: pygame.font.Font, my_color: str):
    doushou.draw_board()
    doushou.draw_turn_text(turn_font, my_color)
    doushou.draw_chesses()


def main():
    # 创建用户端对象
    server_ip = sg.popup_get_text(
        message="请输入服务器ip", title="", default_text=SERVER_IP
    )
    if server_ip is None:
        os._exit(1)
    client1 = Client(server_ip, 12344, 12344, random.randint(1235, 10000))

    pygame.init()

    # 音乐
    pygame.mixer.init()
    menu_music_filepath = "assets/music/menu.mp3"
    gameing_music_filepath = "assets/music/gameing.mp3"
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.load(menu_music_filepath)
    pygame.mixer.music.play(-1)

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
    bt_width, bt_height = button_text.get_width() + 25, button_text.get_height() + 15
    button_rect = pygame.Rect(
        round(SCREEN_SIZE[0] / 2 - bt_width / 2),
        round(SCREEN_SIZE[1] / 2 - bt_height / 2),
        bt_width,
        bt_height,
    )
    button_color = (205, 136, 75)

    try:
        my_color = ""  # 红或蓝
        is_in_room = False
        my_turn = True
        show_start_menu = True
        game_over = False
        gameover_text = "吃光对面的棋子！"
        doushou = Doushou()
        while True:
            clock.tick(FPS)  # 设置帧率

            if show_start_menu is True:  # 展示菜单
                # 播放音乐

                # 绘制按钮
                pygame.draw.rect(
                    doushou._chessboard, button_color, button_rect, border_radius=10
                )
                gameover_suf = gameover_font.render(gameover_text, True, (255, 0, 0))
                doushou._chessboard.blit(
                    gameover_suf,
                    (
                        round(SCREEN_SIZE[0] / 2 - gameover_suf.get_width() / 2),
                        round(
                            SCREEN_SIZE[1] / 2
                            - gameover_suf.get_height() / 2
                            - button_text.get_height()
                            - 13
                        ),
                    ),
                )
                doushou._chessboard.blit(
                    button_text,
                    (
                        round(SCREEN_SIZE[0] / 2 - button_text.get_width() / 2),
                        round(SCREEN_SIZE[1] / 2 - button_text.get_height() / 2),
                    ),
                )

                # 监听事件
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise Exception
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button_rect.collidepoint(event.pos):
                            # 在这里执行点击开始游戏按钮后的操作
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
                                            # 后进房，已满员
                                            flag = False
                                            while 1:
                                                if flag is True:
                                                    break
                                                messages = client1.get_messages()
                                                for message in messages:
                                                    last_message = json.loads(message)
                                                    sender, message_value = (
                                                        last_message.popitem()
                                                    )
                                                    if (
                                                        message_value.get("seed")
                                                        is not None
                                                    ):
                                                        doushou.seed = message_value[
                                                            "seed"
                                                        ]
                                                        flag = True
                                                        client1.send({"ready": "True"})
                                                        break
                                                for event in pygame.event.get():
                                                    if event.type == pygame.QUIT:
                                                        raise Exception
                                            if doushou.seed >= 500000:
                                                my_color = "蓝"
                                            else:
                                                my_color = "红"
                                        else:
                                            # 先进房
                                            while not is_my_room_ready(client1):
                                                clock.tick(FPS)  # 设置帧率
                                                gameover_suf = gameover_font.render(
                                                    "搜索对手中...", True, (255, 0, 0)
                                                )
                                                doushou.draw_board()
                                                doushou._chessboard.blit(
                                                    gameover_suf,
                                                    (
                                                        round(
                                                            SCREEN_SIZE[0] / 2
                                                            - gameover_suf.get_width()
                                                            / 2
                                                        ),
                                                        round(
                                                            SCREEN_SIZE[1] / 2
                                                            - gameover_suf.get_height()
                                                            / 2
                                                            - button_text.get_height()
                                                            - 13
                                                        ),
                                                    ),
                                                )
                                                for event in pygame.event.get():
                                                    if event.type == pygame.QUIT:
                                                        client1.leave_room()
                                                        pygame.quit()  # 这里只是获取事件但不做任何处理，从而实现清空缓冲区的效果
                                                screen.blit(doushou._chessboard, (0, 0))
                                                pygame.display.update()
                                            print("对手已到位，开始对局")
                                            client1.send({"seed": doushou.seed})
                                            flag = False
                                            while 1:
                                                if flag is True:
                                                    break
                                                messages = client1.get_messages()
                                                for message in messages:
                                                    last_message = json.loads(message)
                                                    sender, message_value = (
                                                        last_message.popitem()
                                                    )
                                                    if (
                                                        message_value.get("ready")
                                                        is not None
                                                    ):
                                                        flag = True
                                                        break
                                                    for event in pygame.event.get():
                                                        if event.type == pygame.QUIT:
                                                            raise Exception
                                            if doushou.seed >= 500000:
                                                my_color = "红"
                                            else:
                                                my_color = "蓝"
                                is_in_room = True
                            else:
                                # 已在房间内，再来一局逻辑
                                if my_color == "蓝":
                                    doushou.reset_seed()
                                    client1.send({"seed": doushou.seed})
                                    flag = False
                                    while 1:
                                        if flag is True:
                                            break
                                        messages = client1.get_messages()
                                        for message in messages:
                                            last_message = json.loads(message)
                                            sender, message_value = (
                                                last_message.popitem()
                                            )
                                            if message_value.get("ready") is not None:
                                                flag = True
                                                break
                                        for event in pygame.event.get():
                                            if event.type == pygame.QUIT:
                                                raise Exception
                                    if doushou.seed >= 500000:
                                        my_color = "红"
                                else:
                                    flag = False
                                    while 1:
                                        if flag is True:
                                            break
                                        messages = client1.get_messages()
                                        for message in messages:
                                            last_message = json.loads(message)
                                            sender, message_value = (
                                                last_message.popitem()
                                            )
                                            if message_value.get("seed") is not None:
                                                doushou.seed = message_value["seed"]
                                                flag = True
                                                client1.send({"ready": "True"})
                                                break
                                        for event in pygame.event.get():
                                            if event.type == pygame.QUIT:
                                                raise Exception
                                    if doushou.seed >= 500000:
                                        my_color = "蓝"
                            if my_color == "蓝":
                                my_turn = True
                            else:
                                my_turn = False
                            doushou.init_new_game()
                            render_screen(doushou, font, my_color)
                            show_start_menu = False
                            game_over = False
                            # 播放游戏音乐
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(gameing_music_filepath)
                            pygame.mixer.music.play(-1)
            else:  # 展示游戏页
                if my_turn is False and game_over is False:
                    # 若不是本人回合,查看对手操作
                    messages = client1.get_messages()
                    for message in messages:
                        last_message = json.loads(message)
                        sender, message_value = last_message.popitem()
                        i, j, old_focus_i, old_focus_j = (
                            message_value["i"],
                            message_value["j"],
                            message_value["old_focus_i"],
                            message_value["old_focus_j"],
                        )
                        # 模拟对手下棋，避免网络消息乱序导致程序错乱
                        if doushou._cover_board_logic[i][j] is True:
                            doushou.click_at(i, j)
                            logger.info(f"对方点击: {i}, {j}")
                        else:
                            # 模拟对手点击两次的效果
                            doushou.click_at(old_focus_i, old_focus_j)
                            render_screen(doushou, font, my_color)
                            screen.blit(doushou._chessboard, (0, 0))
                            pygame.display.update()
                            time.sleep(0.7)
                            doushou.click_at(i, j)
                            logger.info(f"对方点击: {old_focus_i}, {old_focus_j}")
                            logger.info(f"对方点击: {i}, {j}")
                        my_turn = True
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            raise Exception
                elif my_turn is True and game_over is False:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            raise Exception
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:  # 按下的是鼠标左键
                                i, j = doushou.get_coord(event.pos)
                                old_turn = doushou.blue_turn
                                old_focus_pos = doushou.focus_pos_logic
                                doushou.click_at(i, j)
                                logger.info(
                                    f"本人点击: {i}, {j} | old_turn: {old_turn}, new_turn: {doushou.blue_turn}"
                                )
                                if old_turn != doushou.blue_turn:
                                    # 出现控制权翻转才发送消息
                                    my_turn = False
                                    val_to_send = {
                                        "i": i,
                                        "j": j,
                                        "old_focus_i": (
                                            old_focus_pos.x
                                            if old_focus_pos is not None
                                            else ""
                                        ),
                                        "old_focus_j": (
                                            old_focus_pos.y
                                            if old_focus_pos is not None
                                            else ""
                                        ),
                                        "gameover_text": "",
                                    }
                                    client1.send(val_to_send)
                                    break
                if is_my_room_ready(client1) is False:
                    # 对方退出，重新进入菜单页
                    client1.leave_room()
                    is_in_room = False
                    show_start_menu = True
                render_screen(doushou, font, my_color)
                if doushou.check_over() != GameResult.NOT_OVER or game_over is True:
                    gameover_text = ""
                    if doushou.check_over() == GameResult.BLUE_WIN:
                        if my_color == "蓝":
                            gameover_text = "耶！你赢了！"
                        else:
                            gameover_text = "哎呀！就差一点了！"
                    elif doushou.check_over() == GameResult.RED_WIN:
                        if my_color == "红":
                            gameover_text = "耶！你赢了！"
                        else:
                            gameover_text = "哎呀！就差一点了！"
                    else:
                        gameover_text = "平局!"
                    gameover_suf = gameover_font.render(
                        gameover_text, True, (255, 0, 0)
                    )
                    # 一局游戏结束
                    doushou._chessboard.blit(
                        gameover_suf,
                        (
                            round(SCREEN_SIZE[0] / 2 - gameover_suf.get_width() / 2),
                            round(
                                SCREEN_SIZE[1] / 2
                                - gameover_suf.get_height() / 2
                                - button_text.get_height()
                                - 13
                            ),
                        ),
                    )
                    button_text = button_font.render("再来一局", True, text_color)
                    game_over = True
                    show_start_menu = True
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(menu_music_filepath)
                    pygame.mixer.music.play(-1)
            screen.blit(doushou._chessboard, (0, 0))
            pygame.display.update()
    except Exception as e:
        traceback.print_exc()
    finally:
        try:
            client1.leave_room()
        except:
            pass
        pygame.quit()
        os._exit(1)


main()
