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

    tmp_obj = model.add_object_type(number=len(sas_task.variables.value_names)) # used for effects in transitions
            
    state = model.target_state    
    
    #---------------#
    #   CONSTANTS   #
    #---------------#
    action_costs = []
    for action in sas_task.operators:
        action_costs.append(action.cost)
    cost_table = model.add_int_table(action_costs)
    
    # testing - ignore
    # save the preconditions for all actions as set constants
    # ONLY SAVING PRECONDITIONS WHICH ARE POSITIVE (value 0)
    '''all_preconditions = []
    for action in sas_task.operators:
        preconditions = [var for var, pre, _, _ in action.pre_post if pre == 0]  # add preconditions
        preconditions.extend([var for var, val in action.prevail if val == 0])  # convert generator to list and extend
        all_preconditions.append(preconditions)'''



    #-----------------#
    #   BASE CASES    #
    #-----------------#
    model.add_base_case([true_strips_vars.contains(var) for var, val in sas_task.goal.pairs if val == 0])   
    
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
            ] + [
                true_strips_vars.contains(var) 
                for var, val in action.prevail
                if val == 0
            ],
            effects=[
                (actions_used, actions_used.add(i))
            ] + [
                (true_strips_vars, true_strips_vars.union(model.create_set_const(object_type=tmp_obj, value=[var for var, _, val, _ in action.pre_post if val == 0])))
            ]
        )
        model.add_transition(transition)
    
    # ------------------#
    # STATE CONSTRAINTS #
    # ------------------#
    
    
    #for i, action in enumerate(sas_task.operators):
        
        # TODO: try using state constraints to enforce preconditions?
        '''model.add_state_constr(
            true_strips_vars.issuperset(action_preconditions[i])
        )'''
            
    
    # ------------------#
    #    DUAL BOUNDS    #
    # ------------------#
    model.add_dual_bound(0)
    
    #-------#
    # Solver
    #-------#
    solver = dp.DFBB(model, time_limit=100)
    solution = solver.search()

    print("Transitions to apply:")

    for t in solution.transitions:
        print(t.name)

    print("Cost: {}".format(solution.cost))
    

if __name__ == "__main__":
    main()
