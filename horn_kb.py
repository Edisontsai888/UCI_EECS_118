from collections import defaultdict, namedtuple


# --------------------- Logic Core (Horn, SLD) ---------------------
def Var(name): return ("Var", name)
def is_var(t): return isinstance(t, tuple) and t[0] == "Var"
def P(name, *args): return (name, *args)
Fact  = namedtuple("Fact",  ["head"])
Rule  = namedtuple("Rule",  ["head", "body"])

class HornKB:
  def __init__(self):
    self.facts = defaultdict(list)
    self.rules = defaultdict(list)
    self._vcount = 0
    
  def tell(self, clause):
    head_name = clause.head[0]
    if isinstance(clause, Fact): self.facts[head_name].append(clause)
    else: self.rules[head_name].append(clause)

  def ask(self, goal):
    yield from self._prove([goal], {})

  def _prove(self, goals, θ):
    if not goals:
      yield θ; return
    first, rest = goals[0], goals[1:]

    # Facts
    for f in self.facts[first[0]]:
      θ1 = unify(first, f.head, dict(θ))
      if θ1 is not None:
        yield from self._prove(rest, θ1)

    # Rules (freshen vars per use)
    for r in self.rules[first[0]]:
      self._vcount += 1
      r2 = _freshen_clause(r, self._vcount)
      θ1 = unify(first, r2.head, dict(θ))
      if θ1 is not None:
        yield from self._prove(list(r2.body) + list(rest), θ1)


def substitute(term, θ):
  if is_var(term):
    name = term[1]
    return substitute(θ[name], θ) if name in θ else term
  if isinstance(term, tuple):
    return tuple([term[0]] + [substitute(a, θ) for a in term[1:]])
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
  if isinstance(x, tuple): return any(occurs_check(var, a, θ) for a in x[1:])
  return False

def _freshen_clause(clause, suffix):
  mapping = {}
  def f(t):
    if is_var(t):
      n = t[1]
      if n not in mapping: mapping[n] = ("Var", f"{n}_{suffix}")
      return mapping[n]
    if isinstance(t, tuple):
      return tuple([t[0]] + [f(a) for a in t[1:]])
    return t
  if isinstance(clause, Fact):
    return Fact(f(clause.head))
  else:
    return Rule(f(clause.head), tuple(f(b) for b in clause.body))
