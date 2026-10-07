import math
import pygame


class Puller:
    """Represents a puller character anchor on either side of the rope."""

    def __init__(self, x, y, color, label):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.font = pygame.font.SysFont(None, 24)

    def render(self, surface, lean=0.0, effort=0.0):
        """Draw the puller with a dynamic lean based on rope momentum."""
        axis = pygame.Vector2(math.sin(lean), -math.cos(lean))
        side = pygame.Vector2(math.cos(lean), math.sin(lean))

        base = pygame.Vector2(self.x, self.y + 35)
        body_center = base + axis * 35
        body_half_height = 34
        body_half_width = 20

        body_corners = [
            body_center - side * body_half_width - axis * body_half_height,
            body_center + side * body_half_width - axis * body_half_height,
            body_center + side * body_half_width + axis * body_half_height,
            body_center - side * body_half_width + axis * body_half_height,
        ]
        pygame.draw.polygon(surface, self.color, body_corners)

        head_center = base + axis * 78
        pygame.draw.circle(surface, (240, 210, 180), (round(head_center.x), round(head_center.y)), 16)

        left_foot = base - side * 10
        right_foot = base + side * 10
        left_knee = base - side * 14 + axis * 20
        right_knee = base + side * 14 + axis * 20
        pygame.draw.line(surface, (25, 25, 25), (round(left_foot.x), round(left_foot.y)),
                         (round(left_knee.x), round(left_knee.y)), 6)
        pygame.draw.line(surface, (25, 25, 25), (round(right_foot.x), round(right_foot.y)),
                         (round(right_knee.x), round(right_knee.y)), 6)

        arm_length = 18 + int(8 * max(0.0, min(1.0, effort)))
        shoulder = body_center + axis * 5
        left_hand = shoulder - side * arm_length - axis * 12
        right_hand = shoulder + side * arm_length - axis * 12
        pygame.draw.line(surface, (30, 30, 30), (round(shoulder.x), round(shoulder.y)),
                         (round(left_hand.x), round(left_hand.y)), 5)
        pygame.draw.line(surface, (30, 30, 30), (round(shoulder.x), round(shoulder.y)),
                         (round(right_hand.x), round(right_hand.y)), 5)

        label_surf = self.font.render(self.label, True, (240, 240, 240))
        surface.blit(label_surf, (self.x - label_surf.get_width() // 2, self.y + 45))
