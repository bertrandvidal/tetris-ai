import pygame
import random
from enum import Enum

colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]


class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


class Tetris:
    level = 2
    score = 0
    state = "start"
    field = []
    height = 0
    width = 0
    x = 100
    y = 60
    zoom = 20
    figure = None

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.state = "start"
        self.field = []
        self.score = 0
        self.figure = None
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        self.figure = Figure(3, 0)

    def gameover(self):
        self.state = "gameover"

    def is_done(self):
        return self.state == "gameover"

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if (
                        i + self.figure.y > self.height - 1
                        or j + self.figure.x > self.width - 1
                        or j + self.figure.x < 0
                        or self.field[i + self.figure.y][j + self.figure.x] > 0
                    ):
                        intersection = True
        return intersection

    def break_lines(self):
        lines = 0
        self.score = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score = lines

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.gameover()

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation


class TetrisDrawer(object):
    """Hold all the logic to render a game of Tetris
    """

    INITIALIZED = None
    FPS = 25
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)

    size = (400, 500)
    screen = None
    score_font = None
    game_over_font = None
    clock = None

    def __init__(self):
        self.screen = None
        self.clock = None
        self.score_font = None
        self.game_over_font = None

    def _setup(self):
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.score_font = pygame.font.SysFont("Calibri", 25, True, False)
        self.game_over_font = pygame.font.SysFont("Calibri", 65, True, False)

    def _load_pygame(self):
        pygame.init()
        pygame.display.set_caption("Tetris-Now With AI!")

    def close(self):
        pygame.quit()

    def render(self, game, info=None):
        if TetrisDrawer.INITIALIZED is None:
            self._load_pygame()
            TetrisDrawer.INITIALIZED = True
        if self.screen is None:
            self._setup()
        self.clear_screen()
        self.render_grid_and_pieces(game)
        self.render_current_piece(game)
        self.render_info(info or "")
        if game.is_done():
            self.render_game_over()
        pygame.display.flip()
        self.clock.tick(TetrisDrawer.FPS)

    def clear_screen(self):
        self.screen.fill(TetrisDrawer.WHITE)

    def render_grid_and_pieces(self, game):
        for i in range(game.height):
            for j in range(game.width):
                pygame.draw.rect(
                    self.screen,
                    TetrisDrawer.GRAY,
                    [
                        game.x + game.zoom * j,
                        game.y + game.zoom * i,
                        game.zoom,
                        game.zoom,
                    ],
                    1,
                )
                if game.field[i][j] > 0:
                    pygame.draw.rect(
                        self.screen,
                        colors[game.field[i][j]],
                        [
                            game.x + game.zoom * j + 1,
                            game.y + game.zoom * i + 1,
                            game.zoom - 2,
                            game.zoom - 1,
                        ],
                    )

    def render_current_piece(self, game):
        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        pygame.draw.rect(
                            self.screen,
                            colors[game.figure.color],
                            [
                                game.x + game.zoom * (j + game.figure.x) + 1,
                                game.y + game.zoom * (i + game.figure.y) + 1,
                                game.zoom - 2,
                                game.zoom - 2,
                            ],
                        )

    def render_info(self, info):
        text = self.score_font.render(info, True, TetrisDrawer.BLACK)
        self.screen.blit(text, [0, 0])

    def render_game_over(self):
        text_game_over = self.game_over_font.render("Game Over :( ", True, (255, 0, 0))
        self.screen.blit(text_game_over, [10, 200])


class Actions(Enum):
    ROTATE = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3
    SPACE = 4
    QUIT = 5


class ActionDecider(object):
    action_space = None

    def __init__(self, action_space):
        self.action_space = action_space

    def get_action(self, game):
        raise NotImplementedError


class RandomActionDecider(ActionDecider):
    def __init__(self):
        # Randome decider shouldn't be able to quit the game
        super().__init__(
            [
                action
                for action in Actions
                if action not in [Actions.QUIT, Actions.SPACE]
            ]
        )

    def get_action(self, game):
        return [self.action_space[random.randint(0, len(self.action_space) - 1)]]


class KeyboardAction(ActionDecider):
    def __init__(self):
        super().__init__([action for action in Actions])

    def get_action(self, counter, game):
        actions = []
        # automatically go down if no input
        if counter % (TetrisDrawer.FPS // game.level // 2) == 0:
            actions.append(Actions.DOWN)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    actions.append(Actions.ROTATE)
                if event.key == pygame.K_DOWN:
                    actions.append(Actions.DOWN)
                if event.key == pygame.K_LEFT:
                    actions.append(Actions.LEFT)
                if event.key == pygame.K_RIGHT:
                    actions.append(Actions.RIGHT)
                if event.key == pygame.K_SPACE:
                    actions.append(Actions.SPACE)
                if event.key == pygame.K_ESCAPE:
                    actions = [Actions.QUIT]
        return actions


class ActionApplier(object):
    def apply_actions(self, actions, game):
        for action in actions:
            if action == Actions.ROTATE:
                game.rotate()
            if action == Actions.LEFT:
                game.go_side(-1)
            if action == Actions.RIGHT:
                game.go_side(1)
            if action == Actions.SPACE:
                game.go_space()
            if action == Actions.DOWN:
                game.go_down()
            if action == Actions.QUIT:
                # Yep we're done!!
                return True
        return False


if __name__ == "__main__":
    # Initialize the game engine
    drawer = TetrisDrawer()

    # Loop until the user clicks the close button.
    done = False
    game = Tetris(20, 10)
    counter = 0

    decider = KeyboardAction()
    applier = ActionApplier()
    drawer.render(game)

    while not done:
        if game.figure is None:
            game.new_figure()
        counter += 1
        if counter > 100000:
            counter = 0

        actions = decider.get_action(counter, game)
        done = applier.apply_actions(actions, game)
        drawer.render(game)

    clock = pygame.time.Clock()
    drawer.close()
