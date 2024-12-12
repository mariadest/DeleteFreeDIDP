import didppy as dp

n = 4
k = [0, 1]

model = dp.Model()

c1 = model.add_int_var(target=0)
c2 = model.add_int_var(target=0)
c3 = model.add_int_var(target=0)

k_table = model.add_int_table(k)

add_c1 = dp.Transition(
    name="add c1",
    cost=k_table[1] + dp.IntExpr.state_cost(),
    preconditions=[c3==0],
    effects=[
        (c1, 1),
    ],
)
model.add_transition(add_c1)

add_c2 = dp.Transition(
    name="add c2",
    cost=k_table[1] + dp.IntExpr.state_cost(),
    preconditions=[c3==0],
    effects=[
        (c2, 1)
    ],
)
model.add_transition(add_c2)

model.add_base_case([
    c1 == 1,
    c2 == 1
])

# SOLVER
solver = dp.CABS(model, time_limit=2)
solution = solver.search()

print("Transitions to apply:")

for t in solution.transitions:
    print(t.name)

print("Cost: {}".format(solution.cost))