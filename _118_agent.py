class AgentBase:
    def reset(self, obs=None):
        pass

    def act(self, obs):
        raise NotImplementedError("Implement act(obs) returning action vector")
