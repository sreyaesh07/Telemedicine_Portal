"""
GameEngine: owns the helicopter and all obstacles.

Collision detection and game over / restart are handled here (Task 2),
along with the distance score (Task 3) and the shield (Task 4).
"""

import random

import pygame

from game.helicopter import Helicopter
from game.obstacle import Obstacle
from game.renderer import WIDTH, HEIGHT

SPAWN_INTERVAL_FRAMES = 90
GAP_HEIGHT = 150
WALL_WIDTH = 60
SCROLL_SPEED = 3
PIXELS_PER_METER = 10   # scroll pixels that count as one meter of distance

COLOR_SHIELD_TEXT = (0, 120, 200)


class GameEngine:
    def __init__(self):
        self._reset()

    def _reset(self):
        """Put the game back into its starting state."""
        self.helicopter = Helicopter(x=100, y=HEIGHT / 2)
        self.obstacles = []
        self.frames_until_spawn = 0
        self.game_over = False
        self.distance = 0.0   # in scroll pixels; converted to meters for display
        self.shield_active = False

    def _distance_meters(self):
        return int(self.distance / PIXELS_PER_METER)

    def _spawn_obstacle(self):
        margin = 60
        gap_y = random.randint(margin + GAP_HEIGHT // 2, HEIGHT - margin - GAP_HEIGHT // 2)
        self.obstacles.append(Obstacle(
            x=WIDTH, gap_y=gap_y, gap_height=GAP_HEIGHT,
            wall_width=WALL_WIDTH, screen_height=HEIGHT, speed=SCROLL_SPEED,
        ))

    def _find_collision(self):
        """Return the first obstacle the helicopter is touching, or None.

        Obstacles whose hit was already absorbed by the shield are skipped,
        so the helicopter can safely finish passing through them.
        """
        heli_rect = self.helicopter.get_rect()
        for obstacle in self.obstacles:
            if obstacle.shield_hit:
                continue
            # Check the two wall rects separately; the gap between them
            # is not part of either rect, so flying through it is safe.
            if heli_rect.colliderect(obstacle.get_top_rect()):
                return obstacle
            if heli_rect.colliderect(obstacle.get_bottom_rect()):
                return obstacle
        return None

    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        self.helicopter.handle_input(keys_pressed)

    def handle_keydown(self, key):
        if self.game_over:
            if key == pygame.K_r:
                self._reset()
        elif key == pygame.K_SPACE:
            self.shield_active = True

    def update(self):
        if self.game_over:
            return

        self.helicopter.update(HEIGHT)

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_obstacle()
            self.frames_until_spawn = SPAWN_INTERVAL_FRAMES

        for obstacle in self.obstacles:
            obstacle.update()
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]

        hit = self._find_collision()
        if hit is not None:
            if self.shield_active:
                # Shield absorbs this one obstacle and is used up. Marking the
                # obstacle means it can't hurt us (or drain a future shield)
                # on the following frames while we're still overlapping it.
                self.shield_active = False
                hit.shield_hit = True
            else:
                self.game_over = True

        if not self.game_over:
            # Only count distance for frames the helicopter survives
            self.distance += SCROLL_SPEED

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.helicopter, self.obstacles,
                            shield_active=self.shield_active)

        distance_text = f"Distance: {self._distance_meters()} m"
        if self.game_over:
            renderer.draw_banner(surface, font, "GAME OVER - Press R to restart")
            # Final distance, centered just below the banner
            final_text = f"Final {distance_text}"
            text_w, _ = font.size(final_text)
            pos = ((surface.get_width() - text_w) // 2, surface.get_height() // 2 + 30)
            renderer.draw_text(surface, font, final_text, pos)
        else:
            renderer.draw_text(surface, font, distance_text, (10, 10))
            if self.shield_active:
                renderer.draw_text(surface, font, "SHIELD", (10, 40), COLOR_SHIELD_TEXT)