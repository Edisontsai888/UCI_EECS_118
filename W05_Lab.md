# EECS 118 - Lab 5: Logical Agents and Knowledge Bases

### On Today's Lab

1. Encode world knowledge declaratively using predicates and rules.
2. Understand how inference replaces imperative `if-else` logic.
3. Observe the agent reasoning live in the simulation.


### Horn Clause Knowledge Base

A Horn clause is a disjunction of literals (predicates or their negations) with at most one positive literal. In our case, we will represent knowledge using Horn clauses in the form of rules and facts.


- The agent's behavior is driven entirely by a Horn-clause Knowledge Base (KB), not hardcoded control.
- Each predicate represents a fact about the world
  - Ex: `At(cat, Kitchen)`
- Each rule defines how new facts can be inferred
  - Ex: If a `room is connected` and `room is safe`, then `you can go there`.

In this lab, you will implement a simple Horn clause knowledge base (KB) to help an agent navigate a grid world. The agent will use the KB to infer safe paths and make decisions based on its knowledge of the environment. See `main_kb.py` and `kb.py` for the relevant code files.

---

### Environment Setup

From Canvas Homepage:

* `main_kb.py` — contains the game engine and logic inference code (no modification).
* `hello_agent.py` — where they define **facts** and **rules**.

---

### Tasks

1. **Run the simulation** and observe the agent moving toward the cat.
2. **Open `hello_agent.py`** and modify `init_kb()` to include:

   * At least **four rooms** connected as a graph.
   * A predicate like `Fire(Room)` that makes a room unsafe.
   * Rules such as:

     ```python
     self.tell_rule(P("Safe", R), P("Room", R), P("NotFire", R))
     self.tell_rule(P("CanGo", R), P("At", "agent", R0), P("Connected", R0, R), P("Safe", R))
     ```
3. **Add a new rule** that lets the agent rescue the cat only if:

   * It is in the same room, **and**
   * The room is **safe**.
4. **Test** by toggling between safe and fire rooms (already visualized).
5. *(Optional)* Add a new fact or rule that affects planning (e.g., “If carrying cat, avoid Lab.”)

---

### 🔍 Deliverables

Students submit:

* The modified `hello_agent.py`.
* A short paragraph explaining:

  * What new facts/rules they added.
  * What behavior they expected vs. observed.

---

### Extensions

* Add reasoning with intermediate predicates (e.g., `Reachable(Room)`).
* Extend to multi-step planning (`CanGo` chain reasoning).
* Display KB contents live (for debugging).


---

### Files for W05 Lab

* **main_kb.py**
  * Tiny entry point.
  * Launches the simulation by constructing `Game` and calling `run()`.

* **game_kb.py**
  * Pygame simulation (rooms graph: Hall, Kitchen, Lab, Pantry).
  * Manages state (agent room, cat room, fire rooms, carrying/not), input (AGENT↔HUMAN mode, pause/quit, WASD in HUMAN), the frame loop (`step()/render()`), and builds the **percept** dict each frame for the agent. Renders rooms/edges/agent/cat and a HUD.

* **agent_base.py**
  * Minimal agent scaffold.
  * Owns a **Horn clause KB** (`HornKB`).
  * Provides helpers: `tell_fact`, `tell_rule`, `ask_one`.
  * Default policy: if KB entails `CanGo(X)`, return action `("GO", X)`, else `("WAIT", None)`.

* **hello_kb_agent.py**
  * The concrete Lab-5 agent.
  * In `init_kb()` it declares map connectivity, baseline safety facts, and **rules** for `Reachable`, `CanGo`, and the   * carrying-cat constraint** (can only enter `Safe` rooms when carrying).
  * In `perceive(p)` it reasserts dynamic facts each frame
    * `At(agent, ·)`, `At(cat, ·)`, `Safe(r)` for non-fire rooms.
    * `Carrying(agent, cat)` if applicable.

* **`kb.py`**
  * Lightweight logic utilities:
  * term/variable constructors (`Var`, `P`),
  * `Fact`/`Rule` data types,
  * `substitute`, `unify`,
  * Simple depth-first **backchaining** (`ask`) over facts/rules. (Used for predicate/term definitions in the agent code.)

* **horn_kb.py**
  * The Horn-clause inference engine actually used by `AgentBase`.
  * Maintains indexed **facts** and **rules**, performs SLD-resolution style proving with **variable freshening**, and provides `tell()`/`ask()` plus `substitute`, `Var`, `P`.

* **W05_Lab.md**
  * This thingy.

---

### Logical Symbols Cheat Sheet

| Symbol / Function   | Technical Name           | Description                                                 |
| ------------------- | ------------------------ | ----------------------------------------------------------- |
| `P(...)`            | Predicate constructor    | Builds a **predicate expression** like `At(agent, Kitchen)` |
| `Var("X")`          | Logic variable           | Represents a universally quantified variable (X)            |
| `"At"`              | Predicate symbol         | Relation: something **is at** a location                    |
| `"Connected"`       | Predicate symbol         | Relation: two rooms are directly linked                     |
| `"CanGo"`           | Predicate symbol         | Derived predicate: the agent **can move** to a room         |
| `"Fire"` / `"Safe"` | Predicate symbols        | Properties of rooms                                         |
| `tell_fact()`       | Assertion function       | Adds a **ground fact** to the KB (no variables)             |
| `tell_rule()`       | Rule definition function | Adds a **Horn clause** to the KB (with variables)           |
| `ask_one(expr)`     | Query function           | Checks if `expr` logically follows from the KB              |
| `Horn clause`       | Type of logical sentence | `Head :- Body1 ∧ Body2 …` — used for inference              |

---

### Random Notes

| Function                           | Meaning                                                   | Example                                                            | Logical Form                                |
| ---------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------- |
| `tell_fact(expr)`                  | Adds a **fact** — always true, no conditions.             | `tell_fact(P("Connected","Hall","Kitchen"))`                       | `Connected(Hall,Kitchen)`                   |
| `tell_rule(head, body1, body2, …)` | Adds a **rule** — true *if* all body statements are true. | `tell_rule(P("CanGo",R), P("At","agent",R0), P("Connected",R0,R))` | `CanGo(R) ← At(agent,R0) ∧ Connected(R0,R)` |


* `tell_fact` → store *data*.
* `tell_rule` → store *logic*.
