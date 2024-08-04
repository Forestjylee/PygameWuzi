import pygame

# 初始化 Pygame
pygame.init()

# 屏幕大小
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 加载背景图片
background_image = pygame.image.load("assets/bg.png")

# 加载要显示/隐藏的图片
image_to_show = pygame.image.load("assets/red_rat.png")

# 图片的初始状态（是否显示）
image_visible = False

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 获取鼠标点击位置
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # 如果点击在背景图片范围内
            if 0 <= mouse_x < SCREEN_WIDTH and 0 <= mouse_y < SCREEN_HEIGHT:
                # 切换图片的显示状态
                image_visible = not image_visible

    # 绘制背景图片
    screen.blit(background_image, (0, 0))

    # 根据状态绘制或不绘制图片
    if image_visible:
        screen.blit(image_to_show, (100, 100))  # 假设图片显示在 (100, 100) 位置

    pygame.display.flip()

# 退出 Pygame
pygame.quit()
