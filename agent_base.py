from horn_kb import HornKB, Fact, Rule, P, Var, substitute
class AgentBase:
  def __init__(self):
    self.kb = HornKB()
    self.init_kb()

  def init_kb(self): raise NotImplementedError
  def perceive(self, percept): pass

  def tell_fact(self, pred): self.kb.tell(Fact(pred))
  def tell_rule(self, head, *body): self.kb.tell(Rule(head, body))

  def ask_one(self, pred):
    for θ in self.kb.ask(pred): return θ
    return None

  def decide(self):
    X = Var("X")
    θ = self.ask_one(P("CanGo", X))
    if θ:
      return ("GO", substitute(X, θ))
    return ("WAIT", None)
