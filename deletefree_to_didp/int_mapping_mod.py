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
def mapping(domain_file, problem_file, zero_heuristic, goal_heuristic, track_actions, ignore_actions):
    task = pddl_parsing.open(
        domain_filename=domain_file, task_filename=problem_file)
    
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
        
    action = model.add_object_type(number=len(sas_task.operators))
    actions_considered = model.add_set_var(object_type=action, target=[])
            
                    
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
                    ~actions_considered.contains(i)
                ] + [
                    sum(
                        (dypdl_vars[var] != val).if_then_else(1, 0)
                        for var, _, val, _ in action.pre_post
                    ) > 0
                ],
                effects=[
                    (dypdl_vars[var], val)
                    for var, _, val, _ in action.pre_post
                ] + [
                    (actions_considered, actions_considered.add(i))
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
                ] + [
                    ~actions_considered.contains(i)
                ],
                effects=[
                    (dypdl_vars[var], val)
                    for var, _, val, _ in action.pre_post
                ] + [
                    (actions_considered, actions_considered.add(i))
                ]
            )
            
        model.add_transition(transition)
        
        ignoreTransition = dp.Transition(
            name = "ignore " + str(i) +": " + str(action.name),
            cost = dp.IntExpr.state_cost(),
            preconditions=[
                ~actions_considered.contains(i)
            ] + [
                (dypdl_vars[var] == val)
                for var, _, val, _ in action.pre_post
            ],
            effects=[(actions_considered, actions_considered.add(i))] 
        )
        model.add_transition(ignoreTransition)
        
        
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