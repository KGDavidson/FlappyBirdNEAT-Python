import pygame
import neat
import time
import os
import random
pygame.font.init()

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

scoreFont = pygame.font.SysFont("comicsans", 50)


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


class Pipe:
    gap = 200
    vel = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.pipeTop = pygame.transform.flip(pipeImg, False, True)
        self.pipeBottom = pipeImg

        self.passed = False
        self.setHeight()

    def setHeight(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.pipeTop.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.vel

    def draw(self, win):
        win.blit(self.pipeTop, (self.x, self.top))
        win.blit(self.pipeBottom, (self.x, self.bottom))

    def collide(self, bird):
        birdMask = bird.getMask()
        topMask = pygame.mask.from_surface(self.pipeTop)
        bottomMask = pygame.mask.from_surface(self.pipeBottom)

        topOffset = (self.x - bird.x, self.top - round(bird.y))
        bottomOffset = (self.x - bird.x, self.bottom - round(bird.y))

        bPoint = birdMask.overlap(bottomMask, bottomOffset)
        tPoint = birdMask.overlap(topMask, topOffset)

        if tPoint or bPoint:
            return True

        return False


class Ground:
    vel = 5
    width = groundImg.get_width()
    img = groundImg

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        if (self.x1 + self.width < 0):
            self.x1 = self.x2 + self.width

        if (self.x2 + self.width < 0):
            self.x2 = self.x1 + self.width

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


def drawWindow(win, bird, pipes, ground, score):
    win.blit(bgImg, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = scoreFont.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (winWidth - 10 - text.get_width(), 10))

    ground.draw(win)

    bird.draw(win)

    pygame.display.update()


def main():
    bird = Bird(230, 350)
    ground = Ground(730)
    pipes = [Pipe(600)]

    score = 0

    win = pygame.display.set_mode((winWidth, winHeight))
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # bird.move()
        ground.move()
        addPipe = False

        rem = []
        for pipe in pipes:
            if pipe.collide(bird):
                pass

            if pipe.x + pipe.pipeTop.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                addPipe = True
            pipe.move()

        if addPipe:
            score += 1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730:
            pass

        drawWindow(win, bird, pipes, ground, score)

    pygame.quit()
    quit()


main()
