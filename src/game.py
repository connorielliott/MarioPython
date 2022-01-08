import random

import pygame
import time

from pygame.locals import *
from time import sleep


class Sprite:
    def __init__(self, x, y, w, h, image):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image = pygame.image.load(image)
        self.flip = False
        self.gravity = 3

    def update(self):
        return True

    def checkCollision(self, s):
        if self.y + self.h <= s.y:
            return False
        if self.y >= s.y + s.h:
            return False
        if self.x + self.w <= s.x:
            return False
        if self.x >= s.x + s.w:
            return False
        return True

    def isBrick(self):
        return False

    def isCoinBrick(self):
        return False

    def isMario(self):
        return False


class Mario(Sprite):
    def __init__(self):
        super().__init__(150, 0, 50, 80, "mario1.png")
        self.framesInAir = 11
        self.vertVel = 0
        self.px = 150
        self.py = 0
        self.imageNum = 0
        self.images = []
        for i in range(1, 6):
            self.images.append(pygame.image.load("mario" + str(i) + ".png"))

    def update(self):
        self.vertVel += self.gravity
        self.y += self.vertVel
        self.framesInAir += 1

        # Mario lands on ground
        if self.y > 450 - self.h:
            self.y = 450 - self.h
            self.framesInAir = 0
            self.vertVel = 0
        return True

    def move(self, forward):
        self.imageNum += 1
        if self.imageNum > 4:
            self.imageNum = 0
        self.image = self.images[self.imageNum]
        if forward:
            self.x += 8.5
            self.flip = False
        if not forward:
            self.x -= 8.5
            self.flip = True

    def jump(self):
        if self.framesInAir < 10:
            self.vertVel -= 5.5

    def setPreviousPos(self):
        self.px = self.x
        self.py = self.y

    def fixPosition(self, s):
        # Top of sprite collision
        if self.py + self.h <= s.y <= self.y + self.h:
            self.vertVel = 0
            self.framesInAir = 0
            self.y = s.y - self.h
            return "top"

        # Bottom of sprite collision
        elif self.py >= s.y + s.h >= self.y:
            self.vertVel = 0
            self.y = s.y + s.h
            self.framesInAir = 11
            return "bottom"

        # Left side of sprite collision
        elif self.px + self.w <= s.x <= self.x + self.w:
            self.x = s.x - self.w
            return "left"

        # Right side of sprite collision
        elif self.px >= s.x + s.w >= self.x:
            self.x = s.x + s.w
            return "right"

    def isMario(self):
        return True


class Brick(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 43, 43, "brick.png")

    def isBrick(self):
        return True


class CoinBrick(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 43, 43, "coinbrick.png")
        self.maxHits = 5
        self.hits = 0

    def isCoinBrick(self):
        self.hits += 1
        if self.maxHits == self.hits:
            self.image = pygame.image.load("emptycoinbrick.png")
        return self.maxHits >= self.hits

    def isBrick(self):
        return True


class Coin(Sprite):
    def __init__(self, x, y, model):
        super().__init__(x, y, 43, 43, "coin.png")
        self.vertVel = -10
        self.horizVel = random.randrange(-20, 20) + 0.3
        self.model = model

    def update(self):
        # Move coin
        self.y += self.vertVel
        self.x += self.horizVel
        self.vertVel += self.gravity

        # Returns false if coin falls off-screen
        return self.y < 500 and self.model.mario.x - self.model.cameraPos < self.x < 1000 + self.model.mario.x - self.model.cameraPos


class Model:
    def __init__(self):
        self.groundPos = 450
        self.cameraPos = 150
        self.mario = Mario()
        self.sprites = []
        self.sprites.append(self.mario)
        self.sprites.append(Brick(800, 400))
        self.sprites.append(Brick(400, 277))
        self.sprites.append(Brick(443, 277))
        self.sprites.append(Brick(486, 277))
        self.sprites.append(Brick(529, 277))
        self.sprites.append(Brick(572, 277))
        self.sprites.append(CoinBrick(486, 104))

    def update(self):
        keep = []
        for s in self.sprites:
            if s.update():
                keep.append(s)
        self.sprites = keep

        for s in self.sprites:
            if s.isBrick() and self.mario.checkCollision(s):
                if self.mario.fixPosition(s) == "bottom" and s.isCoinBrick():
                    self.sprites.append(Coin(s.x, s.y - 43, self))


class View:
    def __init__(self, model):
        screen_size = (1000, 500)
        self.screen = pygame.display.set_mode(screen_size, 32)
        self.model = model
        self.background = pygame.image.load("background.jpg")
        self.ground = pygame.image.load("ground.png")

    def update(self):
        self.screen.fill([0, 200, 100])
        self.screen.blit(self.background, (-self.model.mario.x * 0.4 - 100, 0))
        self.screen.blit(self.ground, (-self.model.mario.x, self.model.groundPos))
        for sprite in self.model.sprites:
            if not sprite.flip:
                self.screen.blit(sprite.image, (sprite.x - self.model.mario.x + self.model.cameraPos, sprite.y))
            else:
                self.screen.blit(pygame.transform.flip(sprite.image, True, False), (sprite.x - self.model.mario.x + self.model.cameraPos, sprite.y))

        pygame.display.flip()


class Controller:
    def __init__(self, model):
        self.model = model
        self.keep_going = True

    def update(self):
        self.model.mario.setPreviousPos()
        for event in pygame.event.get():
            if event.type == QUIT:
                self.keep_going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.keep_going = False
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and not keys[K_RIGHT]:
            self.model.mario.move(False)
        if keys[K_RIGHT] and not keys[K_LEFT]:
            self.model.mario.move(True)
        if keys[K_UP] or keys[K_SPACE]:
            self.model.mario.jump()
        # if keys[K_DOWN]:
        # add mario crouch


print("Use the arrow keys to move. Press Esc to quit.")
pygame.init()
m = Model()
v = View(m)
c = Controller(m)
while c.keep_going:
    c.update()
    m.update()
    v.update()
    sleep(0.02)
print("Goodbye")
