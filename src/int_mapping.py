# Translator mapping each STRIPS variable to a DIDP variable
import didppy as dp
import math


# It's assumed that all variables have 2 values -> #TODO: add check?
def mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions):
    # NOTE: While we use 0 as the default value for negated variables, SAS+ (and this translator) use 1 instead
    model = dp.Model(float_cost = True)
    
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    initial_state = (sas_task.init.values)
    dypdl_vars = []     # store all dydpl variables for later access
    
    for i, var in enumerate(sas_task.variables.value_names):
        var = model.add_float_var(target=initial_state[i])
        dypdl_vars.append(var)
            
                    
    #---------------#
    #   CONSTANTS   #
    #---------------#
    action_costs = []
    for action in sas_task.operators:
        action_costs.append(float(action.cost))
    cost_table = model.add_float_table(action_costs)
    
    
    #-----------------#
    #   BASE CASES    #
    #-----------------#
    model.add_base_case([dypdl_vars[var] == val for var,val in sas_task.goal.pairs])    
    
    
    # ------------------#
    #    TRANSITIONS
    # ------------------#
    for i, action in enumerate(sas_task.operators):
        if ignore_actions:
            transition = dp.Transition(
                name=str(i) +": " + str(action.name),
                cost = cost_table[i] + dp.FloatExpr.state_cost(),
                preconditions=[
                    dypdl_vars[pre] == val              # prevail conditions
                    for pre, val in action.prevail
                ] + [
                    dypdl_vars[pre] == val              # preconditions
                    for pre, val, _, _ in action.pre_post if val != -1
                ] + [
                    sum(
                        (dypdl_vars[var] != val).if_then_else(1, 0)
                        for var, _, val, _ in action.pre_post
                    ) > 0
                ],
                effects=[
                    (dypdl_vars[var], val)
                    for var, _, val, _ in action.pre_post
                ]
            )
        else:
            transition = dp.Transition(
                name=str(i) +": " + str(action.name),
                cost = cost_table[i] + dp.FloatExpr.state_cost(),
                preconditions=[
                    dypdl_vars[pre] == val              # prevail conditions
                    for pre, val in action.prevail
                ] + [
                    dypdl_vars[pre] == val              # preconditions
                    for pre, val, _, _ in action.pre_post if val != -1
                ],
                effects=[
                    (dypdl_vars[var], val)
                    for var, _, val, _ in action.pre_post
                ]
            )
            
        model.add_transition(transition)
        
        
    # ------------------#
    #    DUAL BOUNDS    #
    # ------------------#
    if zero_heuristic:
        model.add_dual_bound(0)     # trivial dual bound - still increases performance

    # dual bound which expresses: # of goals not fulfilled / max effects of any action
    if goal_heuristic:
        epsilon = 0.000001
        max_effects = max(float(len(action.pre_post)) for action in sas_task.operators) 
        model.add_dual_bound(
            (sum(
            (dypdl_vars[var] != val).if_then_else(1, 0)
            for var, val in sas_task.goal.pairs)
            / max_effects) - epsilon
        )
                
    
    return model