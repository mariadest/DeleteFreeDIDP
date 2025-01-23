# Translator mapping all STRIPS variables to a single DyPDL set variable

import sys
import os

# Add the third_party directory to sys.path 
sys.path.append(os.path.join(os.path.dirname(__file__), "third_party"))

import third_party.pddl_parser.pddl_file as pddl_parsing
import third_party.normalize as normalize
import third_party.translate as translate
import didppy as dp
import math

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
    
    # building dypdl task from here on out
    # NOTE: While we use 0 as the default value for negated variables, SAS+ (and therefore this translator) use 1 instead
    model = dp.Model()
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    strips_var = model.add_object_type(number=len(sas_task.variables.value_names))
    true_strips_vars = model.add_set_var(object_type=strips_var, target=[i for i, var in enumerate(sas_task.variables.value_names) if sas_task.init.values[i] == 0])    # used to track which strips variables have accumulated

    variable = model.add_object_type(number=len(sas_task.variables.value_names)) # used in transitions
    
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
    model.add_base_case([true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, val in sas_task.goal.pairs if val == 0]))])   

    
    # ------------------#
    #    TRANSITIONS
    # ------------------#
    for i, action in enumerate(sas_task.operators):
        if ignore_actions:  
            transition = dp.Transition(
                name=str(i) +": " + str(action.name),
                cost = cost_table[i] + dp.IntExpr.state_cost(),
                preconditions=[
                    true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, pre, _, _ in action.pre_post if pre == 0]))
                ] + [
                    true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, val in action.prevail if val == 0])) 
                ] + [
                    ~model.create_set_const(object_type = variable, value = [var for var, _, val, _ in action.pre_post if val == 0]).issubset(true_strips_vars)
                ],
                effects=[
                    (true_strips_vars, true_strips_vars.union(model.create_set_const(object_type=variable, value=[var for var, _, val, _ in action.pre_post if val == 0])))
                ]
            )
        else:
            transition = dp.Transition(
                name=str(i) +": " + str(action.name),
                cost = cost_table[i] + dp.IntExpr.state_cost(),
                preconditions=[
                    true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, pre, _, _ in action.pre_post if pre == 0]))
                ] + [
                    true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, val in action.prevail if val == 0])) 
                ],
                effects=[
                    (true_strips_vars, true_strips_vars.union(model.create_set_const(object_type=variable, value=[var for var, _, val, _ in action.pre_post if val == 0])))
                ]
            )
        model.add_transition(transition)
    
    # ------------------#
    #    DUAL BOUNDS    #
    # ------------------#
    if zero_heuristic:
        model.add_dual_bound(0)
    
    if goal_heuristic:
        max_var_count = max(len({var for var, _, _, _ in action.pre_post}) for action in sas_task.operators)
        model.add_dual_bound((len(sas_task.goal.pairs) - sum(
        (true_strips_vars.contains(var)).if_then_else(1, 0)
        for var, val in sas_task.goal.pairs if val == 0)) // max_var_count)   
        
    return model
