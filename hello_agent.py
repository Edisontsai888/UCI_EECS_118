import numpy as np
from _118_agent import AgentBase


class MyAgent(AgentBase):
    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)
        # Start moving right
        self.current_direction = (1, 0)
        # For debugging
        print("Agent initialized, starting direction: right")



    def act(self, obs):
        agent_x, agent_y = obs[0], obs[1]
        hit_wall = obs[2] > 0.0


        print(
            f"Position: ({agent_x:.1f}, {agent_y:.1f}), Hit wall: {hit_wall}"
        )

        next_direction = np.random.randint(2, size=(2,)) * 2 - 1
        self.current_direction  = next_direction

        return next_direction


if __name__ == "__main__":
    agent = MyAgent()
    obs = np.array([400.0, 300.0])  # example observation
    action = agent.act(obs)
    print("Observation:", obs)
    print("Action:", action)
    print("----------------")
    print("By the way, you are running the wrong file.")
    print("Run _118_simloop.py instead.")
