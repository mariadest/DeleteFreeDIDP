# THIS EXAMPLE IS BASED ON THE MIN SEED-SET PROBLEM FROM CHAPTER 4
import math
import didppy as dp

# number of nutrients 
n = 4

# constants
k =  [0, 1]

# create model
model = dp.Model(maximize=False, float_cost=False)

#-------------------------------------#
# defining state variables (nutrients)
#-------------------------------------#
c1 = model.add_int_resource_var(target=0, less_is_better=False)
c2 = model.add_int_resource_var(target=0, less_is_better=False)
c3 = model.add_int_resource_var(target=0, less_is_better=False)
c4 = model.add_int_resource_var(target=0, less_is_better=False)

#----------------#
# constants table
#----------------#
k_table = model.add_int_table(k)

#-------------#
# transitions
#-------------#
# transitions where a single nutrient is added
add_c1 = dp.Transition(
    name = "add c1",
    cost = k_table[1] + dp.IntExpr.state_cost(),
    effects=[
        (c1, 1)
    ],
    preconditions=[c1 == 0]
) 
model.add_transition(add_c1)

add_c2 = dp.Transition(
    name = "add c2",
    cost = 1 + dp.IntExpr.state_cost(),
    preconditions=[c2 == 0],
    effects=[
        (c2, 1)
    ]
) 
model.add_transition(add_c2)

add_c3 = dp.Transition(
    name = "add c3",
    cost = 1 + dp.IntExpr.state_cost(),
    preconditions=[c3 == 0],
    effects=[
        (c3, 1)
    ]
) 
model.add_transition(add_c3)

add_c4 = dp.Transition(
    name = "add c4",
    cost = 1 + dp.IntExpr.state_cost(),
    preconditions=[c4 == 0],
    effects=[
        (c4, 1)
    ]
) 
model.add_transition(add_c4)

#transitions where a reaction is used 
r1 = dp.Transition(
    name="reaction 1",
    cost = 1 + dp.IntExpr.state_cost(),
    preconditions=[
        c1 == 1,
        c2 == 1
    ],
    effects=[
        (c3, 1)
    ],
)
model.add_transition(r1)

r2 = dp.Transition(
    name = "reaction 2",
    cost = 1 + dp.IntExpr.state_cost(),
    preconditions=[
        c3 == 1
    ],
    effects=[
        (c1, 1),
        (c4, 1)
    ],
)
model.add_transition(r2)

#------------#
# base cases
#------------#
model.add_base_case([
    c1 == 1,
    c2 == 1,
    c3 == 1,
    c4 == 1
])

#-------#
# Solver
#-------#
solver = dp.CABS(model, time_limit=2)
solution = solver.search()

print("Transitions to apply:")

for t in solution.transitions:
    print(t.name)

print("Cost: {}".format(solution.cost))