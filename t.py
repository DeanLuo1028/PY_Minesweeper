import pygame

# 初始化
pygame.init()
screen = pygame.display.set_mode((400, 300))
rect = pygame.Rect(150, 100, 100, 50) # 建立矩形物件
color = (0, 128, 255)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 偵測滑鼠點擊
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                color = (255, 0, 0) # 點擊後變紅
                print("矩形被點擊了！")
            else:
                color = (0, 128, 255) # 點擊外變回藍色

    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, color, rect) # 繪製矩形
    pygame.display.flip()

pygame.quit()
