import sys
import os

# Add the third_party directory to sys.path 
sys.path.append(os.path.join(os.path.dirname(__file__), "third_party"))

import third_party.pddl_parser.pddl_file as pddl_parsing
import third_party.options as options
import third_party.normalize as normalize
import third_party.translate as translate
import didppy as dp


def main():
    task = pddl_parsing.open(
         domain_filename=options.domain, task_filename=options.task)
     
    normalize.normalize(task)
    
    # removing delete effects
    for action in task.actions:
        for index, effect in reversed(list(enumerate(action.effects))):
            if effect.literal.negated:
                del action.effects[index]
    
    
    sas_task = translate.pddl_to_sas(task)
    print("-------------------------------------------")
    '''for var_index, (var_range, axiom_layer, value_names) in enumerate(
        zip(sas_task.variables.ranges, sas_task.variables.axiom_layers, sas_task.variables.value_names)):
            print(f"Variable v{var_index}:")
            print(f"  Range: {var_range}")
            print(f"  Axiom Layer: {axiom_layer}")
            print(f"  Values: {', '.join(value_names)}")    '''
    # building dypdl task 
    model = dp.Model()
    
    #variables
    initial_state = (sas_task.init.values)  # initial state values
    
    # adding a new int_var for each sas variable   
    
    # takes variable name and checks whether negated is in first or second position 
    # uses 
    dypdl_vars = []
    
    for i, var in enumerate(sas_task.variables.value_names): 
        print("Variable: " + var[0] + ", " + var[1])
        print("---------------------")
        
        # check if negated variable has value 1 -> need to switch values 0 and 1 for dypdl variable
        if (var[1].startswith("Negated")):
            if (initial_state[i] == 1):
                var = model.add_int_var(target=0)
            else:
                var = model.add_int_var(target=1)
        else:
            var = model.add_int_var(target=initial_state[i])
        dypdl_vars.append(var)  # add var to the list of dydpl vars to be able to access it
            
    
    # TODO: constants
    #state_values = [0, 1]
    #state_values_table = model.add_int_table([0, 1])
    
    ''''action_costs = []
    for action in sas_task.operators:
        action_costs.append(action.cost)
    cost_table = model.add_int_table(action_costs)
        
    # TODO: base cases
    goal_variables = []
    for variable, value in sas_task.goal.pairs:
        if (value != 0):       # assuming this will always be 1 
            goal_variables.append(variable)
            print("variable: " + variable + " chont dri")
        print(f"Variable {variable} must have value {value}")'''
    
    #for variable, value in sas_task.goal.pairs:
        
        
    # TODO: transitions
    
    # TODO: optional state constraints & 

if __name__ == "__main__":
    main()
