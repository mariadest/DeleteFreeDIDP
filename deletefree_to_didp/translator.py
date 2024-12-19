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

    #TODO: Check if all variables have 2 values -> stop if not
    
    # building dypdl task from here on out
    model = dp.Model()
    switched = False    # checks if negated variables have value 2 instead of value 1
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    initial_state = (sas_task.init.values)  # initial state values for easy accesss
    dypdl_vars = []     # store all dydpl variables for later access
    
    # adding a new int_var for each sas variable   
    for i, var in enumerate(sas_task.variables.value_names): 
        # check if negated variable has value 1 instead of 0
        # -> need to switch values 0 and 1 for dypdl variable
        # WILL ASSUME ALL VALUES ARE SWITCHED -> TODO?
        if (var[1].startswith("Negated")):
            switched = True
            if (initial_state[i] == 1):
                var = model.add_int_var(target=0)
            else:
                var = model.add_int_var(target=1)
        else:
            var = model.add_int_var(target=initial_state[i])
        dypdl_vars.append(var) 
            
    
    #---------------#
    #   CONSTANTS   #
    #---------------#
    action_costs = []
    for action in sas_task.operators:
        action_costs.append(action.cost)
    cost_table = model.add_int_table(action_costs)
    
    
    #-----------------#
    #   BASE CASES    #
    #-----------------#
    goal_variables = []
    
    for variable, value in sas_task.goal.pairs:
        if (switched):
            if (value == 0): 
                goal_variables.append(dypdl_vars[variable])    

    #def create_conditions(variables, value):
        #return [var == value for var in variables]
    #conditions = create_conditions(goal_variables, 1)
    
    model.add_base_case([var == 1 for var in goal_variables])    
    
    # ------------------#
    #    TRANSITIONS
    # ------------------#
    # get variables for which preconditions hold and their values
    precondition_variables = []
    precondition_values = []
    for action in sas_task.operators:
        for variable, value in action.prevail:
            precondition_variables.append(dypdl_vars[variable])
            if (switched):
                if(value == 1):
                    precondition_values.append(0)
                else:
                    precondition_values.append(1)
            else:
                precondition_values.append[value]
    
    action_count = len(sas_task.operators)
    
    # add a transitions for each action
    for i in range (action_count):
        transition = dp.Transition(
            name="transition {}".format(i),
            cost = cost_table[i] + dp.IntExpr.state_cost(),
            preconditions=[
                #TODO
            ],
            effects=[
                #TODO
            ]
        )
    model.add_transition(transition)
    
    # TODO: optional state constraints & 

if __name__ == "__main__":
    main()
