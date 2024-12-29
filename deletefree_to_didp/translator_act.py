# Translator mapping STRIPS actions to DIDP variables

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
    # NOTE: While we use 0 as the default value for negated variables, SAS+ (and therefore this translator) use 1 instead
    model = dp.Model()
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    action = model.add_object_type(number=len(sas_task.operators))  
    actions_used = model.add_set_var(object_type=action, target=[])    # starting with no actions in the set
        
    strips_var = model.add_object_type(number=len(sas_task.variables.value_names))
    true_strips_vars = model.add_set_var(object_type=strips_var, target=[i for i, var in enumerate(sas_task.variables.value_names) if sas_task.init.values[i] == 0])    # used to track which strips variables have accumulated

            
    state = model.target_state    
    
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
    model.add_base_case([true_strips_vars.contains(var) for var, val in sas_task.goal.pairs])
    
    # ------------------#
    #    TRANSITIONS
    # ------------------#
    for i, action in enumerate(sas_task.operators):
        transition = dp.Transition(
            name="transitions {}".format(i),
            cost = cost_table[i] + dp.IntExpr.state_cost(),
            preconditions=[
                true_strips_vars.contains(var) 
                for var, pre, _, _ in action.pre_post 
                if pre == 0
            ],
            effects=[
                (actions_used, actions_used.add(i))
            ] + [
                (true_strips_vars, true_strips_vars.add(var)) 
                for var, _, val, _ in action.pre_post if val == 0
            ]
        )
        model.add_transition(transition)
    
    # ------------------#
    # STATE CONSTRAINTS #
    # ------------------#
    
    
    for i, action in enumerate(sas_task.operators):
        
        # TODO: try using state constraints to enforce preconditions?
        
        
        '''needed_preconditions = [(var, pre) for var, pre, _, _ in action.pre_post if pre != -1]  # add preconditions
        needed_preconditions.append((var, val) for var, val in action.prevail) # add prevail conditions
        
        current_vars = [(var, val) for var, val in zip(range(len(sas_task.variables.value_names)), sas_task.init.values)] # add initial state variable values
        
        # add all variables values which have been added by previous actions 
        # workaround since we can't easily access the elements of a set variable -> ask on github?
        for j in range (len(sas_task.operators)):
            if actions_used.contains(j):
                current_vars.append([(var, val) for var, val in sas_task.operators[j].pre_post])
                
        
        #for j in actions_used:
            #current_vars.append([(var, val) for var, _, val, _ in sas_task.operators[j].pre_post])'''
        
        '''model.add_state_constr(            
            ~actions_used.contains(action) | ~current_vars.contains(pair) for pair in needed_preconditions
        )'''
            
    
    #-------#
    # Solver
    #-------#
    solver = dp.CAASDy(model, time_limit=30)
    solution = solver.search()

    print("Transitions to apply:")

    for t in solution.transitions:
        print(t.name)

    print("Cost: {}".format(solution.cost))

if __name__ == "__main__":
    main()
