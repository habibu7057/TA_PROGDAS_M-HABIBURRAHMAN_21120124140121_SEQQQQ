import pygame
from pygame.constants import K_SPACE

# enums :(
INACTIVE = 0
HOVERED = 1
JUST_PRESSED = 2
PRESSED = 3
RELEASED = 4

pygame.font.init()

default_font = pygame.font.Font("assets/fonts/JetBrainsMono-Regular.ttf", 16)
icon_font= pygame.font.Font("assets/fonts/font bottons music.ttf", 24)

class Button:
    def __init__(self, x, y, w, h, label=""):
        self.rect = pygame.Rect(x, y, w, h)

        self.state = INACTIVE
        self.label = label
        self.colors = [(0,0,0), (100,100,100), (255,0,0), (100,0,0), (0,0,255)]
        self.__mouse_entered = False
        self.__mouse_exited = False
        self.__is_hovered = False

    def set_color(self, state, color):
        self.colors[state] = color

    def set_colors(self, colors):
        for i in range(min(len(colors), len(self.colors))):
            self.colors[i] = colors[i]

    def update(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_focused():
            if not self.__mouse_entered and not self.__is_hovered:
                self.__mouse_entered = True
                self.__is_hovered = True
            elif self.__mouse_entered:
                self.__mouse_entered = False
        else:
            if not self.__mouse_exited and self.__is_hovered:
                self.__mouse_exited = True
                self.__is_hovered = False
            elif self.__mouse_exited:
                self.__mouse_exited = False

        if not pygame.mouse.get_pressed()[0] and self.state != PRESSED:
            self.state = HOVERED if self.__is_hovered else INACTIVE

        if self.state == JUST_PRESSED:
            self.state = PRESSED
        if self.state == RELEASED:
            self.state = INACTIVE

        if pygame.mouse.get_just_pressed()[0] and self.__is_hovered:
            self.state = JUST_PRESSED
        elif pygame.mouse.get_just_released()[0] and self.state == PRESSED:
            self.state = RELEASED


    def draw(self, surface:pygame.Surface, font:pygame.Font):
        text = font.render(self.label, True, (0,0,0))
        text_rect = text.get_rect(center=(self.rect.center))

        pygame.draw.rect(surface, self.colors[self.state], self.rect)
        surface.blit(text, text_rect)

INACTIVE = 0
PENDING = 1
CONFIRM = 2

class Label:
    def __init__(self, text:str, x, y, font:pygame.Font, color:tuple[int, int, int], editable=False):
        self.text = text
        self.font = font
        self.color = color
        self.pos: list[int] = [x, y]
        self.is_editable = editable
        self.state = INACTIVE
        self.dest_text:str = ""

        self.text_surface = self.font.render(self.text, True, self.color)

        self.use_capital = False

    def update(self, events):
        if self.get_rect().collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_just_pressed()[0] and self.is_editable:
            self.state = PENDING

        # text input handling
        # horrifying
        # basically stringifies the keycode if it's a letter
        # this is gonna be the death of me
        if self.state == PENDING:
            self.color = (255, 255, 0)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.use_capital = True
                    elif event.key == pygame.K_RETURN:
                        self.state = CONFIRM
                    elif event.key == pygame.K_BACKSPACE:
                        self.dest_text = self.dest_text[0:-1]
                    elif pygame.key.name(event.key).isalnum() or event.key == K_SPACE:
                        if event.key != pygame.K_SPACE:
                            if not self.use_capital:
                                self.dest_text += pygame.key.name(event.key)
                            else:
                                self.dest_text += pygame.key.name(event.key).upper()
                        elif event.key == pygame.K_SPACE:
                            self.dest_text += " "
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.use_capital = False

        if self.state == CONFIRM:
            if self.dest_text == "":
                self.dest_text = "..."
            self.set_text(self.dest_text)
            self.dest_text = ""
            self.color = (255, 255, 255)
            self.state = INACTIVE

    def get_rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.text_surface.get_size()[0], self.text_surface.get_size()[1])

    def set_text(self, text: str):
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = pygame.Rect(self.pos[0], self.pos[1], self.text_surface.get_size()[0], self.text_surface.get_size()[1])

    def draw(self, surface:pygame.Surface):
        # pygame.draw.rect(surface, (255,0,0), self.get_rect())
        if self.state == INACTIVE:
            text = self.font.render(self.text, True, self.color)
            surface.blit(text, self.pos)
        elif self.state == PENDING:
            text = self.font.render(self.dest_text, True, self.color)
            
            caret = text.get_rect()
            caret.x, caret.y = self.pos[0] + caret.width, self.pos[1]
            caret.width = 2

            pygame.draw.rect(surface, (255,255,255), caret)
            surface.blit(text, self.pos)



