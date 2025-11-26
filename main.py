from _118_simloop import Game, run
from hello_agent import MyAgent as HelloAgent
from bfs_agent import BFSAgent

window_width = 1000
window_height = 900
sprite_path = None
# sprite_path = "assets/sadcat.png"  # example sprite file

if __name__ == "__main__":
    # game = Game(window_width, window_height, sprite_file=sprite_path, goal_seed=1, maze_seeds=42)
    game = Game(window_width, window_height, sprite_file=sprite_path, goal_seed=1, maze_seeds=44)
    # game = Game(window_width, window_height, sprite_file=sprite_path, goal_seed=1, maze_seeds=513)

    print("Choose your agent:")
    print("1: Human control")
    print("2: Simple agent (moves bottom-right)")
    print("3: BFS agent (finds shortest path)")
    choice = input("Enter your choice (1-3): ")
    print(game.walls)
    # quit()
    if choice == "1":
        run(game)  # human-controlled
    elif choice == "2":
        agent = HelloAgent()
        run(game, agent)  # simple agent
    elif choice == "3":
        agent = BFSAgent()
        run(game, agent)  # BFS pathfinding agent
    else:
        print("Invalid choice. Running human control by default.")
        run(game)
