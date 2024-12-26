import sys
import os

# Add the third_party directory to sys.path 
sys.path.append(os.path.join(os.path.dirname(__file__), "third_party"))

import third_party.pddl_parser.pddl_file as pddl_parsing
import third_party.options as options
import third_party.normalize as normalize
import third_party.translate as translate
import didppy as dp

# It's assumed that all variables have 2 values -> #TODO: add check?
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
    
    # building dypdl task from here on out
    # NOTE: While we use 0 as the default value for negated variables, SAS+ (and this translator) use 1 instead
    model = dp.Model()
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    initial_state = (sas_task.init.values)
    dypdl_vars = []     # store all dydpl variables for later access
    
    for i, var in enumerate(sas_task.variables.value_names):
        var = model.add_int_var(target=initial_state[i])
        dypdl_vars.append(var)
    
    state = model.target_state  # used for debugging
        
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
    model.add_base_case([dypdl_vars[var] == val for var,val in sas_task.goal.pairs])    
    
    
    # ------------------#
    #    TRANSITIONS
    # ------------------#
    for i, action in enumerate(sas_task.operators):
        transition = dp.Transition(
            name="transition {}".format(i),
            cost = cost_table[i] + dp.IntExpr.state_cost(),
            preconditions=[
                dypdl_vars[var] == preval
                for var, preval, _, _ in action.pre_post
                if preval != -1
            ],
            effects=[
                (dypdl_vars[var], val)
                for var, _, val, _ in action.pre_post
            ]
        )
        model.add_transition(transition)
    
    #-------#
    # Solver
    #-------#
    solver = dp.DBDFS(model, time_limit=30)
    solution = solver.search()

    print("Transitions to apply:")

    for t in solution.transitions:
        print(t.name)

    print("Cost: {}".format(solution.cost))

if __name__ == "__main__":
    main()
