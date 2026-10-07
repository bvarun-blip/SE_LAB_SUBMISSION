import math
import struct
import pygame

from .marble import Marble
from .wall import Wall


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 26)

        self.difficulties = {
            "E": {
                "name": "Easy",
                "acceleration": 0.22,
                "friction": 0.95,
                "max_speed": 6,
                "time": 45
            },
            "M": {
                "name": "Medium",
                "acceleration": 0.35,
                "friction": 0.97,
                "max_speed": 8,
                "time": 35
            },
            "H": {
                "name": "Hard",
                "acceleration": 0.50,
                "friction": 0.98,
                "max_speed": 10,
                "time": 25
            }
        }

        self.difficulty_key = "M"
        self.state = "playing"

        self.background = (235, 230, 210)
        self.goal_color = (50, 180, 80)

        self.walls = self.create_maze()

        self.goal = pygame.Rect(
            self.width - 75,
            self.height - 75,
            42,
            42
        )

        self.sound_enabled = False
        self.bounce_sound = None
        self.goal_sound = None
        self.timeout_sound = None

        self.create_sounds()
        self.start_game(self.difficulty_key)

    def create_maze(self):
        return [
            # Outer border
            Wall(0, 0, self.width, 15),
            Wall(0, self.height - 15, self.width, 15),
            Wall(0, 0, 15, self.height),
            Wall(self.width - 15, 0, 15, self.height),

            # Internal maze
            Wall(100, 70, 20, 260),
            Wall(100, 70, 180, 20),
            Wall(260, 70, 20, 170),
            Wall(180, 220, 100, 20),
            Wall(180, 220, 20, 170),
            Wall(330, 60, 20, 250),
            Wall(330, 290, 150, 20),
            Wall(470, 120, 20, 190),
            Wall(380, 120, 110, 20),
            Wall(380, 120, 20, 110),
            Wall(70, 390, 180, 20),
            Wall(250, 350, 20, 60),
            Wall(270, 350, 180, 20),
        ]

    def create_sounds(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1)

            self.bounce_sound = self.make_tone(220, 70)
            self.goal_sound = self.make_tone(700, 220)
            self.timeout_sound = self.make_tone(120, 400)

            self.sound_enabled = True
        except pygame.error:
            self.sound_enabled = False

    def make_tone(self, frequency, duration_ms):
        sample_rate = 44100
        samples = int(sample_rate * duration_ms / 1000)

        data = bytearray()

        for i in range(samples):
            value = int(
                15000 *
                math.sin(2 * math.pi * frequency * i / sample_rate)
            )
            data.extend(struct.pack("<h", value))

        return pygame.mixer.Sound(buffer=bytes(data))

    def play_sound(self, sound):
        if self.sound_enabled and sound is not None:
            sound.play()

    def start_game(self, difficulty_key):
        self.difficulty_key = difficulty_key
        settings = self.difficulties[difficulty_key]

        self.walls = self.create_maze()

        self.marble = Marble(
            45,
            45,
            radius=12,
            acceleration=settings["acceleration"],
            friction=settings["friction"],
            max_speed=settings["max_speed"]
        )

        self.time_limit = settings["time"]
        self.start_time = pygame.time.get_ticks()

        self.state = "playing"
        self.end_message = ""
        self.finish_time = 0

    def handle_event(self, event):
        if self.state == "playing":
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.start_game("E")

            elif event.key == pygame.K_m:
                self.start_game("M")

            elif event.key == pygame.K_h:
                self.start_game("H")

            elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

    def handle_input(self):
        if self.state == "playing":
            self.marble.handle_input((self.width, self.height))

    def update(self):
        if self.state != "playing":
            return

        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        remaining = self.time_limit - elapsed

        if remaining <= 0:
            self.state = "lost"
            self.end_message = "TIME'S UP!"
            self.play_sound(self.timeout_sound)
            return

        self.marble.move()

        bounced = False

        for wall in self.walls:
            if wall.collides_with_circle(
                self.marble.pos,
                self.marble.radius
            ):
                wall.resolve_collision(self.marble)
                bounced = True

        if bounced:
            self.play_sound(self.bounce_sound)

        # Goal collision.
        goal_center = pygame.Vector2(self.goal.center)

        if self.marble.pos.distance_to(goal_center) <= self.marble.radius + 20:
            self.finish_time = elapsed
            self.state = "won"
            self.end_message = "MAZE SOLVED!"
            self.play_sound(self.goal_sound)

    def render(self, screen):
        screen.fill(self.background)

        if self.state == "playing":
            self.render_game(screen)
        else:
            self.render_game(screen)
            self.render_end_screen(screen)

    def render_game(self, screen):
        # Goal
        pygame.draw.circle(
            screen,
            self.goal_color,
            self.goal.center,
            21
        )
        pygame.draw.circle(
            screen,
            (20, 100, 40),
            self.goal.center,
            21,
            3
        )

        for wall in self.walls:
            wall.draw(screen)

        self.marble.draw(screen)

        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        remaining = max(0, self.time_limit - elapsed)

        timer_text = self.font.render(
            f"Time: {remaining:.1f}s",
            True,
            (25, 25, 25)
        )

        difficulty_text = self.small_font.render(
            f"Difficulty: {self.difficulties[self.difficulty_key]['name']}",
            True,
            (25, 25, 25)
        )

        screen.blit(timer_text, (25, 20))
        screen.blit(difficulty_text, (25, 48))

        instruction = self.small_font.render(
            "Move mouse away from center to tilt",
            True,
            (30, 30, 30)
        )

        screen.blit(
            instruction,
            (self.width - instruction.get_width() - 20, 20)
        )

    def render_end_screen(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        if self.state == "won":
            title = self.big_font.render(
                "MAZE SOLVED!",
                True,
                (100, 255, 120)
            )

            subtitle = self.font.render(
                f"Finish time: {self.finish_time:.2f} seconds",
                True,
                (255, 255, 255)
            )

        else:
            title = self.big_font.render(
                "TIME'S UP!",
                True,
                (255, 100, 100)
            )

            subtitle = self.font.render(
                "You did not reach the goal in time.",
                True,
                (255, 255, 255)
            )

        screen.blit(
            title,
            (
                self.width // 2 - title.get_width() // 2,
                120
            )
        )

        screen.blit(
            subtitle,
            (
                self.width // 2 - subtitle.get_width() // 2,
                190
            )
        )

        replay = self.font.render(
            "Choose difficulty to replay:",
            True,
            (255, 255, 255)
        )

        screen.blit(
            replay,
            (
                self.width // 2 - replay.get_width() // 2,
                260
            )
        )

        options = self.font.render(
            "E = Easy     M = Medium     H = Hard",
            True,
            (255, 255, 255)
        )

        screen.blit(
            options,
            (
                self.width // 2 - options.get_width() // 2,
                305
            )
        )

        quit_text = self.font.render(
            "Q = Quit",
            True,
            (255, 255, 255)
        )

        screen.blit(
            quit_text,
            (
                self.width // 2 - quit_text.get_width() // 2,
                350
            )
        )