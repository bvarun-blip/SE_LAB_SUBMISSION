import pygame
from pygame.math import Vector2


class Marble:
    def __init__(self, x, y, radius=12, acceleration=0.35,
                 friction=0.97, max_speed=8):
        self.start_pos = Vector2(x, y)
        self.pos = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.radius = radius
        self.acceleration = acceleration
        self.friction = friction
        self.max_speed = max_speed

    def reset(self):
        self.pos = self.start_pos.copy()
        self.velocity = Vector2(0, 0)

    def handle_input(self, screen_size):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        center = Vector2(screen_size[0] / 2, screen_size[1] / 2)
        direction = Vector2(mouse_x, mouse_y) - center

        if direction.length() > 10:
            direction = direction.normalize()
            self.velocity += direction * self.acceleration

        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

    def move(self):
        self.pos += self.velocity
        self.velocity *= self.friction

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            (220, 50, 50),
            (int(self.pos.x), int(self.pos.y)),
            self.radius
        )
        pygame.draw.circle(
            screen,
            (255, 220, 220),
            (int(self.pos.x - 4), int(self.pos.y - 4)),
            3
        )