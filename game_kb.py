import pygame as pg
from enum import Enum
from hello_kb_agent import HelloAgent
from horn_kb import Var


FPS = 60
W, H = 800, 500

# --------------------- Game ---------------------
class RunState(Enum):
  RUNNING = 1
  PAUSED = 2
  QUIT = 3

class Mode(Enum):
  AGENT = 1
  HUMAN = 2

class Game:
  def __init__(self):
    pg.init()
    self.screen = pg.display.set_mode((W, H))
    pg.display.set_caption("EECS 118 Logical Agent Demo")
    self.clock = pg.time.Clock()
    self.font = pg.font.SysFont(None, 22)

    # World
    self.rooms = ["Hall","Kitchen","Lab","Pantry"]
    self.pos = {
      "Hall":    (360, 250),
      "Kitchen": (360, 150),
      "Lab":     (560, 250),
      "Pantry":  (560, 150),
    }
    self.edges = {("Hall","Kitchen"),("Kitchen","Hall"),
                  ("Hall","Lab"),("Lab","Hall"),
                  ("Kitchen","Pantry"),("Pantry","Kitchen")}

    # State
    self.agent_room = "Hall"
    self.cat_room   = "Kitchen"
    self.fire_rooms = set(["Lab"])   # demo: Lab on fire
    self.carrying_cat = False

    # Control
    self.state = RunState.RUNNING
    self.mode = Mode.HUMAN

    # Agent
    self.agent = HelloAgent()

  # ---------- Core loop ----------
  def run(self):
    while self.state != RunState.QUIT:
      self.handle_events(pg.event.get())
      if self.state == RunState.RUNNING:
        self.step()
      self.render()
      self.clock.tick(FPS)
    pg.quit()

  def step(self):
    # 1) Build percept
    percept = {
      "agent_at": self.agent_room,
      "cat_at": self.cat_room,
      "fire_rooms": list(self.fire_rooms),
      "carrying_cat": self.carrying_cat
    }

    # 2) Agent or Human acts
    self.agent.perceive(percept) # perceive even in human mode for KB updates
    if self.mode == Mode.AGENT:
      # self.agent.perceive(percept)
      action, target = self.agent.decide()
      if action == "GO" and target:
        self.move_agent_to(target)

    # 3) Simple terminal: pick up cat if same room
    if self.agent_room == self.cat_room and not self.carrying_cat:
      self.carrying_cat = True

  # ---------- Effects ----------
  def move_agent_to(self, dest):
    # if (self.agent_room, dest) in self.edges and dest not in self.fire_rooms:
    # [FAR] Ignoring fire should be decided by agent logic, not by the simulation (free well)
    if (self.agent_room, dest) in self.edges:
      self.agent_room = dest

  # ---------- Input ----------
  def handle_events(self, events):
    for e in events:
      if e.type == pg.QUIT: self.state = RunState.QUIT
      elif e.type == pg.KEYDOWN:
        if e.key in (pg.K_ESCAPE, pg.K_q): self.state = RunState.QUIT
        elif e.key in (pg.K_SPACE, pg.K_p):
          self.state = RunState.PAUSED if self.state == RunState.RUNNING else RunState.RUNNING
        elif e.key == pg.K_m:
          self.mode = Mode.HUMAN if self.mode == Mode.AGENT else Mode.AGENT
          
        elif self.mode == Mode.HUMAN and e.type == pg.KEYDOWN:
          dirs = {pg.K_w:(0,-1), pg.K_s:(0,1), pg.K_a:(-1,0), pg.K_d:(1,0)}
          if e.key not in dirs:
            return
          vx, vy = dirs[e.key]
          cx, cy = self.pos[self.agent_room]
          best, best_dist2 = None, float("inf")

          for (a,b) in self.edges:
            if a != self.agent_room:
              continue
            nx, ny = self.pos[b]
            dx, dy = nx-cx, ny-cy
            # must roughly be in same half-plane of that key
            if vx*dx + vy*dy <= 0:
              continue
            dist2 = dx*dx + dy*dy
            if dist2 < best_dist2:
              best, best_dist2 = b, dist2

          if best:
            self.move_agent_to(best)



        # elif self.mode == Mode.HUMAN and e.type == pg.KEYDOWN:
        #   dirs = {
        #     pg.K_w: (0, -1),  # up
        #     pg.K_s: (0,  1),  # down
        #     pg.K_a: (-1, 0),  # left
        #     pg.K_d: (1,  0),  # right
        #   }
        #   if e.key not in dirs:
        #     return

        #   vx, vy = dirs[e.key]
        #   cx, cy = self.pos[self.agent_room]
        #   best, best_score = None, 0

        #   for (a, b) in self.edges:
        #     if a != self.agent_room:
        #       continue
        #     nx, ny = self.pos[b]
        #     dx, dy = nx - cx, ny - cy
        #     dot = dx * vx + dy * vy
        #     if dot > best_score:  # most aligned neighbor in that direction
        #       best, best_score = b, dot

        #   if best:
        #     self.move_agent_to(best)

        # elif self.mode == Mode.HUMAN:
        #   nxt = None
        #   if e.key == pg.K_w: dir = "up"
        #   elif e.key == pg.K_s: dir = "down"
        #   elif e.key == pg.K_a: dir = "left"
        #   elif e.key == pg.K_d: dir = "right"
        #   else: dir = None

        #   if dir:
        #     # pick any connected room different from current
        #     for (a, b) in self.edges:
        #       if a == self.agent_room:
        #         nxt = b
        #         break
        #       if b == self.agent_room:
        #         nxt = a
        #         break

        #   if nxt:
        #     self.move_agent_to(nxt)

        # elif self.mode == Mode.HUMAN:
        #   # Human moves with WASD (graph-respecting)
        #   nxt = None
        #   if   e.key == pg.K_w: nxt = "Kitchen" if self.agent_room=="Hall" else None
        #   elif e.key == pg.K_s: nxt = "Lab"     if self.agent_room=="Hall" else None
        #   elif e.key == pg.K_d: nxt = "Pantry"  if self.agent_room=="Kitchen" else None
        #   elif e.key == pg.K_a: nxt = "Hall"    if self.agent_room in ("Kitchen","Lab") else None
        #   if nxt: self.move_agent_to(nxt)
        
        # elif self.mode == Mode.HUMAN:
        #   if e.key in (pg.K_w, pg.K_a, pg.K_s, pg.K_d):
        #     for (a, b) in self.edges:
        #       if a == self.agent_room:
        #         self.move_agent_to(b)
        #         break
        #       elif b == self.agent_room:
        #         self.move_agent_to(a)
        #         break


  # ---------- Draw ----------
  def render(self):
    self.screen.fill((18, 22, 28))
    # Edges
    for a,b in self.edges:
      ax, ay = self.pos[a]; bx, by = self.pos[b]
      pg.draw.line(self.screen, (80,80,90), (ax,ay), (bx,by), 2)
    # Rooms
    for r,(x,y) in self.pos.items():
      color = (200,70,70) if r in self.fire_rooms else (70,170,200)
      pg.draw.circle(self.screen, color, (x,y), 38, 0)
      txt = self.font.render(r, True, (10,10,10))
      self.screen.blit(txt, (x-20, y-8))
    # Agent
    ax, ay = self.pos[self.agent_room]
    pg.draw.circle(self.screen, (240,240,240), (ax, ay), 16)
    pg.draw.circle(self.screen, (30,30,30), (ax, ay), 16, 2)
    # Cat (hidden once carried)
    if not self.carrying_cat:
      cx, cy = self.pos[self.cat_room]
      pg.draw.rect(self.screen, (250,210,80), pg.Rect(cx-10, cy-10, 20, 20))
    # HUD
    hud = [
      f"Mode: {'AGENT' if self.mode==Mode.AGENT else 'HUMAN'}  (press M to toggle)",
      f"Agent: {self.agent_room}   Cat: {'with agent' if self.carrying_cat else self.cat_room}",
      "Fire: " + (", ".join(sorted(self.fire_rooms)) or "none"),
      "[SPACE] pause/resume   [Q or ESC] quit   [WASD] human moves (HUMAN mode)"
    ]
    for i, line in enumerate(hud):
      t = self.font.render(line, True, (220,220,220))
      self.screen.blit(t, (16, 16 + 22*i))
    pg.display.flip()