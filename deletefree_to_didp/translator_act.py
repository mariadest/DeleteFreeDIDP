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
    
    # check which vars have value 0 and which value 1 in the initial state
    strips_0_vars_tmp = []
    strips_1_vars_tmp = []
    for i, var in enumerate(sas_task.variables.value_names):
        if sas_task.init.values[i] == 0:
            strips_0_vars_tmp.append(i)
        else:
            strips_1_vars_tmp.append(i)
    
    # ONLY FOR TESTING! REMOVE AFTERWARDS
    strips_val0 = model.add_set_var(object_type=strips_var, target=strips_0_vars_tmp)    # used to track which strips variables with val 0 have accumulated
    strips_val1 = model.add_set_var(object_type=strips_var, target=strips_1_vars_tmp)    # used to track which strips variables with val 1 have accumulated
            
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
    
    
    # ------------------#
    #    TRANSITIONS
    # ------------------#
    for i, action in enumerate(sas_task.operators):
        transition = dp.Transition(
            name="transitions {}".format(i),
            cost = cost_table[i] + dp.IntExpr.state_cost(),
            preconditions=[],
            effects=[
                (actions_used, actions_used.add(i)),
                (strips_val0, strips_val0.add(var)) for var, _, val, _ in action.pre_post if val == 0 # only for testing! remove afterwards
                (strips_val1, strips_val1.add(var)) for var, _, val, _ in action.pre_post if val == 1
            ]
        )
        model.add_transition(transition)
    
    # ------------------#
    # STATE CONSTRAINTS #
    # ------------------#
    for action in sas_task.operators:
        needed_preconditions = [(var, preval) for var, preval, _, _ in action.pre_post if preval != -1]
        
        
        '''model.add_state_constr(            
            #~actions_used.contains(action) | 
        )'''
            
    
    #-------#
    # Solver
    #-------#
    

if __name__ == "__main__":
    main()
