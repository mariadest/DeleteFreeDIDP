import didppy as dp

model = dp.Model()

obj = model.add_object_type(number=4)

var = model.add_set_var(object_type=obj, target=[])

const = model.create_set_const(object_type=obj, value=[1, 2])

state = model.target_state

var.add(1)

print(var.contains(1).eval(state, model))

