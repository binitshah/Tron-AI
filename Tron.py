import pygame
import time

class Player:
    def __init__(self, x, y, bearing, color, speed=1, boost_multiplier=1, num_boosts=3, ai_controller=None):
        """
        sets player's initial values
        """
        self.x = x  # player x coord
        self.y = y  # player y coord
        self.bearing = bearing  # player direction
        self.color = color
        self.speed = speed * 2  # player speed
        self.boost_multiplier = boost_multiplier  # multiplies player speed for boost duration
        self.num_boosts_left = num_boosts
        self.boost_start_time = time.time()  # used to control boost length
        self.bounding_box = pygame.Rect(self.x - 1, self.y - 1, 2, 2)  # player rect object
        self.path = []
        self.ai_controller = ai_controller

    def move(self):
        """
        moves the player
        """
        self.x += self.bearing[0] * self.boost_multiplier
        self.y += self.bearing[1] * self.boost_multiplier
        self.path.append(self.bounding_box)
        self.bounding_box = pygame.Rect(self.x - 1, self.y - 1, 2, 2)

    def boost(self):
        """
        starts the player boost
        """
        if self.num_boosts_left > 0:
            self.num_boosts_left -= 1
            self.boost_multiplier = 2
            self.boost_start_time = time.time()

class Game:
    def __init__(self, width=600, height=660, headless=False, players=None):
        """
        sets game's initial values
        """
        self.width = width
        self.height = height
        self.offset = abs(height - width)
        if players:
            self.players_generator = players
            self.players = players()
        else:
            self.players_generator = self.default_players
            self.players = self.default_players()
        self.scores = [0, 0]
        self.walls = [pygame.Rect(0, self.offset, 15, height),
                      pygame.Rect(0, self.offset, width, 15),
                      pygame.Rect(width - 15, self.offset, 15, height),
                      pygame.Rect(0, height - 15, width, 15)]

        self.headless = headless
        if not headless:
            pygame.init()
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Tron")
            self.font = pygame.font.Font(None, 72)
            self.clock = pygame.time.Clock()

    def default_players(self, p1_color=(0, 255, 255), p2_color=(255, 0, 255)):
        default_p1 = Player(50, (self.height + self.offset) / 2, (2, 0), p1_color)
        default_p2 = Player(self.width - 50, (self.height + self.offset) / 2, (-2, 0), p2_color)
        return default_p1, default_p2
    
    def inputUpdate(self):
        """
        takes input from user/ai and apply update to game dynamics

        :return: Whether quit was NOT triggered
        :rtype: boolean
        """
        if self.headless:
            return True

        input_events = pygame.event.get()

        p1 = self.players[0]
        if p1.ai_controller:
            # remove all user key events for wasd + tab
            input_events = list(filter(lambda event: event.type != pygame.KEYDOWN or event.key != pygame.K_w or event.key != pygame.K_a or event.key != pygame.K_s or event.key != pygame.K_d or event.key != pygame.K_TAB, input_events))
            input_events += p1.ai_controller()
        
        p2 = self.players[1]
        if p2.ai_controller:
            # remove all user key presses for arrow keys + rshift
            input_events = list(filter(lambda event: event.type != pygame.KEYDOWN or event.key != pygame.K_UP or event.key != pygame.K_LEFT or event.key != pygame.K_DOWN or event.key != pygame.K_RIGHT or event.key != pygame.K_RSHIFT, input_events))
            input_events += p2.ai_controller()

        for event in input_events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                # === Player 1 === #
                if event.key == pygame.K_w:
                    if p1.bearing != (0, p1.speed):
                        p1.bearing = (0, -p1.speed)
                elif event.key == pygame.K_s:
                    if p1.bearing != (0, -p1.speed):
                        p1.bearing = (0, p1.speed)
                elif event.key == pygame.K_a:
                    if p1.bearing != (p1.speed, 0):
                        p1.bearing = (-p1.speed, 0)
                elif event.key == pygame.K_d:
                    if p1.bearing != (-p1.speed, 0):
                        p1.bearing = (p1.speed, 0)
                elif event.key == pygame.K_TAB:
                    p1.boost()
                # === Player 2 === #
                if event.key == pygame.K_UP:
                    if p2.bearing != (0, p2.speed):
                        p2.bearing = (0, -p2.speed)
                elif event.key == pygame.K_DOWN:
                    if p2.bearing != (0, -p2.speed):
                        p2.bearing = (0, p2.speed)
                elif event.key == pygame.K_LEFT:
                    if p2.bearing != (p2.speed, 0):
                        p2.bearing = (-p2.speed, 0)
                elif event.key == pygame.K_RIGHT:
                    if p2.bearing != (-p2.speed, 0):
                        p2.bearing = (p2.speed, 0)
                elif event.key == pygame.K_RSHIFT:
                    p2.boost()

        return True

    def playersChecks(self):
        """
        checks state of the player to modify behavior of the game
        """
        collided_players_indices = []
        for i in range(2):
            # ensure that players cannot boost longer than 0.5s
            if time.time() - self.players[i].boost_start_time >= 0.5:
                self.players[i].boost_multiplier = 1

            # check for wall collisions
            if self.players[i].bounding_box.collidelist(self.walls) > -1:
                collided_players_indices.append(i)

            # check for path collisions
            last_bounding_box = None
            if self.players[i].path: last_bounding_box = self.players[i].path.pop()
            if self.players[i].bounding_box in self.players[0].path or self.players[i].bounding_box in self.players[1].path:
                collided_players_indices.append(i)
            if last_bounding_box: self.players[i].path.append(last_bounding_box)

        if len(collided_players_indices) > 0:
            player_losses = {0: 0, 1: 0}
            for index in collided_players_indices:
                player_losses[index] += 1
            if player_losses[0] == 0:
                self.scores[0] += 1
            if player_losses[1] == 0:
                self.scores[1] += 1

            self.players = self.players_generator()

    def drawObjects(self):
        for i in range(2):
            # draw and move player, including path trail
            self.players[i].move()
            if not self.headless:
                pygame.draw.rect(self.screen, self.players[i].color, self.players[i].bounding_box, 0)
                for path_bit in self.players[i].path:
                    pygame.draw.rect(self.screen, self.players[i].color, path_bit)

        # draw walls
        for wall in self.walls:
            pygame.draw.rect(self.screen, (42, 42, 42), wall, 0)

        # draw score
        score_text = self.font.render('{0} : {1}'.format(self.scores[0], self.scores[1]), 1, (255, 153, 51))
        score_text_pos = score_text.get_rect()
        score_text_pos.centerx = int(self.width / 2)
        score_text_pos.centery = int(self.offset / 2)
        self.screen.blit(score_text, score_text_pos)
        
    def run(self):
        running = True

        while running:
            self.screen.fill((0, 0, 0)) # fill black screen
            self.playersChecks()
            self.drawObjects()
            running = self.inputUpdate()
            pygame.display.flip()  # flips display
            self.clock.tick(60)  # regulates FPS

        if not self.headless:
            pygame.quit()