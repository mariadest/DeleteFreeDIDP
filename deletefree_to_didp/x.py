import didppy as dp
import sys

model = dp.Model()
state = model.target_state

'''test = model.add_int_table([1,2,3,4,5])
x = [4,5]
x_table = model.add_int_table(x)
a = model.add_object_type(number=10)
b = model.add_set_var(object_type=a, target=[1, 2])
c = model.add_object_type(number=10)
testiiing = model.add_object_type(number=2)
t = model.create_set_const(testiiing, value=[0, 1])'''
a = model.add_object_type(number=10)
b = model.add_set_var(object_type = a, target = [1, 2, 3])
c = model.create_set_const(object_type = a, value = [1, 2, 3])

state = model.target_state

print((c.issubset(b)).eval(state, model))
