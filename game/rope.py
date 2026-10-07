import math
import pygame


class Rope:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_y = screen_height // 2
        self.marker_x = float(screen_width // 2)
        self.left_win_x = 180
        self.right_win_x = screen_width - 180
        self.pull_step = 12

        # Task 3: visual state for momentum and tension.
        self.velocity = 0.0
        self.tension = 0.0

    def pull_left(self, strength=1.0):
        delta = self.pull_step * max(0.0, strength)
        self.marker_x = max(self.left_win_x, self.marker_x - delta)
        self.velocity = -delta
        self.tension = min(1.0, self.tension + 0.18 + 0.10 * min(strength, 2.5))

    def pull_right(self, strength=1.0):
        delta = self.pull_step * max(0.0, strength)
        self.marker_x = min(self.right_win_x, self.marker_x + delta)
        self.velocity = delta
        self.tension = min(1.0, self.tension + 0.18 + 0.10 * min(strength, 2.5))

    def check_winner(self):
        if self.marker_x <= self.left_win_x:
            return "PLAYER"
        if self.marker_x >= self.right_win_x:
            return "COMPUTER"
        return None

    def update(self):
        """Decay momentum/tension between pulls for smooth animation."""
        self.velocity *= 0.88
        self.tension *= 0.94
        if abs(self.velocity) < 0.05:
            self.velocity = 0.0
        if self.tension < 0.02:
            self.tension = 0.0

    def reset(self):
        self.marker_x = float(self.screen_width // 2)
        self.velocity = 0.0
        self.tension = 0.0

    def _rope_points(self):
        """Create sag at low tension and vibration at high tension."""
        now = pygame.time.get_ticks()
        struggle = max(
            self.tension,
            min(1.0, abs(self.velocity) / max(1.0, self.pull_step * 2.5)),
        )
        sag_amount = 16.0 * (1.0 - struggle)
        vibration_amount = 1.0 + 3.5 * struggle

        points = []
        start_x, end_x = 60, self.screen_width - 60
        segments = 32
        for i in range(segments + 1):
            x = start_x + (end_x - start_x) * i / segments
            normalized = i / segments
            sag = math.sin(math.pi * normalized) * sag_amount
            wave = math.sin(now * 0.045 + x * 0.07) * vibration_amount * struggle
            y = self.center_y + sag + wave
            points.append((round(x), round(y)))
        return points, struggle

    def render(self, surface):
        points, struggle = self._rope_points()

        pygame.draw.lines(surface, (105, 80, 55), False, points, 14)
        pygame.draw.lines(surface, (180, 140, 90), False, points, 10)

        pygame.draw.line(surface, (50, 200, 50),
                         (self.left_win_x, self.center_y - 40),
                         (self.left_win_x, self.center_y + 40), 4)
        pygame.draw.line(surface, (200, 50, 50),
                         (self.right_win_x, self.center_y - 40),
                         (self.right_win_x, self.center_y + 40), 4)
        pygame.draw.line(surface, (120, 120, 120),
                         (self.screen_width // 2, self.center_y - 20),
                         (self.screen_width // 2, self.center_y + 20), 2)

        flag_rect = pygame.Rect(int(self.marker_x) - 12, self.center_y - 24, 24, 48)
        pygame.draw.rect(surface, (230, 40, 40), flag_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), flag_rect, width=2, border_radius=4)

        if struggle > 0.15:
            label_font = pygame.font.SysFont(None, 22)
            label = "TENSION" if struggle > 0.45 else "STRAIN"
            text = label_font.render(label, True, (255, 215, 120))
            surface.blit(text, (self.screen_width // 2 - text.get_width() // 2, self.center_y + 85))
