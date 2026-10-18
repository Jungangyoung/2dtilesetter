import os
import pygame
import button
import csv
import pickle

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#pygame window
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
LOWER_MARGIN = 100
SIDE_MARGIN = 300


screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

#define game variables
ROWS = 12
MAX_COLS = 520
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 2
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

#load images
candle1 = pygame.image.load('resources/sprites/static_sprites/candlesbra.png').convert_alpha()
candle2 = pygame.image.load('resources/sprites/animated_sprites/green_light/S1.png').convert_alpha()
sky = pygame.image.load('resources/Textures/sky.png').convert_alpha()
mushroom = pygame.image.load('resources/sprites/npc/soldier/0.png').convert_alpha()
#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'resources/tiles/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

save_img = pygame.image.load('resources/ui/save.png').convert_alpha()
load_img = pygame.image.load('resources/ui/load.png').convert_alpha()


#define colours
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

#define font
font = pygame.font.SysFont('Futura', 30)

#create empty tile list
def create_empty_world():
    return [[-1 for _ in range(MAX_COLS)] for _ in range(ROWS)]
world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

##create ground
#for tile in range(0, MAX_COLS):
#   world_data[ROWS - 1][tile] = 0

#function for outputing the text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


#create function for drawing background
def draw_bg():
    screen.fill(GREEN)
    width = sky.get_width()
    for x in range(200):
        screen.blit(sky, ((x * width) - scroll * 0.5, -280))
        screen.blit(sky, ((x * width) -scroll * 0.6, SCREEN_HEIGHT - mushroom.get_height() - 144))

#draw grid
def draw_grid():
    #vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    #hrizontal lines
    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))

#function for drawing world tiles
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))




#create buttons
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 65, save_img, 1.5)
load_button = button.Button(SCREEN_WIDTH // 2 + 170, SCREEN_HEIGHT + LOWER_MARGIN - 65, load_img, 1.5)
#make a button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

run = True
while run:

    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()

    draw_text(f'level {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('UP/DOWN: change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

    #save and load data
    if save_button.draw(screen):
        #save level data
        pickle_out = open(f'level{level}_data', 'wb')
        pickle.dump(world_data, pickle_out)
        pickle_out.close()
        print(f"{f'level{level}_data'} saved!")
        #with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
        #   writer = csv.writer(csvfile, delimiter = ',')
        #   for row in world_data:
        #       writer.writerow(row)

    if load_button.draw(screen):
        scroll = 0
        #filename = f'level{level}_data'
        if os.path.exists(f'level{level}_data'):
            with open(f'level{level}_data', 'rb') as pickle_in:
                loaded_data = pickle.load(pickle_in)

            # Check dimensions before accepting the saved map
            if (len(loaded_data) == ROWS and
                all(len(row) == MAX_COLS for row in loaded_data)):
                world_data = loaded_data
            else:
                print("Saved map has incorrect dimensions!")
                world_data = create_empty_world()
        else:
            print(f"Level file not found: {f'level{level}_data'}")
            
        #with open(f'level{level}_data.csv', newline='') as csvfile:
        #   reader = csv.reader(csvfile, delimiter = ',')
        #   for x, row in enumerate(reader):
        #       for y, tile in enumerate(row):
        #           world_data[x][y] = int(tile)
                

    #draw tile panels and tiles
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    #choose a file
    button_count = 0
    for button_count,i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count

    #highlight the selected tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

    #scroll_the_map
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed

    #add new tiles to screen
    #get mouse position
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    #check that the coordinates are in bounds
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        if 0 <= y < len(world_data) and 0 <= x < len(world_data[y]):
        #update tile value
            if pygame.mouse.get_pressed()[0] == 1:
                if world_data[y][x] != current_tile:
                    world_data[y][x] = current_tile
            if pygame.mouse.get_pressed()[2] == 1:           
                world_data[y][x] = -1  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame. KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
                scroll = 0
                world_data = create_empty_world()
                if os.path.exists(f'level{level}_data'):
                    pickle_in = open(f'level{level}_data', 'rb')
                    world_data = pickle.load(pickle_in)
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
                scroll = 0
                world_data = create_empty_world()
                if os.path.exists(f'level{level}_data'):
                    pickle_in = open(f'level{level}_data', 'rb')
                    world_data = pickle.load(pickle_in)
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5

        if event.type == pygame. KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1



    pygame.display.update()


pygame.quit()













