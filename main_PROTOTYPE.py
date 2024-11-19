import pygame
import sys
import math

from scripts.utils import h_col

print("hello there!")


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("seqqqq")

        self.screen = pygame.display.set_mode((640, 480), vsync=True)
        self.display = pygame.Surface((640, 480))

        self.clock = pygame.time.Clock()

        self.bpm = 120
        self.division = 4
        self.beat_duration = 60000 / (self.bpm * self.division)
        self.last_beat = 0

        # test
        self.sequence = [
            "x...x...xx..x...",
            "....x.......x...",
            "..x...x...x...xx",
        ]

        self.sounds = [
            pygame.mixer.Sound("samples/kick.wav"),
            pygame.mixer.Sound("samples/snare.wav"),
            pygame.mixer.Sound("samples/hat.wav")
        ]

        for sound in self.sounds:
            sound.set_volume(0.5)

        self.sound_played_list = [
            False,
            False,
            False
        ]

    def run(self):
        while True:
            # update #
            # print(math.floor(pygame.time.get_ticks() / self.beat_duration))

            beat = math.floor(pygame.time.get_ticks() / self.beat_duration)

            if self.last_beat != beat:
                self.last_beat = beat

                for i in range(len(self.sound_played_list)):
                    self.sound_played_list[i] = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # draw #
            self.display.fill(h_col("#14a3ff"))

            for i, track in enumerate(self.sequence):
                for j, item in enumerate(track):
                    if beat % 16 == j:
                        color: tuple = (100, 0, 0) if item == "." else (0, 255, 255)
                    else:
                        color = (0, 0, 0) if item == "." else (255, 255, 255)

                    if beat % 16 == j and item == "x" and not self.sound_played_list[i]:
                        pygame.mixer.Channel(i).play(self.sounds[i])
                        print("play sound!", i)
                        self.sound_played_list[i] = True

                    pygame.draw.rect(self.display, color,
                                     (j * 20 + 20, i * 20 + 20, 18, 18))

            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()),
                (0, 0)
            )

            pygame.display.update()
            self.clock.tick(60)  # target fps


Game().run()
