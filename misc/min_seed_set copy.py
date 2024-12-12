# THIS EXAMPLE IS BASED ON THE MIN SEED-SET PROBLEM FROM CHAPTER 4

import didppy as dp

# number of nutrients 
n = 4

# possible costs for actions & reactions
ac =  [0, 1]

# create model
model = dp.Model(maximize=False, float_cost=False)

# define object type
nutrient = model.add_object_type(number=n)

# defining state variables (nutrients)
nutrients = model.add_set_var(object_type=nutrient, target=[])  # create a set of all state variables

# constants - not very useful here since we only have values 0 and 1 as cost
actionCosts = model.add_int_table(ac)

# transitions
# transitions where a nutrient is added
for i in range(0, n):
    addNutrient = dp.Transition(
        name="addNutrient {}".format(i),
        cost=actionCosts[1] + dp.IntExpr.state_cost(),   # action cost + value of next state
        preconditions=[],
        effects=[
            (c1, )
        ]
    )

#transitions where a reaction is used 

# base cases
