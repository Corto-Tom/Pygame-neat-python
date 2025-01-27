import os
import random
import math
import pygame
import neat
from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_caption("Platformer")

BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 900
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("./assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f ))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i*width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0 
        self.loading = True

    def jump(self):
        self.y_vel = -self.GRAVITY*8
        self.animation_count = 0
        self.jump_count += 1 
        if self.jump_count == 1:
            self.fall_count = 0
           

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0


    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count/fps)*self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        # print(self.rect.x, self.rect.y)
        if self.rect.y > 1000:
            self.rect.y = 00
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 1.2:
            self.hit = False
            self.hit_count = 0


        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0


    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        # if self.loading:  
        #     SPIRITE = load_sprite_sheets("MainCharacters", "Loading", 96, 64, True)
        #     sprite_sheet = "Appearing_right" if self.direction == "right" else "Appearing_left"
        
        #     if sprite_sheet in SPIRITE: 
        #         sprites = SPIRITE[sprite_sheet]
        #         sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        #         self.sprite = sprites[sprite_index]
        #         self.animation_count += 1
        #         print("len(sprites)", len(sprites))
        #         print("self.animation_count", self.animation_count)
        #         print("self.ANIMATION_DELAY", self.ANIMATION_DELAY)
        #         print("sprite_index", sprite_index)
        #         if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
        #             self.loading = False
        #             self.animation_count = 0 
        #     return

        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"

        if self.y_vel < 0:
            if self.jump_count ==1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY*2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite )

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count//self.ANIMATION_DELAY)%len(sprites)

        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image )

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    __, __, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT//height +1):
            pos = [i*width, j*height]
            tiles.append(pos)
    
    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tuple(tile))
    
    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2.2)
    collide_right = collide(player, objects, PLAYER_VEL * 2.2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "Fire":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")


    block_size = 96

    player = Player(130, 740, 50, 50)
    # fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    # fire.on()
    # floor = [Block(i*block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH*2//block_size)]
    # objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), Block(block_size * 3, HEIGHT - block_size * 3, block_size), fire]
    



    floor_1 = [Block(i*block_size, HEIGHT - block_size, block_size)for i in range(0, 3)]
    floor_2 = [Block(i*block_size, HEIGHT - block_size, block_size)for i in range(4, 10)]
    floor_3 = [Block(i*block_size, HEIGHT - block_size, block_size)for i in range(12, 15)]
    floor_4 = [Block(i*block_size, HEIGHT - block_size, block_size)for i in range(19, 22)]

    air_block_1 = [Block(i*block_size, HEIGHT - block_size*5, block_size) for i in range(6,8)]
    air_block_2 = [Block(10*block_size, HEIGHT - block_size*3, block_size)]
    air_block_3 = [Block(0, HEIGHT - block_size*5, block_size)]
    air_block_4 = [Block(3*block_size, HEIGHT - block_size*3, block_size)]
    air_block_5 = [Block(16*block_size, HEIGHT - block_size*3, block_size)]
    air_block_6 = [Block(3*block_size, HEIGHT - block_size*7, block_size)]
    air_block_7 = [Block(22*block_size, HEIGHT - block_size*3, block_size)]
    air_block_8 = [Block(19*block_size, HEIGHT - block_size*5, block_size)]
    air_block_9 = [Block(22*block_size, HEIGHT - block_size*6, block_size)]
    air_block_10 = [Block(19*block_size, HEIGHT - block_size*8, block_size)]

    fire_block = [Fire(65, HEIGHT - block_size - 64, 16, 32), Fire(0, HEIGHT - block_size - 64, 16, 32),
                  Fire(65*10, HEIGHT - block_size - 64, 16, 32), Fire(65*9, HEIGHT - block_size - 64, 16, 32),
                  Fire(65*12, HEIGHT - block_size - 64, 16, 32), Fire(65*11, HEIGHT - block_size - 64, 16, 32),
                  Fire(65*11, HEIGHT - block_size*5 - 64, 16, 32), Fire(65*10, HEIGHT - block_size*5 - 64, 16, 32),
                  Fire(65*20, HEIGHT - block_size - 64, 16, 32), Fire(65*19, HEIGHT - block_size - 64, 16, 32),
                  Fire(65*31, HEIGHT - block_size - 64, 16, 32), Fire(65*30, HEIGHT - block_size - 64, 16, 32)]

    for fire in fire_block:
        fire.on()

    level_1 = [*floor_1, *floor_2, *floor_3, *floor_4, 
               *air_block_1, *air_block_2, *air_block_3, *air_block_4, *air_block_5, *air_block_6, *air_block_7, *air_block_8, *air_block_9, *air_block_10, 
               *fire_block]
    objects = level_1

    offset_x = 0
    scroll_area_width = 400

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        for fire in fire_block:
            fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()

# if __name__ == "__main__":
#     main(window)    

#=======================================================                =================================================               =================================
#=======================================================                =================================================               =================================
# Above this Line is the game made for being played by a human.
# Everyting Below would be expected to be played by an IA and/or is defining that said IA and training method
#=======================================================                =================================================               =================================
#=======================================================                =================================================               =================================

config_path = "config-neat.txt"  # Nom exact de ton fichier

class Player:
    def __init__(self):
        self.position = (0, 0)

# Exemple de classe pour l'environnement
class GameEnvironment:
    def __init__(self, player, objects, background, bg_image):
        self.player = player
        self.objects = objects
        self.background = background
        self.bg_image = bg_image

    def reset(self):
        # Réinitialise l'état du jeu
        self.player.position = (0, 0)

    def get_state(self):
        # Retourne l'état actuel du jeu (sous forme de dictionnaire)
        return {
            "player_x": self.player.position[0],
            "player_y": self.player.position[1],
            "health": self.player.health
        }

    def step(self, action):
        # Met à jour l'environnement en fonction de l'action de l'IA
        reward = 1  # Exemple de récompense
        done = False  # Exemple : si le jeu est fini
        next_state = self.get_state()
        return next_state, reward, done

    def render(self):
        # Affiche le jeu (si nécessaire)
        pass

# Initialisation des objets nécessaires
player = Player()
objects = []
background = "blue"
bg_image = None

# Fonction d'évaluation corrigée
def eval_genomes(genomes, config):
    for _, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        environment = GameEnvironment(player, objects, background, bg_image)

        # Réinitialiser l'environnement et le jeu
        environment.reset()

        # Exécuter le jeu pendant un certain temps et calculer l'aptitude
        for _ in range(1000):
            state = environment.get_state()
            action = net.activate(state.values())  # L'IA prend une décision
            next_state, reward, done = environment.step(action)

            genome.fitness += reward  # Ajouter la récompense à l'aptitude

            if done:
                break

        environment.render()

def run():
    # Chargement de la configuration NEAT
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path  # Utilisation de ton fichier config
    )
    # Création de la population
    population = neat.Population(config)

    # Ajout d'un reporter pour suivre la progression
    population.add_reporter(neat.reporting.StdOutReporter(True))
    population.add_reporter(neat.Checkpointer(5))  # Sauvegarde toutes les 5 générations

    # Lancer l'évolution
    winner = population.run(eval_genomes, 50)  # 50 générations

if __name__ == "__main__":
    run()