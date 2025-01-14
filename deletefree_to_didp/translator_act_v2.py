# Translator mapping all STRIPS variables to a single DyPDL variable and keeping track of actions used

import sys
import os
import math

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
    actions_considered = model.add_set_var(object_type=action, target=[])
    
    strips_var = model.add_object_type(number=len(sas_task.variables.value_names))
    true_strips_vars = model.add_set_var(object_type=strips_var, target=[i for i, var in enumerate(sas_task.variables.value_names) if sas_task.init.values[i] == 0])    # used to track which strips variables have accumulated

    variable = model.add_object_type(number=len(sas_task.variables.value_names)) # used in transitions
            
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
    model.add_base_case([true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, val in sas_task.goal.pairs if val == 0]))])   
    model.add_base_case([actions_considered.contains(i) for i in range (len(sas_task.operators))], cost = math.inf)
    
    # ------------------#
    #    TRANSITIONS
    # ------------------#
    for i, action in enumerate(sas_task.operators):
        transition = dp.Transition(
            name=str(i) +": " + str(action.name),
            cost = cost_table[i] + dp.IntExpr.state_cost(),
            preconditions=[
                true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, pre, _, _ in action.pre_post if pre == 0]))
            ] + [
                true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, val in action.prevail if val == 0])) 
            ] + [
                ~actions_considered.contains(i)
            ],
            effects=[
                (true_strips_vars, true_strips_vars.union(model.create_set_const(object_type=variable, value=[var for var, _, val, _ in action.pre_post if val == 0])))
            ] + [
                (actions_considered, actions_considered.add(i))
            ]
        )
        model.add_transition(transition)

        
        # ignoring actions which don't lead to new true variables
        ignoreTransition = dp.Transition(
            name = "ignore " + str(i) +": " + str(action.name),
            cost = dp.IntExpr.state_cost(),
            preconditions=[
                ~actions_considered.contains(i)
            ] + [
                model.create_set_const(object_type = variable, value = [var for var, _, val, _ in action.pre_post if val == 0]).issubset(true_strips_vars)
            ]+ [
                ~model.create_set_const(object_type = variable, value = [var for var, _, val, _ in action.pre_post if val == 0]).issubset(true_strips_vars)
            ],
            effects=[(actions_considered, actions_considered.add(i))] 
        )
        model.add_transition(ignoreTransition)

    
    # ------------------#
    #    DUAL BOUNDS    #
    # ------------------#
    model.add_dual_bound(0)
    
    fulfilled_goals = sum(
        (true_strips_vars.contains(var)).if_then_else(1, 0)
        for var, val in sas_task.goal.pairs if val == 0
    )
    model.add_dual_bound(len(sas_task.goal.pairs) - fulfilled_goals)
    
    #-------#
    # Solver
    #-------#
    # TODO: not working correctly currently, CAASDy can't seem to solve it if we use ignore actions
    # CABS can solve it but gives wrong cost despite using correct actions
    solver = dp.CAASDy(model, time_limit=10)
    solution = solver.search()

    print("Transitions to apply:")

    for t in solution.transitions:
        print(t.name)

    print("Cost: {}".format(solution.cost))
    

if __name__ == "__main__":
    main()
