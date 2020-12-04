import pygame
import neat
import time
import os
import random

winWidth = 500
winHeight = 800

birdImgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("sprites", "bird1.png"))), pygame.transform.scale2x(
    pygame.image.load(os.path.join("sprites", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("sprites", "bird3.png")))]
pipeImg = pygame.transform.scale2x(
    pygame.image.load(os.path.join("sprites", "pipe.png")))
groundImg = pygame.transform.scale2x(
    pygame.image.load(os.path.join("sprites", "ground.png")))
bgImg = pygame.transform.scale2x(
    pygame.image.load(os.path.join("sprites", "bg.png")))


class Bird:
    imgs = birdImgs
    maxRotation = 25
    rotVel = 20
    animationTime = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tickCount = 0
        self.vel = 0
        self.height = self.y
        self.imgCount = 0
        self.img = self.imgs[0]

    def jump(self):
        self.vel = -10.5
        self.tickCount = 0
        self.height = self.y

    def move(self):
        self.tickCount += 1

        d = self.vel * self.tickCount + 1.5 * self.tickCount ** 2

        if (d >= 16):
            d = 16

        if (d < 0):
            d -= 2

        self.y += d

        if (d < 0 or self.y < self.height + 50):
            if self.tilt < self.maxRotation:
                self.tilt = self.maxRotation
        else:
            if self.tilt > -90:
                self.tilt -= self.rotVel

    def draw(self, win):
        self.imgCount += 1

        if (self.imgCount < self.animationTime):
            self.img = self.imgs[0]
        elif self.imgCount < self.animationTime * 2:
            self.img = self.imgs[1]
        elif self.imgCount < self.animationTime * 3:
            self.img = self.imgs[2]
        elif self.imgCount < self.animationTime * 4:
            self.img = self.imgs[1]
        elif self.imgCount == self.animationTime * 4 + 1:
            self.img = self.imgs[0]
            self.imgCount = 0

        if self.tilt <= -80:
            self.img = self.imgs[1]
            self.imgCount = self.animationTime * 2

        rotatedImg = pygame.transform.rotate(self.img, self.tilt)
        newRect = rotatedImg.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotatedImg, newRect.topleft)

    def getMask(self):
        return pygame.mask.from_surface(self.img)


def drawWindow(win, bird):
    win.blit(bgImg, (0, 0))
    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(200, 200)
    win = pygame.display.set_mode((winWidth, winHeight))
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # bird.move()
        drawWindow(win, bird)

    pygame.quit()
    quit()


main()
