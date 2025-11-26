import numpy as np
from collections import deque
from _118_agent import AgentBase


class BFSAgent(AgentBase):
    """
    BFS-based exploration agent that:
    - explores with a BFS frontier
    - moves cell-by-cell (no diagonal moves)
    - centers within each cell before leaving
    - re-plans using a BFS path over known map
    - learns real walls after repeated collisions
    - gives up on hopeless exits after stalls
    """

    def __init__(self, seed=0, radius=20, cell_size=100, grid_width=10, grid_height=9):
        self.rng = np.random.default_rng(seed)

        # Parameters
        self.radius = radius
        self.cell_size = cell_size
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Map and navigation memory
        self.current_cell = [0, 0]
        self.visited_cells = set()
        self.discovered_walls = set()
        self.frontier = deque()

        # Movement state
        self.current_direction = np.array([0.0, 0.0])
        self.prev_direction = np.array([0.0, 0.0])

        # Goals
        self.is_going_in_cell = False
        self.is_leaving_cell = False
        self.leave_target_cell = None   # The long-term target — a frontier cell chosen by BFS that we plan to reach eventually.
        self.next_hop_cell = None       # The next step along the path toward that target — always an immediate neighbor (1-cell away).

        # Collision bookkeeping
        self.last_cell_before_move = None # The cell we were in before our last movement attempt. Used to detect collisions.
        self.last_cell_attempted = None   # The neighbor cell we tried to move into. Helps us know which direction failed.
        self.edge_fail_count = {}         # Counts how many times we failed to move from one cell to another. After 3 fails, we call that neighbor a discovered wall.
        self.fail_threshold = 3           # Number of failures before deciding a wall is real (default = 3).

        # Stall handling
        self.leave_stall_count = 0        # How long we’ve been stuck trying to reach the same neighbor.
        self.leave_stall_limit = 20       # Max stall time before giving up and replanning (default = 20 frames).

        # The sets (visited_cells, frontier, discovered_walls) describe what the robot knows about the world.
        # The cells (current_cell, leave_target_cell, next_hop_cell) describe what the robot is doing right now.
        # The counters (edge_fail_count, leave_stall_count) keep it from repeating bad attempts.


    # -------------------------------------------------------
    # Geometry helpers
    # -------------------------------------------------------

    def _pos_to_cell(self, x, y):
        """Convert world position (x,y) to cell coordinates [cx,cy]."""
        cx = int(x // self.cell_size)
        cy = int(y // self.cell_size)
        cx = max(0, min(cx, self.grid_width - 1))
        cy = max(0, min(cy, self.grid_height - 1))
        return [cx, cy]

    def _pos_in_cell(self, x, y):
        """Return local position inside cell and the cell coordinates."""
        cell = self._pos_to_cell(x, y)
        local_x = x - cell[0] * self.cell_size
        local_y = y - cell[1] * self.cell_size
        return (local_x, local_y), cell

    def _is_cell_in_bounds(self, cell):
        """Check if cell [cx,cy] is within grid bounds."""
        cx, cy = cell
        return (0 <= cx < self.grid_width) and (0 <= cy < self.grid_height)

    # -------------------------------------------------------
    # Map helpers
    # -------------------------------------------------------

    def _get_neighbors(self, cell):
        """Return 4-neighbors (in bounds) of a cell [cx, cy]."""
        x, y = cell
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        out = []
        for dx, dy in dirs:
            neigh = [x + dx, y + dy]
            if self._is_cell_in_bounds(neigh):
                out.append(neigh)
        return out

    def _queue_unvisited_neighbors(self, cell):
        """
        Add new neighbor cells to the frontier (BFS queue) if:
        - they are in bounds
        - not already visited
        - not known to be a wall
        - not already in the frontier
        """
        for neigh in self._get_neighbors(cell):
            t = tuple(neigh)
            if t in self.visited_cells:
                continue
            if t in self.discovered_walls:
                continue
            if not any((f[0], f[1]) == (neigh[0], neigh[1]) for f in self.frontier):
                self.frontier.append(neigh)

    def _pick_next_frontier_cell(self):
        """
        Return the next BFS frontier cell (the oldest viable item in frontier),
        skipping anything that has since become visited or marked a wall.
        """
        while self.frontier:
            cand = self.frontier[0]  # peek at leftmost
            t = (cand[0], cand[1])
            if t in self.visited_cells or t in self.discovered_walls:
                # throw it away and continue
                self.frontier.popleft()
                continue
            return cand
        return None

    # -------------------------------------------------------
    # Centering / alignment
    # -------------------------------------------------------

    def _close_to_margins(self, pos_in_cell):
        """
        Check if we're hugging the cell walls.
        Returns [near_left, near_right, near_top, near_bottom] (booleans).
        """
        margin = self.radius
        local_x, local_y = pos_in_cell
        near_left = local_x < margin
        near_right = local_x > self.cell_size - margin
        near_top = local_y < margin
        near_bottom = local_y > self.cell_size - margin
        return [near_left, near_right, near_top, near_bottom]

    def _center_in_cell_direction(self, pos_in_cell):
        """
        If we're too close to a wall inside the cell, nudge back toward center.
        Returns a direction np.array([dx, dy]) or None.
        """
        near_left, near_right, near_top, near_bottom = self._close_to_margins(pos_in_cell)

        move_x = 0.0
        move_y = 0.0
        if near_left:
            move_x += 1.0
        if near_right:
            move_x -= 1.0
        if near_top:
            move_y += 1.0
        if near_bottom:
            move_y -= 1.0

        if move_x != 0.0 or move_y != 0.0:
            return np.array([move_x, move_y])
        return None

    def _aligned_for_axis_move(self, x, y, dx, dy):
        """
        Corridor-centering rule:
        - If moving horizontally (dx != 0), ensure y doesn't collide with top/bottom edges.
        - If moving vertically (dy != 0), ensure x doesn't collide with left/right edges.
        """
        cell = self._pos_to_cell(x, y)
        cx, cy = cell
        start_x = cx * self.cell_size
        end_x = (cx + 1) * self.cell_size
        start_y = cy * self.cell_size
        end_y = (cy + 1) * self.cell_size

        if dx != 0 and dy == 0:
            return (y > start_y + self.radius) and (y < end_y - self.radius)
        if dy != 0 and dx == 0:
            return (x > start_x + self.radius) and (x < end_x - self.radius)
        return True  # dx=dy=0 or weird case

    # -------------------------------------------------------
    # BFS path planner for known space
    # -------------------------------------------------------

    def _compute_path_cells(self, start_cell, goal_cell):
        """
        Plan a path on known/free-ish cells (visited cells + frontier cells that aren't walls).
        Returns list of cells [start_cell, ..., goal_cell], or None if unreachable.
        """
        start_t = tuple(start_cell)
        goal_t = tuple(goal_cell)

        q = deque([start_t])
        parent = {start_t: None}

        def neighbors(c):
            cx, cy = c
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                n_t = (nx, ny)

                # must be in bounds
                if not self._is_cell_in_bounds([nx, ny]):
                    continue

                # cannot be a known wall
                if n_t in self.discovered_walls:
                    continue

                # we treat a cell as traversable if:
                #   - we have visited it before (we know it's open)
                #   OR
                #   - it is currently in the frontier (we believe it's worth exploring)
                if (n_t not in self.visited_cells
                        and n_t not in [tuple(f) for f in self.frontier]):
                    continue

                yield n_t

        found = False
        while q:
            cur = q.popleft()
            if cur == goal_t:
                found = True
                break
            for n in neighbors(cur):
                if n not in parent:
                    parent[n] = cur
                    q.append(n)

        if not found:
            return None

        # backtrack
        path = []
        cur = goal_t
        while cur is not None:
            path.append(list(cur))
            cur = parent[cur]
        path.reverse()
        return path

    # -------------------------------------------------------
    # Movement helpers
    # -------------------------------------------------------

    def _direction_toward_cell(self, from_cell, to_cell):
        """
        Return a move direction [-1,0,1] along x or y toward an adjacent cell.
        Assumes to_cell is a 4-neighbor of from_cell.
        """
        fx, fy = from_cell
        tx, ty = to_cell
        dx = np.sign(tx - fx)
        dy = np.sign(ty - fy)
        return np.array([dx, dy], dtype=float)

    def _record_failed_edge(self, from_cell, to_cell, local_x, local_y):
        """
        Called when we tried to move from `from_cell` to `to_cell`, hit a wall,
        and we are still in from_cell.
        We increment a fail counter. Only after enough fails do we mark `to_cell`
        as a wall and remove it from frontier.
        """
        key = (from_cell[0], from_cell[1], to_cell[0], to_cell[1])
        self.edge_fail_count[key] = self.edge_fail_count.get(key, 0) + 1


        if self.edge_fail_count[key] >= self.fail_threshold:
            self.discovered_walls.add(tuple(to_cell))

            # prune from frontier
            self.frontier = deque(
                f for f in self.frontier
                if (f[0], f[1]) != tuple(to_cell)
            )

            # abandon this route
            self.is_leaving_cell = False
            self.leave_target_cell = None
            self.next_hop_cell = None
            self.leave_stall_count = 0

    # -------------------------------------------------------
    # Main control loop
    # -------------------------------------------------------

    def act(self, obs):
        """
        obs is a dict:
        {
            "pos_x": float,
            "pos_y": float,
            "hit_wall": float  (1.0 if last move collided, else 0.0)
        }

        Returns np.array([dx, dy]) in {-1,0,1} (movement command).
        """
        x = float(obs["pos_x"])
        y = float(obs["pos_y"])
        hit_wall = float(obs["hit_wall"])

        self.prev_direction = self.current_direction

        # where am I now?
        (lx, ly), cell = self._pos_in_cell(x, y)
        cell_tuple = tuple(cell)
        self.current_cell = cell

        # 1. Collision handling (learning walls)
        if hit_wall and self.last_cell_before_move and self.last_cell_attempted:
            # "still in the same cell" means we didn't actually leave
            if cell_tuple == tuple(self.last_cell_before_move):
                self._record_failed_edge(
                    from_cell=self.last_cell_before_move,
                    to_cell=self.last_cell_attempted,
                    local_x=lx,
                    local_y=ly
                )

        # 2. First time in this cell? Mark visited, add neighbors to frontier,
        #    and force centering behavior.
        if cell_tuple not in self.visited_cells:
            self.visited_cells.add(cell_tuple)
            self._queue_unvisited_neighbors(cell)

            self.is_going_in_cell = True
            self.is_leaving_cell = False
            self.leave_target_cell = None
            self.next_hop_cell = None
            self.leave_stall_count = 0

        # 3. PHASE 1: Center inside the cell if needed
        if self.is_going_in_cell:
            nudge = self._center_in_cell_direction((lx, ly))
            if nudge is not None:
                self.current_direction = nudge
                return self.current_direction

            # done centering
            self.is_going_in_cell = False

        # 4. If we're walking toward a goal and we ARRIVED at the next hop,
        #    advance the path so next_hop_cell moves forward.
        if self.is_leaving_cell and (self.next_hop_cell is not None):
            if tuple(self.current_cell) == tuple(self.next_hop_cell):
                path = self._compute_path_cells(self.current_cell, self.leave_target_cell)
                if path is None or len(path) < 2:
                    # either at goal or can't continue
                    self.next_hop_cell = None
                else:
                    self.next_hop_cell = path[1]
                self.leave_stall_count = 0

        # 5. PHASE 2: If we don't currently have a route, pick a new frontier target
        if (not self.is_leaving_cell) or (self.leave_target_cell is None) or (self.next_hop_cell is None):
            target = self._pick_next_frontier_cell()

            if target is None:
                # Nowhere else to explore (frontier is exhausted)
                self.current_direction = np.array([0.0, 0.0])
                return self.current_direction

            # commit to that frontier cell as our long-term target
            self.is_leaving_cell = True
            self.leave_target_cell = target
            self.leave_stall_count = 0

            # compute a path from here to that target
            path = self._compute_path_cells(self.current_cell, self.leave_target_cell)
            if path is None or len(path) < 2:
                # give up immediately; we'll try again next frame
                self.is_leaving_cell = False
                self.leave_target_cell = None
                self.next_hop_cell = None
                self.current_direction = np.array([0.0, 0.0])
                return self.current_direction

            # first hop after current position
            self.next_hop_cell = path[1]

        # 6. PHASE 3: Move toward next_hop_cell (guaranteed neighbor)
        if self.next_hop_cell is not None:
            desired_step = self._direction_toward_cell(self.current_cell, self.next_hop_cell)

            aligned = self._aligned_for_axis_move(
                x, y,
                desired_step[0], desired_step[1]
            )

            if not aligned:
                # Try to nudge sideways toward center so we can safely move in corridor
                nudge = self._center_in_cell_direction((lx, ly))
                if nudge is not None:
                    self.current_direction = nudge
                    self.leave_stall_count += 1
                    if self.leave_stall_count > self.leave_stall_limit:
                        self.is_leaving_cell = False
                        self.leave_target_cell = None
                        self.next_hop_cell = None
                        self.leave_stall_count = 0
                    return self.current_direction

                # Can't nudge, just idle this frame
                self.current_direction = np.array([0.0, 0.0])
                self.leave_stall_count += 1
                if self.leave_stall_count > self.leave_stall_limit:
                    self.is_leaving_cell = False
                    self.leave_target_cell = None
                    self.next_hop_cell = None
                    self.leave_stall_count = 0
                return self.current_direction

            # We ARE aligned: attempt to move into next_hop_cell
            self.current_direction = desired_step

            # Bookkeeping for collision learning next frame
            self.last_cell_before_move = tuple(self.current_cell)
            self.last_cell_attempted = tuple(self.next_hop_cell)

            # Since we're actively moving, reset stall
            self.leave_stall_count = 0

            return self.current_direction

        # 7. Fallback (should only hit if next_hop_cell somehow vanished mid-frame)
        self.current_direction = np.array([0.0, 0.0])
        return self.current_direction

