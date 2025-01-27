import os
import random
import math
import pygame
import neat
from os import listdir
from os.path import isfile, join
import pickle

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
        self.state = [self.rect.x, self.rect.y, self.x_vel, self.y_vel, 0, 0] # dans l'ordre on a (0)pos_x, (1)pos_y, (2)x_vel, (3)y_vel, (4)dist_to_start, (5)is_hit
        self.apple_count = 0
        self.sprite = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.lv_count = 0
        self.block_pos = None
        
    def get_dist(self):
        dist_to_start = math.floor(((130 - self.rect.x)**2 + (740 - self.rect.y)**2)**0.5)
        return dist_to_start

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

    def loop(self, fps, offset_x, offset_y):
        self.y_vel += min(1, (self.fall_count/fps)*self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        if self.y_vel > 80:
            self.rect.y = 0
            self.y_vel = 0
            offset_y = 0
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 1.2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()
        if self.hit:
            self.state = [self.rect.x, self.rect.y, math.floor(self.x_vel), math.floor(self.y_vel), self.get_dist(), 1]
        else:
            self.state = [self.rect.x, self.rect.y, math.floor(self.x_vel), math.floor(self.y_vel), self.get_dist(), 0]
        # print("player state", self.state)
        return offset_x, offset_y

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
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

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        # print(self.image)
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

    def loop(self):
        pass

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
    
class Apple(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Apple")
        self.apple = load_sprite_sheets("Items", "Fruits", width, height)
        self.image = self.apple["Apple"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0

    def loop(self):
        sprites = self.apple
        sprite_index = (self.animation_count//self.ANIMATION_DELAY)%len(sprites)

        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count//self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class End(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "End")
        self.end = load_sprite_sheets("Items", "Checkpoints", width, height)
        self.image = self.end["Checkpoint (Flag Idle)(64x64)"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0

    def loop(self):
        sprites = self.end
        sprite_index = (self.animation_count//self.ANIMATION_DELAY)%len(sprites)

        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count//self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class TopBar():
    def __init__(self, width, height):
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

    def draw(self, window):
        window.blit(self.image, self.rect)

class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.stat = []
        self.obstacle_pos = []
        pygame.display.set_caption("Platformer")

    def get_background(self, name="Blue.png"):
        image = pygame.image.load(join("assets", "Background", name))
        __, __, width, height = image.get_rect()
        tiles = []

        for i in range(WIDTH // width + 1):
            for j in range(HEIGHT // height + 1):
                pos = [i * width, j * height]
                tiles.append(pos)

        return tiles, image

    def draw(self, window, background, bg_image, player, objects, offset_x, offset_y):
        for tile in background:
            window.blit(bg_image, tuple(tile))

        for obj in objects:
            obj.draw(window, offset_x, offset_y)

        player.draw(window, offset_x, offset_y)
        pygame.display.update()

    def handle_vertical_collision(self, player, objects, dy):
        collided_objects = []

        player.move(0, dy)
        player.update()
        for obj in objects:
            if pygame.sprite.collide_mask(player, obj) and obj.name == "Apple":
                collided_objects.append(obj)
                break
        player.move(0, -dy)
        player.update()

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

    def collide(self, player, objects, dx):
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

    def handle_move(self, player, objects, outputs = None):
        keys = pygame.key.get_pressed()

        player.x_vel = 0
        collide_left = self.collide(player, objects, -PLAYER_VEL * 2.2)
        collide_right = self.collide(player, objects, PLAYER_VEL * 2.2)

        if (keys[pygame.K_LEFT] and not collide_left) or outputs == 0:
            player.move_left(PLAYER_VEL)
        if (keys[pygame.K_RIGHT] and not collide_right) or outputs == 1:
            player.move_right(PLAYER_VEL)

        vertical_collide = self.handle_vertical_collision(player, objects, player.y_vel)
        to_check = [collide_left, collide_right, *vertical_collide]
        for obj in to_check:
            if obj and obj.name == "Apple":
                player.apple_count += 1
                objects.remove(obj)
                break
            if obj and obj.name == "Fire":
                player.make_hit()
            if obj and obj.name == "End":
                objects = self.place_block_at_random(player.rect.x, player.rect.y)
                player.lv_count += 1
        return objects

    def collide_block(self, objects, block):
        is_in_collision = False
        for obj in objects:
            if pygame.sprite.collide_mask(obj, block):
                is_in_collision = True
                break
        
        return is_in_collision

    def get_block_coord_at_random(self, x_start, y_start):
        pi_val  =[0, 1/6, 1/4, 1/3, 1/2, 2/3, 3/4, 5/4, 7/4, 5/4, 11/6]
        pi = 3.141592
        t = pi_val[random.randrange(0, len(pi_val))]
        new_coord = [math.ceil(x_start + 220*math.sin(t*pi)), math.ceil(y_start + 60*math.cos(t*pi))]
        return new_coord
        
    def place_block_at_random(self, x_start, y_start):
        block_size = 96
        next_point = [x_start, y_start]
        objects = []
        i = 0
        while i < 50:
            if not self.collide_block(objects, Block(next_point[0], next_point[1], block_size)):
                objects.append(Block(next_point[0], next_point[1], block_size))
                if random.randrange(0, 500) < 251 and i != 49:
                    if not self.collide_block(objects, Apple(next_point[0] + 20, next_point[1] - 56 , 32, 32)):
                        objects.append(Apple(next_point[0] + 20, next_point[1] - 56 , 32, 32))
                if i == 49:
                    if not self.collide_block(objects, End(next_point[0], next_point[1]-130, 64, 64)):
                        objects.append(End(next_point[0]+20, next_point[1]-128, 64, 64))
                    else: 
                        i -= 1
                next_point = self.get_block_coord_at_random(next_point[0], next_point[1])
                if next_point[1] > 700:
                    next_point = self.get_block_coord_at_random(next_point[0], next_point[1])
            else:
                next_point = self.get_block_coord_at_random(next_point[0], next_point[1])
                i -= 1
                print(i)
            i += 1

        return objects

    def load_lv1(self, player):
        block_size = 96
        block_pos = []
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

        fire_block = [
                      Fire(65, HEIGHT - block_size - 64, 16, 32), Fire(0, HEIGHT - block_size - 64, 16, 32),
                      Fire(65*10, HEIGHT - block_size - 64, 16, 32), Fire(65*9, HEIGHT - block_size - 64, 16, 32),
                      Fire(65*12, HEIGHT - block_size - 64, 16, 32), Fire(65*11, HEIGHT - block_size - 64, 16, 32),
                      Fire(65*11, HEIGHT - block_size*5 - 64, 16, 32), Fire(65*10, HEIGHT - block_size*5 - 64, 16, 32),
                      Fire(65*20, HEIGHT - block_size - 64, 16, 32), Fire(65*19, HEIGHT - block_size - 64, 16, 32),
                      Fire(65*31, HEIGHT - block_size - 64, 16, 32), Fire(65*30, HEIGHT - block_size - 64, 16, 32)
                     ]

        apples = [ 
                   Apple(210, 740, 32, 32),
                   Apple(0, 356, 32, 32),
                   Apple(310, 164, 32, 32),
                   Apple(575, 356, 32, 32),
                   Apple(975, 548, 32, 32),
                   Apple(1350, 740, 32, 32),
                   Apple(1545, 548, 32, 32),
                   Apple(1840, 356, 32, 32),
                   Apple(1840, 740, 32, 32),
                   Apple(2120, 548, 32, 32),
                   Apple(1835, 68, 32, 32),
                 ]
        
        for fire in fire_block:
            fire.on()
            fire.loop()
        level_1 = [
                   *floor_1, *floor_2, *floor_3, *floor_4, 
                   *air_block_1, *air_block_2, *air_block_3, *air_block_4, *air_block_5, *air_block_6, *air_block_7, *air_block_8, *air_block_9, *air_block_10, 
                   *fire_block,
                   *apples,
                   End(2130, 196, 64, 64)
                   ]
        objects = level_1
        for block in objects:
            block_pos.append(block.rect.x)
            block_pos.append(block.rect.y)
        player.block_pos = block_pos
        return objects

    def get_pos_obstacle(self, objects):
        obstacles_pos = []
        for obj in objects:
            obstacles_pos.append((obj.rect.x, obj.rect.y))
        
        return obstacles_pos

    def main(self):
        clock = pygame.time.Clock()
        background, bg_image = self.get_background("Blue.png")

        player = Player(130, 740, 50, 50)
        # objects = [*self.place_block_at_random(120, 800)]
        objects = [*self.load_lv1(player)]
        self.obstacle_pos = self.get_pos_obstacle(objects)


        offset_x = 0
        offset_y = 0
        scroll_area_width = 400

        topbar = TopBar(100, 20)

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
                    if event.key == pygame.K_a:
                        player = Player(130, 740, 50, 50)
                        objects = objects = [*self.load_lv1()]
                        offset_x = 0
                        offset_y = 0

            offset_x, offset_y = player.loop(FPS, offset_x, offset_y)
            self.stat = [*player.state, *self.obstacle_pos]
            # print(self.stat)
            objects = self.handle_move(player, objects)
            self.draw(self.window, background, bg_image, player, objects, offset_x, offset_y)

            if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0):
                offset_x += player.x_vel
            if (player.rect.y - offset_y >= HEIGHT - scroll_area_width and player.y_vel > 0) or (player.rect.y - offset_y <= scroll_area_width and player.y_vel < 0):
                offset_y += player.y_vel
            

        pygame.quit()
        quit()

# Run the game
# Game().main()

#=======================================================                =================================================               =================================
#=======================================================                =================================================               =================================
# Above this Line is the game made for being played by a human.
# Everyting Below would be expected to be played by an IA and/or is defining that said IA and training method
#=======================================================                =================================================               =================================
#=======================================================                =================================================               =================================

# config_path = "config-neat.txt"  # Nom exact de ton fichier

def eval_genom(genome, config):
    # charger la config reseau
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    # Initialser le jeu
    game = Game()
    background, bg_image = game.get_background("Blue.png")
    player = Player(130, 740, 50, 50)
    objects = game.load_lv1(player)

    clock = pygame.time.Clock()
    offset_x, offset_y = 0, 0
    fitness = 0
    scroll_area_width = 400
    lv_count = 0
    apple_count = 0

    run = True
    time_elapsed = 0
    time_limit = 10*1000

    while run:
        delta_time = clock.tick(FPS)
        time_elapsed += delta_time
        if time_elapsed >= time_limit:
            run = False
            break
        # Simuler les entrées réseaux
        inputs = [
            *player.state,
            *player.block_pos
        ]
        # Obtenir les sorties réseaux
        outputs = net.activate(inputs)
        output = None
        # Mapper les sorties à des actions
        if outputs[0] > 0.2:
            player.move_left
            output = 0
        if outputs[1] > 0.2:
            player.move_right
            output = 1
        if outputs[2] > 0.2 and player.jump_count < 2:
            player.jump()
        # Gerer les collisions et mise a jour
        objects = game.handle_move(player, objects, output)
        offset_x, offset_y = player.loop(FPS, offset_x, offset_y)
        # Calculer la fitness
        if player.apple_count > apple_count:
            fitness += 1
            apple_count += 1
        if player.apple_count == 0:
            fitness -= 0.2
        if player.hit:
            fitness -= 2
        if player.lv_count > lv_count:
            lv_count += 1
            fitness += 10
        game.draw(game.window, background, bg_image, player, objects, offset_x, offset_y)
        # Arreter le jeu si le joueur est bloqué
        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0):
            offset_x += player.x_vel
        if (player.rect.y - offset_y >= HEIGHT - scroll_area_width and player.y_vel > 0) or (player.rect.y - offset_y <= scroll_area_width and player.y_vel < 0):
            offset_y += player.y_vel
        if player.rect.y > HEIGHT:
            fitness -= 10
            run = False
    return fitness

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genom(genome, config)

def run_neat():
    # Charger la configuration
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        "config-neat.txt"
    )
    # Initialiser la population
    p = neat.Population(config)
    # Ajouter des reporters ( pour observer les statistiques d'entrainement )
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # Lancer l'entrainement
    winner = p.run(eval_genomes, 50)
    # Sauvegarder le reseau gagnant
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    run_neat()

def test_winner():
    # Charger le reseau gagnant
    with open("winner.pkl", "rb") as f:
        winner = pickle.load(f)

    config = neat.config.Config(
        neat.DefaultGenome, 
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        "config-neat.txt"
    )
    net = neat.nn.FeedForwardNetwork.create(winner, config)
    # Tester le reseau sur le jeu
    eval_genom(winner, config)

# if __name__ == "__main__":
#     test_winner()