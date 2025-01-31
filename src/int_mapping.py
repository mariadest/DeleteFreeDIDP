# Translator mapping each STRIPS variable to a DIDP variable

import sys
import os
import argparse

# Add the third_party directory to sys.path 
sys.path.append(os.path.join(os.path.dirname(__file__), "third_party"))

import third_party.pddl_parser.pddl_file as pddl_parsing
import third_party.normalize as normalize
import third_party.translate as translate
import didppy as dp


# It's assumed that all variables have 2 values -> #TODO: add check?
def mapping(domain_file, problem_file, zero_heuristic, goal_heuristic, ignore_actions):
    task = pddl_parsing.open(
        domain_filename=domain_file, task_filename=problem_file)
    
    normalize.normalize(task)
    
    # removing delete effects
    for action in task.actions:
        for index, effect in reversed(list(enumerate(action.effects))):
            if effect.literal.negated:
                del action.effects[index]
    
    
    sas_task = translate.pddl_to_sas(task)
    
    # check if task is unsolvable by checking if downward created a trivial unsolvable task
    if sas_task.goal.pairs == [(0, 1)]:
        "unsolvable task"
        return None
    
    
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
        if ignore_actions:
            transition = dp.Transition(
                name=str(i) +": " + str(action.name),
                cost = cost_table[i] + dp.IntExpr.state_cost(),
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
                cost = cost_table[i] + dp.IntExpr.state_cost(),
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

    # dual bound which expresses nr of goals not fulfilled
    if goal_heuristic:
        max_var_count = max(len({var for var, _, _ , _ in action.pre_post}) for action in sas_task.operators)
        model.add_dual_bound(
            len(sas_task.goal.pairs) - sum(
            (dypdl_vars[var] == val).if_then_else(1, 0)
            for var, val in sas_task.goal.pairs) // max_var_count)
    
    return model