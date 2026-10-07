import pygame


class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, (55, 60, 70), self.rect)
        pygame.draw.rect(screen, (110, 115, 125), self.rect, 2)

    def collides_with_circle(self, center, radius):
        # Find the closest point on the rectangle to the circle center.
        closest_x = max(self.rect.left, min(center.x, self.rect.right))
        closest_y = max(self.rect.top, min(center.y, self.rect.bottom))

        dx = center.x - closest_x
        dy = center.y - closest_y

        return dx * dx + dy * dy <= radius * radius

    def resolve_collision(self, marble):
        # Use the nearest point to determine the collision normal.
        closest_x = max(self.rect.left, min(marble.pos.x, self.rect.right))
        closest_y = max(self.rect.top, min(marble.pos.y, self.rect.bottom))

        normal = pygame.Vector2(
            marble.pos.x - closest_x,
            marble.pos.y - closest_y
        )

        if normal.length_squared() == 0:
            distances = [
                (abs(marble.pos.x - self.rect.left), pygame.Vector2(-1, 0)),
                (abs(marble.pos.x - self.rect.right), pygame.Vector2(1, 0)),
                (abs(marble.pos.y - self.rect.top), pygame.Vector2(0, -1)),
                (abs(marble.pos.y - self.rect.bottom), pygame.Vector2(0, 1)),
            ]
            _, normal = min(distances, key=lambda item: item[0])

        else:
            normal = normal.normalize()

        # Push the marble outside the wall.
        marble.pos += normal * 2

        # Reflect velocity only when moving toward the wall.
        dot = marble.velocity.dot(normal)

        if dot < 0:
            marble.velocity -= 1.8 * dot * normal
            marble.velocity *= 0.8

        return True