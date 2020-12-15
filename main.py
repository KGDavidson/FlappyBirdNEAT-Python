import pygame
import neat
import time
import os
import random

######

PIPE_SPACING = 100
TICK_SPEED = 240

######

pygame.font.init()

winWidth = 500
winHeight = 800

gen = -1

pipeImg = pygame.transform.scale2x(
    pygame.image.load(os.path.join("sprites", "pipe.png")))
bgImg = pygame.transform.scale2x(
    pygame.image.load(os.path.join("sprites", "bg.png")))
birdImgs = [pygame.transform.scale2x(pygame.image.load(
    os.path.join("sprites", "bird" + str(x) + ".png"))) for x in range(1, 4)]
groundImg = pygame.transform.scale2x(
    pygame.image.load(os.path.join("sprites", "ground.png")))

font = pygame.font.SysFont("comicsans", 50)


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

        displacement = self.vel*(self.tickCount) + 0.5*(3)*(self.tickCount)**2

        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
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


def drawWindow(win, birds, pipes, ground, score, gen):
    win.blit(bgImg, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    scoreText = font.render("Score: " + str(score), 1, (255, 255, 255))
    genText = font.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(scoreText, (winWidth - 15 - scoreText.get_width(), 10))
    win.blit(genText, (winWidth - 15 - genText.get_width(),
                       20 + genText.get_height()))

    ground.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()


def main(genomes, config):
    global PIPE_SPACING
    global TICK_SPEED
    global gen

    gen += 1

    birds = []
    nets = []
    ge = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))

        g.fitness = 0
        ge.append(g)

    ground = Ground(730)
    pipes = [Pipe(PIPE_SPACING + 500)]

    score = 0

    win = pygame.display.set_mode((winWidth, winHeight))
    pygame.display.set_caption('Flappy Bird AI')
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(TICK_SPEED)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipeIndex = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipeTop.get_width():
                pipeIndex = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            output = nets[x].activate((bird.y, abs(
                bird.y - pipes[pipeIndex].height), abs(bird.y - pipes[pipeIndex].bottom)))

            if output[0] > 0.5:
                bird.jump()

        addPipe = False
        ground.move()

        rem = []
        for pipe in pipes:
            pipe.move()
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    addPipe = True

            if pipe.x + pipe.pipeTop.get_width() < 0:
                rem.append(pipe)

        if addPipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(PIPE_SPACING + 500))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() - 10 >= 730 or bird.y < -50:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        drawWindow(win, birds, pipes, ground, score, gen)


def run(configPath):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, configPath)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    localDir = os.path.dirname(__file__)
    configPath = os.path.join(localDir, 'config.txt')
    run(configPath)
