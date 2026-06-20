import pygame

clock = pygame.time.Clock()

   
pygame.init()
screen = pygame.display.set_mode((956, 716))
pygame.display.set_caption("Acoustic_Heist")
icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)

# myfont = pygame.font.Font('fonts/AlienBlock-Regular.ttf', 40)
# text_surface = myfont.render('heist', False, 'White')

bg = pygame.image.load('images/bg1.png')
player = pygame.image.load('images/pl.png')
player = pygame.transform.smoothscale(player, (64, 64))


bg_width = bg.get_width()
bg_x = 0

bg_sound = pygame.mixer.Sound('sounds/bg.mp3')
bg_sound.play()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x + bg_width, 0)) 
    screen.blit(player, (300, 250))

    bg_x -= 5
    if bg_x <= -956:
        bg_x = 0

    pygame.display.update()

    clock.tick(60)
