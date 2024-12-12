import didppy as dp

# Number of locations
n = 4
# Ready time
a = [0, 5, 0, 8]
# Due time
b = [100, 16, 10, 14]
# Travel time
c = [
    [0, 3, 4, 5],
    [3, 0, 5, 4],
    [4, 5, 0, 3],
    [5, 4, 3, 0],
]

model = dp.Model(maximize=False, float_cost=False)

customer = model.add_object_type(number=n)

# U
unvisited = model.add_set_var(object_type=customer, target=list(range(1, n)))
# i
location = model.add_element_var(object_type=customer, target=0)
# t (resource variable)
time = model.add_int_resource_var(target=0, less_is_better=True)

ready_time = model.add_int_table(a)
due_time = model.add_int_table(b)
travel_time = model.add_int_table(c)

for j in range(1, n):
    visit = dp.Transition(
        name="visit {}".format(j),
        cost=travel_time[location, j] + dp.IntExpr.state_cost(),
        preconditions=[unvisited.contains(j)],
        effects=[
            (unvisited, unvisited.remove(j)),
            (location, j),
            (time, dp.max(time + travel_time[location, j], ready_time[j])),
        ],
    )
    model.add_transition(visit)

return_to_depot = dp.Transition(
    name="return",
    cost=travel_time[location, 0] + dp.IntExpr.state_cost(),
    effects=[
        (location, 0),
        (time, time + travel_time[location, 0]),
    ],
    preconditions=[unvisited.is_empty(), location != 0],
)
model.add_transition(return_to_depot)

model.add_base_case([unvisited.is_empty(), location == 0])

for j in range(1, n):
    model.add_state_constr(
        ~unvisited.contains(j) | (time + travel_time[location, j] <= due_time[j])
    )

min_to = model.add_int_table(
    [min(c[k][j] for k in range(n) if k != j) for j in range(n)]
)

model.add_dual_bound(min_to[unvisited] + (location != 0).if_then_else(min_to[0], 0))

min_from = model.add_int_table(
    [min(c[j][k] for k in range(n) if k != j) for j in range(n)]
)

model.add_dual_bound(
    min_from[unvisited] + (location != 0).if_then_else(min_from[location], 0)
)

solver = dp.CABS(model)
solution = solver.search()

print("Transitions to apply:")

for t in solution.transitions:
    print(t.name)

print("Cost: {}".format(solution.cost))