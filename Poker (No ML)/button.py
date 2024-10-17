import pygame
import sys


class Button():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = None
        self.alreadyPressed = False
        self.buttonSurf = None

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)



    def setButton(self, buttonText, onclickFunction):
        pygame.init()
        font = pygame.font.SysFont('Arial', 40, False, False)
        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))
        self.onclickFunction = onclickFunction





