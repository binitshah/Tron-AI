import Tron
import pygame
import random

width = 600
height = 660
offset = abs(width - height)

moves = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]

def agent_moves(players):
    print(f"player1: {players[0].x} {players[0].y} | player2: {players[1].x} {players[1].y}")
    if random.randint(0, 14) == 14:
        return [pygame.event.Event(pygame.KEYDOWN, key=random.choice(moves))]
    else:
        return []

def minimaxbot_players():
        default_p1 = Tron.Player(50, (height + offset) / 2, (2, 0), (0, 255, 255), ai_controller=agent_moves)
        default_p2 = Tron.Player(width - 50, (height + offset) / 2, (-2, 0), (255, 0, 255))
        return default_p1, default_p2

tron_game = Tron.Game(width=width, height=height, players=minimaxbot_players)
tron_game.run()