import didppy as dp

n = 4
weights = [10, 20, 30, 40]
profits = [5, 25, 35, 50]
capacity = 50

model = dp.Model(maximize=True, float_cost=False)

item = model.add_object_type(number=n)
r = model.add_int_var(target=capacity)
i = model.add_element_var(object_type=item, target=0)

w = model.add_int_table(weights)
p = model.add_int_table(profits)

pack = dp.Transition(
    name="pack",
    cost=p[i] + dp.IntExpr.state_cost(),
    effects=[(r, r - w[i]), (i, i + 1)],
    preconditions=[i < n, r >= w[i]],
)
model.add_transition(pack)

ignore = dp.Transition(
    name="ignore",
    cost=dp.IntExpr.state_cost(),
    effects=[(i, i + 1)],
    preconditions=[i < n],
)
model.add_transition(ignore)

model.add_base_case([i == n])

solver = dp.ForwardRecursion(model)
solution = solver.search()

for i, t in enumerate(solution.transitions):
    if t.name == "pack":
        print("pack {}".format(i))

print("profit: {}".format(solution.cost))
