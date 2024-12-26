import didppy as dp

# number of nutrients 
n = 4

model = dp.Model()

#-------------------------------------#
# defining state variables (nutrients)
#-------------------------------------#
dydpl_vars = []
for i in range(n):
    nutrient = model.add_int_resource_var(target=0)
    dydpl_vars.append(nutrient)

#-------------#
# transitions
#-------------#
# transitions where a single nutrient is added
for i in range(n):
    addNutrient = dp.Transition(
        name="add nutrient {}".format(i),
        cost = 1 + dp.IntExpr.state_cost(),
        preconditions=[],       # no preconditions
        effects=[
            (dydpl_vars[i], 1)    # add nutrient i 
        ]
    )
    model.add_transition(addNutrient)

#------------#
# base cases
#------------#
model.add_base_case([
    var == 1
    for var in dydpl_vars
])


#-------#
# Solver
#-------#
solver = dp.CAASDy(model, time_limit=2)
solution = solver.search()

print("Transitions to apply:")

for t in solution.transitions:
    print(t.name)

print("Cost: {}".format(solution.cost))