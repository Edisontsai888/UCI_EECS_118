import time
from agent_base import AgentBase
from horn_kb import Fact, Rule
from kb import P, Var

class HelloAgent(AgentBase):
  def init_kb(self):
    # Map edges (undirected)
    for a,b in [("Hall","Kitchen"), ("Hall","Lab"), ("Kitchen","Pantry")]:
      self.tell_fact(P("Connected", a, b))
      self.tell_fact(P("Connected", b, a))

    # Baseline safe rooms (will be reasserted via perceive)
    for r in ["Hall","Kitchen","Lab","Pantry"]:
      self.tell_fact(P("Safe", r))

    # Logical variables
    R, R0 = Var("R"), Var("R0")
    
    self.tell_rule(P("CanGo", R),
               P("At","agent",R0),
               P("Connected",R0,R))


    # # Move if adjacent and safe
    # self.tell_rule(P("CanGo", R),
    #                P("At","agent", R0), P("Connected", R0, R), P("Safe", R))

    # # If cat is in R and reachable & safe, prefer going there
    # self.tell_rule(P("CanGo", R),
    #                P("At","cat", R), P("At","agent", R0),
    #                P("Connected", R0, R), P("Safe", R))

    # # If carrying cat, require CanCarryInto(R) (here equal to Safe(R))
    # self.tell_rule(P("CanCarryInto", R), P("Safe", R))
    # self.tell_rule(P("CanGo", R),
    #                P("At","agent", R0), P("Connected", R0, R),
    #                P("Carrying","agent","cat"), P("CanCarryInto", R))

  def perceive(self, p):
    # Dynamic facts each frame
    self.tell_fact(P("At","agent", p["agent_at"]))
    self.tell_fact(P("At","cat",   p["cat_at"]))
    if p.get("carrying_cat"): self.tell_fact(P("Carrying","agent","cat"))
    for r in ["Hall","Kitchen","Lab","Pantry"]:
      pass
      # if r not in p.get("fire_rooms", []):
      #   self.tell_fact(P("Safe", r))
      
    # Print KB for debugging, limit rate to avoid spamming
    now = time.time()
    if now - getattr(self, "_last_log", 0) > 1:
      self._last_log = now
      # Clear terminal first
      print("\033c", end="")  # ANSI escape code to clear terminal
      print("\n=== KB ===")
      dump_kb(self.kb)
   
  # [FAR] Ensure tell_fact adds only if not already present
  def tell_fact(self, atom):
    pred = atom[0]
    self.kb.facts.setdefault(pred, [])
    if not any(f.head == atom for f in self.kb.facts[pred]):
      self.kb.facts[pred].append(Fact(atom))
      

  # [FAR] Ensure tell_rule adds only if not already present
  def tell_rule(self, head, *body):
    pred = head[0]
    self.kb.rules.setdefault(pred, [])
    if not any(r.head == head and r.body == body for r in self.kb.rules[pred]):
      self.kb.rules[pred].append(Rule(head, body))

def _pp_term(t):
  return t[1] if isinstance(t, tuple) and len(t) == 2 and t[0] == 'Var' else str(t)

def _pp_atom(head_tuple):
  pred = head_tuple[0]
  args = ", ".join(_pp_term(a) for a in head_tuple[1:])
  return f"{pred}({args})"

def dump_kb(kb):
  print("\n=== FACTS ===")
  for pred, flist in kb.facts.items():
    for f in flist:
      print(" ", _pp_atom(f.head))
  print("=== RULES ===")
  for pred, rlist in kb.rules.items():
    for r in rlist:
      head = _pp_atom(r.head)
      body = " ∧ ".join(_pp_atom(b) for b in r.body)
      print(f" {head} :- {body}")

