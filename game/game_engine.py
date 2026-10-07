import random
import pygame
from game.rope import Rope
from game.player import Puller


class GameEngine:
    """Coordinates input, AI, match state, timer, and rendering."""

    MATCH_DURATION_MS = 45_000
    SUDDEN_DEATH_MULTIPLIER = 2.0
    PANIC_DISTANCE = 140
    NORMAL_AI_COOLDOWN = 180
    PANIC_AI_COOLDOWN = 70

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rope = Rope(width, height)
        self.player = Puller(90, height // 2, (50, 120, 220), "PLAYER (A/D)")
        self.computer = Puller(width - 90, height // 2, (220, 80, 50), "COMPUTER")

        # Task 1: use the previous KEYDOWN only. KEYUP is not part of the lock.
        # This prevents rapid/overlapping presses from deadlocking the input.
        self.last_key = None

        self.winner = None
        self.game_state = "PLAYING"
        self.last_computer_pull = pygame.time.get_ticks()
        self.computer_pull_cooldown = self.NORMAL_AI_COOLDOWN
        self.panic_level = 0.0

        # Task 4: match timer and sudden death.
        self.match_start_time = pygame.time.get_ticks()
        self.elapsed_ms = 0
        self.sudden_death = False

        self.font_big = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 26)
        self.font_timer = pygame.font.SysFont(None, 30)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        # Task 1: every A/D KEYDOWN that alternates from the previous key
        # immediately becomes a pull. Late/missing KEYUP events cannot lock it.
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_a, pygame.K_d):
            if event.key != self.last_key:
                pull_strength = self.SUDDEN_DEATH_MULTIPLIER if self.sudden_death else 1.0
                self.rope.pull_left(pull_strength)
                self.last_key = event.key

    def _update_ai_difficulty(self):
        """Task 2: faster/stronger computer pulls as the player nears victory."""
        distance = self.rope.marker_x - self.rope.left_win_x
        self.panic_level = max(
            0.0,
            min(1.0, (self.PANIC_DISTANCE - distance) / self.PANIC_DISTANCE),
        )
        cooldown_range = self.NORMAL_AI_COOLDOWN - self.PANIC_AI_COOLDOWN
        self.computer_pull_cooldown = int(
            self.NORMAL_AI_COOLDOWN - cooldown_range * self.panic_level
        )

    def _computer_pull_strength(self):
        # Normal AI = 0.8 to 2.5x based on panic; sudden death doubles it.
        strength = 0.8 + 1.7 * self.panic_level
        if self.sudden_death:
            strength *= self.SUDDEN_DEATH_MULTIPLIER
        return strength

    def _check_timer(self, now):
        self.elapsed_ms = now - self.match_start_time
        if self.elapsed_ms >= self.MATCH_DURATION_MS and not self.sudden_death:
            self.sudden_death = True
            self.last_computer_pull = now

    def update(self):
        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        self._check_timer(now)
        self._update_ai_difficulty()

        # Task 2: panic surges reduce cooldown and increase pull strength.
        if now - self.last_computer_pull >= self.computer_pull_cooldown:
            variance = random.uniform(0.85, 1.15)
            self.rope.pull_right(self._computer_pull_strength() * variance)
            self.last_computer_pull = now

        # Task 3: smoothly decay momentum/tension for animation.
        self.rope.update()

        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def reset(self):
        self.rope.reset()
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.last_computer_pull = pygame.time.get_ticks()
        self.computer_pull_cooldown = self.NORMAL_AI_COOLDOWN
        self.panic_level = 0.0
        self.match_start_time = pygame.time.get_ticks()
        self.elapsed_ms = 0
        self.sudden_death = False

    def _format_timer(self):
        seconds = min(self.elapsed_ms // 1000, self.MATCH_DURATION_MS // 1000)
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def render(self, screen):
        screen.fill((30, 32, 36))

        mud_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 - 80, 240, 160)
        pygame.draw.rect(screen, (45, 38, 30), mud_rect, border_radius=12)

        # Task 3: leaning follows rope momentum.
        momentum = max(-1.0, min(1.0, self.rope.velocity / 24.0))
        player_lean = -0.16 - 0.28 * max(0.0, -momentum)
        computer_lean = 0.16 + 0.28 * max(0.0, momentum)

        self.rope.render(screen)
        self.player.render(screen, lean=player_lean, effort=abs(momentum))
        self.computer.render(screen, lean=computer_lean, effort=abs(momentum))

        inst_surf = self.font_small.render(
            "Alternate [A] and [D] keys rapidly to pull!", True, (210, 210, 210)
        )
        screen.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, 40))

        timer_text = (
            "SUDDEN DEATH 2x POWER" if self.sudden_death else f"TIME  {self._format_timer()}"
        )
        timer_color = (255, 210, 80) if self.sudden_death else (240, 240, 240)
        timer_surf = self.font_timer.render(timer_text, True, timer_color)
        screen.blit(timer_surf, (self.width // 2 - timer_surf.get_width() // 2, 8))

        if self.panic_level > 0:
            panic_percent = int(self.panic_level * 100)
            panic_surf = self.font_small.render(
                f"PANIC SURGE {panic_percent}%", True, (255, 160, 70)
            )
            screen.blit(panic_surf, (self.width - panic_surf.get_width() - 15, 12))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            win_text = f"{self.winner} WINS!"
            color = (80, 220, 80) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 50),
            )

            result_timer = self.font_small.render(
                f"Match time: {self._format_timer()}", True, (230, 230, 230)
            )
            screen.blit(
                result_timer,
                (self.width // 2 - result_timer.get_width() // 2, self.height // 2 - 5),
            )

            restart_surf = self.font_small.render(
                "Press [R] to Play Again", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 30),
            )
