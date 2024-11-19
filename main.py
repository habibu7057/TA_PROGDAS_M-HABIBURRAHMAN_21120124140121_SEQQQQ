from numpy._core.defchararray import isnumeric
import pygame
import sys
import math
import numpy as np
import os

from scripts.utils import h_col, prompt_file
from scripts.ui import Button, Label

INACTIVE = 0
HOVERED = 1
JUST_PRESSED = 2
PRESSED = 3
RELEASED = 4

print("hello there!")

pygame.font.init()

header_font= pygame.font.Font("assets/fonts/JetBrainsMono-Regular.ttf", 48)
default_font = pygame.font.Font("assets/fonts/JetBrainsMono-Regular.ttf", 16)
icon_font= pygame.font.Font("assets/fonts/font bottons music.ttf", 24)
icon_font_small= pygame.font.Font("assets/fonts/font bottons music.ttf", 16)

class Track:
    def __init__(self, sample: str):
        try:
            self.sample = pygame.mixer.Sound(sample)
            self.sample_loaded = True
        except FileNotFoundError:    
            self.sample = pygame.sndarray.make_sound(np.zeros((2, 2), dtype=np.int16))
            self.sample_loaded = False
        self.sample.set_volume(0.5)

        self.has_played = False

    def __change_pitch(self, sound_array: np.ndarray, semitones:float):
        pitch_factor = 2 ** (semitones/12)
        indices = np.round(np.arange(0, len(sound_array), pitch_factor)).astype(int)
        indices = indices[indices < len(sound_array)]  # Avoid index errors
        return sound_array[indices]

    def set_sample(self, filepath: str):
        try:
            new_sample = pygame.mixer.Sound(filepath)
            self.sample = new_sample
        except pygame.error:
            print("unable to load sound! format invalid!")
            return

    def reset(self):
        self.has_played = False

    def play(self, mixer: pygame.mixer.Channel, transpose = 0):
        if transpose == 0:
            sound = self.sample
        else:
            sound_array = pygame.sndarray.array(self.sample)
            pitched_sound_array = self.__change_pitch(sound_array, transpose)
            sound = pygame.sndarray.make_sound(pitched_sound_array)

        if not self.has_played:
            # print("playsound transposed by " + str(transpose) if self.sample_loaded else "no sound is found")
            mixer.play(sound)
            self.has_played = True

    def preview(self, mixer: pygame.mixer.Channel, transpose = 0):
        if transpose == 0:
            sound = self.sample
        else:
            sound_array = pygame.sndarray.array(self.sample)
            pitched_sound_array = self.__change_pitch(sound_array, transpose)
            sound = pygame.sndarray.make_sound(pitched_sound_array)

        mixer.play(sound)


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("seqqqq")

        # 9th channel is specifically for sample preview
        pygame.mixer.set_num_channels(9)

        self.window_size = (1066, 600)

        self.screen = pygame.display.set_mode((self.window_size[0], self.window_size[1]), vsync=True)
        self.display = pygame.Surface((self.window_size[0], self.window_size[1]))

        self.clock = pygame.time.Clock()
        self.last_opened_dir = ""

        self.bpm = 120
        self.division = 4
        self.beat_duration = 60000 / (self.bpm * self.division)
        self.last_beat = 0

        self.header = header_font.render("SEQQQQmas", True, (255,255,255))

        self.tooltip = Label("", 0, 0, default_font, (255,255,255), False)

        # 16 step, 8 channels
        self.sequences = [
            [-1] * 16,
            [-1] * 16,
            [-1] * 16,
            [-1] * 16,
            [-1] * 16,
            [-1] * 16,
            [-1] * 16,
            [-1] * 16
        ]

        self.active_button_clrs = [
            (220,220,220),
            (200,200,200),
            (255,0,0),
            (255,255,0),
            (0,0,255),
        ]
        
        self.inactive_button_clrs = [
            (0,0,0),
            (50,50,50),
            (255,0,0),
            (0,255,255),
            (0,0,255),
        ]

        init_track_label_text = [
            "Kick",
            "Snare",
            "Hat",
            "Synth",
            "...",
            "...",
            "...",
            "...",
        ]

        self.track_labels = []
        self.track_buttons = []
        self.track_load_buttons = []

        button_size = 48
        button_padding = 2
        button_inset = button_size - button_padding

        seq_offset = button_size * 2

        seq_bottom = button_size * len(init_track_label_text) + seq_offset

        # long math formula to draw stuff relative to other stuff
        for (row, sequence) in enumerate(self.sequences):
            buttons: list[Button] = []
            for (col, beat) in enumerate(sequence):
                button = Button(
                    ((self.window_size[0] - button_size * len(sequence) - button_padding) + (col * button_size)) + button_padding,
                    (row * button_size) + button_padding + seq_offset,
                    button_inset,
                    button_inset
                )

                buttons.append(button)
            self.track_buttons.append(buttons)
            load_button = Button(
                    self.window_size[0] - button_size * (len(sequence) + 1),
                    (row * button_size) + button_padding + seq_offset,
                    button_inset,
                    button_inset,
                    "h"
                )

            load_button.set_color(INACTIVE, (200, 200, 200))

            self.track_load_buttons.append(load_button)
            self.track_labels.append(
                Label(
                    init_track_label_text[row], 
                    2,
                    button_size * row + seq_offset,
                    default_font,
                    (255,255,255),
                    True
                )
            )
        self.song_info_field = [
            Label(str(self.bpm), 180, seq_bottom, default_font, (255,255,255), True),
            Label(str(self.division), 180, seq_bottom + 18, default_font, (255,255,255), True)
        ]

        self.song_info_label = [
            Label("BPM", 60, seq_bottom, default_font, (255,255,255)),
            Label("Division", 60, seq_bottom + 18, default_font, (255,255,255))
        ]

        self.is_editing = False

        self.tracks = [
            Track("assets/samples/kick.wav"),
            Track("assets/samples/snare.wav"),
            Track("assets/samples/hat.wav"),
            Track("assets/samples/synth1.wav"),
            Track(""),
            Track(""),
            Track(""),
            Track(""),
        ]


        self.ui_buttons: dict[str, Button] = {
            "toggle": Button(0, 0, 32, 32, "a"),
        }

        for (i, id) in enumerate(self.ui_buttons):
            self.ui_buttons[id].set_colors(self.active_button_clrs)
            self.ui_buttons[id].rect.x = i * 36 + 4
            self.ui_buttons[id].rect.y = seq_bottom + 4

        self.tracks[0].set_sample("assets/samples/kick2.wav")

        self.last_beat = 0

        self.last_click_pos = (0,0)
        self.transpose_to = 0
        self.last_transpose_to = 0
        self.transpose_offset = 0

        self.start_time = 0
        self.is_playing = 0


    def run(self):
        # preview_text: pygame.Surface = default_font.render("", True, (0,0,0))

        while True:
            # update #
            # print(math.floor(pygame.time.get_ticks() / self.beat_duration))
            self.mouse_left_pressed = 0
            events = pygame.event.get()

            self.tooltip.pos[0] = pygame.mouse.get_pos()[0]
            self.tooltip.pos[1] = pygame.mouse.get_pos()[1]-32
            self.tooltip.update(events)

            for (i, label) in enumerate(self.song_info_field):
                label.update(events)

                if label.text.isnumeric():
                    if i == 0:
                        self.bpm = int(label.text)
                    elif i == 1:
                        self.division = int(label.text)

                    self.beat_duration = 60000 / (self.bpm * self.division)
                else:
                    if i == 0:
                        label.text = str(self.bpm)
                    elif i ==1 :
                        label.text = str(self.division)

            if self.is_playing:
                beat = math.floor((pygame.time.get_ticks() - self.start_time) / self.beat_duration)
            else:
                beat = 0

            if self.last_beat != beat:
                self.last_beat = beat
                for track in self.tracks:
                    track.reset()

            for (i, (track, sequence)) in enumerate(zip(self.tracks, self.sequences)):
                current_note = sequence[beat % 16]
                if current_note != -1:
                    track.play(pygame.mixer.Channel(i), current_note - 60)

            for event in events:
                if event.type == pygame.KEYDOWN:
                    # print(self.is_editing)
                    if event.key == pygame.K_SPACE and not self.is_editing:
                        if not self.is_playing:
                            self.is_playing = True
                            self.start_time = pygame.time.get_ticks()
                            self.ui_buttons[id].label = "g"
                        else:
                            self.is_playing = False
                            self.ui_buttons[id].label = "a"

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # we're modifying the array
            # this is hell but i want to get it done
            # are you cloning a variable or are you merely referencing its address in memory?
            # who knows
            # stay sane, use Rust
            for row in range(len(self.track_buttons)):
                for col in range(len(self.track_buttons[row])):
                    self.track_buttons[row][col].update()

                    if self.track_buttons[row][col].state == JUST_PRESSED:
                        self.last_click_pos = pygame.mouse.get_pos()

                    if self.track_buttons[row][col].state == PRESSED:
                        self.transpose_to = -math.floor((self.last_click_pos[0] - pygame.mouse.get_pos()[0]) / 16) + self.transpose_offset
                        if self.transpose_to != self.last_transpose_to:
                            self.tracks[row].preview(pygame.mixer.Channel(8), self.transpose_to)
                            self.last_transpose_to = self.transpose_to
                            # preview_text = default_font.render(str(self.transpose_to), True, (0,0,0))
                            self.tooltip.text = "Pitch: " + str(self.transpose_to)

                    if self.track_buttons[row][col].state == RELEASED:
                        #print("modified", row, col)
                        self.tooltip.text = ""

                        if self.sequences[row][col] == -1 or self.transpose_to != self.transpose_offset:
                            self.sequences[row][col] = 60 + self.transpose_to
                            self.transpose_offset = self.transpose_to
                        elif self.transpose_to == self.transpose_offset:
                            self.sequences[row][col] = -1

                    if self.sequences[row][col] == -1:
                        colors = self.inactive_button_clrs
                        self.track_buttons[row][col].label = ""
                    else:
                        colors = self.active_button_clrs
                        if self.sequences[row][col] != 60:
                            self.track_buttons[row][col].label = str(self.sequences[row][col] - 60)
                        else:
                            self.track_buttons[row][col].label = ""

                    self.track_buttons[row][col].set_colors(colors)

                    if col == beat % 16 and self.sequences[row][col] == -1:
                        self.track_buttons[row][col].set_color(INACTIVE, (255,0,0))

            for (i, button) in enumerate(self.track_load_buttons):
                button.update()

                if button.state == RELEASED:
                    filepath = prompt_file([("Wave", "*.wav"), ("Vorbis", "*.ogg"), ("MPEG 3", "*.mp3")], self.last_opened_dir)
                    if filepath:
                        self.tracks[i].set_sample(filepath)
                        self.last_opened_dir = os.path.dirname(filepath)
            
            for id in self.ui_buttons:
                self.ui_buttons[id].update()
                button_state =  self.ui_buttons[id].state

                if id == "toggle" and button_state == RELEASED:
                    if not self.is_playing:
                        self.is_playing = True
                        self.start_time = pygame.time.get_ticks()
                        self.ui_buttons[id].label = "g"
                    else:
                        self.is_playing = False
                        self.ui_buttons[id].label = "a"

                """
                if id == "load_sound" and button_state == RELEASED:
                    print(prompt_file([("Wave", "*.wav"), ("Vorbis", "*.ogg"), ("MPEG 3", "*.mp3")]))
                    print("loading")
                """

            editing_count = 0
            for label in self.track_labels:
                label.update(events)

                if label.state == 1:
                    editing_count += 1

            self.is_editing = editing_count > 0

            """
            for i in range(len(self.track_buttons)):
                for j in range(len(self.track_buttons[i])):
                    self.track_buttons[j][i].update()

                    if self.track_buttons[j][i].state == RELEASED:
                        if self.sequences[j][i] == -1:
                            self.sequences[j][i] = 60
                        else:
                            self.sequences[j][i] = -1

                    self.track_buttons[j][i].set_colors(self.inactive_button_clrs if self.sequences[i][j] == -1 else self.active_button_clrs)

                    if i == beat % 16:
                        self.track_buttons[j][i].set_color(INACTIVE, (255,0,0))
            """

            # draw #
            self.display.fill(h_col("#222222"))

            for buttons in self.track_buttons:
                for button in buttons:
                    button.draw(self.display, default_font)

            for button in self.track_load_buttons:
                button.draw(self.display, icon_font)


            for id, button in self.ui_buttons.items():
                button.draw(self.display, icon_font_small)

            for label in self.track_labels:
                label.draw(self.display)

            for label in self.song_info_field:
                label.draw(self.display)
            
            for label in self.song_info_label:
                label.draw(self.display)

            self.display.blit(self.header, (10, 10))

            # self.display.blit(preview_text, (2,2))
            self.tooltip.draw(self.display)
            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()),
                (0, 0)
            )

            pygame.display.update()
            self.clock.tick(60)  # target fps


Game().run()
