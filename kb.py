from collections import defaultdict, namedtuple

# Term: str for constants, ("Var", name) for variables
def Var(name): return ("Var", name)
def is_var(t): return isinstance(t, tuple) and t[0] == "Var"

# Predicate = (name, args...)
def P(name, *args): return (name, *args)

Fact  = namedtuple("Fact",  ["head"])
Rule  = namedtuple("Rule",  ["head", "body"])   # body = tuple of predicates
Clause = (Fact, Rule)

def substitute(term, θ):
  if is_var(term): return substitute(θ.get(term[1], term), θ)
  if isinstance(term, tuple): return tuple([term[0]] + [substitute(a, θ) for a in term[1:]])
  return term

def unify(x, y, θ=None):
  if θ is None: θ = {}
  x, y = substitute(x, θ), substitute(y, θ)
  if x == y: return θ
  if is_var(x): return unify_var(x, y, θ)
  if is_var(y): return unify_var(y, x, θ)
  if isinstance(x, tuple) and isinstance(y, tuple) and x[0]==y[0] and len(x)==len(y):
    for a,b in zip(x[1:], y[1:]):
      θ = unify(a, b, θ)
      if θ is None: return None
    return θ
  return None

def unify_var(v, x, θ):
  name = v[1]
  if name in θ: return unify(θ[name], x, θ)
  if occurs_check(name, x, θ): return None
  θ = dict(θ); θ[name] = x
  return θ

def occurs_check(var, x, θ):
  x = substitute(x, θ)
  if is_var(x): return x[1] == var
  if isinstance(x, tuple):
    return any(occurs_check(var, a, θ) for a in x[1:])
  return False

class HornKB:
  def __init__(self):
    self.facts = defaultdict(list)   # name -> list of Fact
    self.rules = defaultdict(list)   # name -> list of Rule bodies keyed by head name

  def tell(self, clause):
    head_name = clause.head[0]
    if isinstance(clause, Fact):
      self.facts[head_name].append(clause)
    else:
      self.rules[head_name].append(clause)

  def ask(self, goal):
    """Generator of substitutions θ making goal true."""
    yield from self._prove([goal], {})

  # SLD resolution / backward chaining over Horn clauses
  def _prove(self, goals, θ):
    if not goals:
      yield θ; return
    first, rest = goals[0], goals[1:]
    # Try match against facts
    for f in self.facts[first[0]]:
      θ1 = unify(first, f.head, dict(θ))
      if θ1 is not None:
        yield from self._prove(rest, θ1)
    # Try rules
    for r in self.rules[first[0]]:
      θ1 = unify(first, r.head, dict(θ))
      if θ1 is not None:
        new_goals = list(r.body) + rest
        yield from self._prove(new_goals, θ1)
