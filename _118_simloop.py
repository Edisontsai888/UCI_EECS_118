import pygame as pg
import numpy as np

FPS = 60


class Game:
    def __init__(self, width=1000, height=900, goal_seed=0, maze_seeds=42, sprite_file=None):
        self.W, self.H = width, height
        self.seed = goal_seed  # Store seed for goal position
        self.rng = np.random.default_rng(maze_seeds)  # Fixed seed for maze generation
        self.cell_size = 100  # Made cells bigger for wider passages
        self.grid_w = width // self.cell_size
        self.grid_h = height // self.cell_size
        self.agent_radius = 20  # Made agent slightly smaller
        self.walls = self.generate_maze()
        self.reset()
        self.sprite_file = sprite_file
        if sprite_file:
            self.sprite = pg.image.load(sprite_file)
            self.sprite = pg.transform.scale(
                self.sprite, (40, 40)
            )  # Scale sprite to match agent size
            self.rect = self.sprite.get_rect(center=(self.W // 2, self.H // 2))
        else:
            self.rect = pg.Rect(self.W // 2, self.H // 2, 40, 40)
            self.sprite = pg.Surface((40, 40), pg.SRCALPHA)
            pg.draw.circle(self.sprite, (230, 200, 60), (20, 20), self.agent_radius)

    def generate_maze(self):
        # Initialize walls matrix (False = wall, True = path)
        walls = np.zeros((self.grid_h, self.grid_w), dtype=bool)

        def carve_path(x, y):
            walls[y, x] = True  # Mark as path
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            self.rng.shuffle(directions)

            for dx, dy in directions:
                new_x, new_y = x + dx * 2, y + dy * 2
                if (
                    0 <= new_x < self.grid_w
                    and 0 <= new_y < self.grid_h
                    and not walls[new_y, new_x]
                ):
                    walls[y + dy, x + dx] = True  # Mark the path between cells
                    carve_path(new_x, new_y)

        # Start from top-left corner
        carve_path(0, 0)

        # Ensure entrance and exit are paths
        walls[0, 0] = True  # entrance
        walls[-2:, -2:] = True  # Make exit area more accessible
        return walls

    def ensure_path_to_goal(self):
        # Convert goal position to grid coordinates
        goal_grid_x = int(self.goal_x / self.cell_size)
        goal_grid_y = int(self.goal_y / self.cell_size)

        # Clear a path to the goal based on its position
        if goal_grid_x == self.grid_w - 1:  # Right side goals
            # Clear right column
            for y in range(min(goal_grid_y, self.grid_h - 1)):
                self.walls[y, -1] = True
                self.walls[y, -2] = True
        else:  # Top left goal
            # Clear top row
            for x in range(goal_grid_x + 1):
                self.walls[0, x] = True
                self.walls[1, x] = True

        # Ensure the goal location and surrounding area is clear
        self.walls[goal_grid_y, goal_grid_x] = True
        if goal_grid_y > 0:
            self.walls[goal_grid_y - 1, goal_grid_x] = True
        if goal_grid_y < self.grid_h - 1:
            self.walls[goal_grid_y + 1, goal_grid_x] = True
        if goal_grid_x > 0:
            self.walls[goal_grid_y, goal_grid_x - 1] = True
        if goal_grid_x < self.grid_w - 1:
            self.walls[goal_grid_y, goal_grid_x + 1] = True

    def reset(self):
        # Start at the entrance (top-left)
        self.x, self.y = self.cell_size / 2, self.cell_size / 2
        self.vx = self.vy = 0
        self.speed = 100  # Increased speed for faster movement

        # Use seed to determine goal position
        goal_position = self.seed % 3  # Convert seed to 0, 1, or 2

        if goal_position == 0:
            # Bottom right (original position)
            self.goal_x = self.W - self.cell_size
            self.goal_y = self.H - self.cell_size
        elif goal_position == 1:
            # Right side center
            self.goal_x = self.W - int(self.cell_size * 1.5)
            self.goal_y = self.cell_size / 2
        else:
            # Top center at the end of a path
            self.goal_x = self.W / 2 - self.cell_size / 2
            self.goal_y = self.cell_size / 2

        self.won = False
        self.collided = False

    def has_reached_goal(self):
        dist_to_goal = np.sqrt(
            (self.x - self.goal_x) ** 2 + (self.y - self.goal_y) ** 2
        )
        self.won = dist_to_goal < 50  # Within 40 pixels of goal center
        return self.won

    def observe(self):

        return {
            "pos_x": self.x,
            "pos_y": self.y,  # agent position
            "hit_wall": self.collided ,  # hit wall
        }

    def handle_events(self):
        # Human input (arrow keys)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return None
        keys = pg.key.get_pressed()
        ax = keys[pg.K_RIGHT] - keys[pg.K_LEFT]
        ay = keys[pg.K_DOWN] - keys[pg.K_UP]
        # print(f"Human action: ({ax}, {ay})")
        return np.array([ax, ay], dtype=float)

    def check_collision(self, new_x, new_y):
        # Check collision with walls considering agent radius
        eps = 1.0
        r = self.agent_radius * eps
        # Check corners of a square around the agent
        for dx in [-r, r]:
            for dy in [-r, r]:
                check_x = new_x + dx
                check_y = new_y + dy
                grid_x = int(check_x / self.cell_size)
                grid_y = int(check_y / self.cell_size)

                # Check if position is outside the grid or in a wall
                if (
                    grid_x < 0
                    or grid_x >= self.grid_w
                    or grid_y < 0
                    or grid_y >= self.grid_h
                    or not self.walls[grid_y, grid_x]
                ):  # False means wall
                    return True
        return False

    def update(self, action, dt):
        # Environment transition
        if action is None:
            return

        if self.won:  # Stop moving if won
            return

        self.vx, self.vy = self.speed * action
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        grid_x = int(new_x / self.cell_size)
        grid_y = int(new_y / self.cell_size)


        x_collision = self.check_collision(new_x, self.y)
        y_collision = self.check_collision(self.x, new_y)
        self.collided = x_collision or y_collision

        # Check collisions before updating position
        if self.collided:
            # Adjust position based on which axis collided
            if x_collision:
                if action[0] > 0:  # colliding while moving right
                    new_x = (grid_x + 1) * self.cell_size - self.agent_radius - 1
                else:
                    new_x = grid_x * self.cell_size + self.agent_radius + 1
            if y_collision:
                if action[1] > 0:  # colliding while moving down
                    new_y = (grid_y + 1) * self.cell_size - self.agent_radius - 1
                else:
                    new_y = grid_y * self.cell_size + self.agent_radius + 1
        self.x = np.clip(new_x, self.agent_radius, self.W)
        self.y = np.clip(new_y, self.agent_radius, self.H)
        if self.sprite_file:
            self.rect.center = (int(self.x), int(self.y))

        # Check if reached goal
        self.has_reached_goal()

    def render(self, screen):
        # Visualization
        screen.fill((150, 150, 150))  # Light gray background for paths

        # Draw maze walls
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if not self.walls[y, x]:  # False means wall
                    pg.draw.rect(
                        screen,
                        (25, 25, 25),  # Dark walls
                        (
                            x * self.cell_size,
                            y * self.cell_size,
                            self.cell_size,
                            self.cell_size,
                        ),
                    )

        # Draw goal
        pg.draw.circle(
            screen, (0, 255, 0), (int(self.goal_x), int(self.goal_y)), 30
        )  # Increased radius to 30

        # Draw player
        if self.sprite_file:
            screen.blit(self.sprite, self.rect)
        else:
            pg.draw.circle(
                screen, (230, 200, 60), (int(self.x), int(self.y)), self.agent_radius
            )

        # Draw win message
        if self.won:
            font = pg.font.Font(None, 74)
            text = font.render("Goal Reached!", True, (255, 255, 0))
            text_rect = text.get_rect(center=(self.W / 2, self.H / 2))
            screen.blit(text, text_rect)


def run(game, agent=None):
    pg.init()
    screen = pg.display.set_mode((game.W, game.H))
    clock = pg.time.Clock()
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        # use agent if provided, else human input
        if agent is None:
            action = game.handle_events()
        else:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    running = False
                    break
            obs = game.observe()
            action = agent.act(obs)
        if action is None:
            running = False
            continue
        game.update(action, dt)
        game.render(screen)
        pg.display.flip()

        # Check if game is won
        if game.won:
            pg.time.wait(3000)  # Show win message for 1 second
            running = False
            print("\nCongratulations! Goal reached!")

    pg.quit()


def run_human_over_agent(game, agent):
    pg.init()
    screen = pg.display.set_mode((game.W, game.H))
    clock = pg.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # keep window responsive
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False

        human = game.handle_events()  # returns action or None on quit
        if human is None:
            break

        if (human == 0).all():
            obs = game.observe()
            action = agent.act(obs)  # no keys → agent drives
        else:
            action = human  # any key → human overrides

        game.update(action, dt)
        game.render(screen)
        pg.display.flip()
    pg.quit()


def run_blend(game, agent, alpha=0.6):
    # action = alpha*human + (1-alpha)*agent
    pg.init()
    screen = pg.display.set_mode((game.W, game.H))
    clock = pg.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False

        human = game.handle_events()
        if human is None:
            break
        obs = game.observe()
        ai = agent.act(obs)
        action = alpha * human + (1.0 - alpha) * ai
        action = np.clip(action, -1, 1)

        game.update(action, dt)
        game.render(screen)
        pg.display.flip()
    pg.quit()


# Example usage
if __name__ == "__main__":

    class RandomAgent:
        def act(self, obs):
            return np.clip(np.random.randn(2), -1, 1)

    game = Game()
    run(game)  # for human control
    run(game, RandomAgent())  # for AI control
    run_human_over_agent(game, RandomAgent())  # human overrides AI
    run_blend(game, RandomAgent(), alpha=0.7)  # blended control
