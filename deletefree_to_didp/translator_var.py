# Translator mapping each STRIPS variable to a DIDP variable

import sys
import os
import argparse

# Add the third_party directory to sys.path 
sys.path.append(os.path.join(os.path.dirname(__file__), "third_party"))

# used to "overwrite" argparse arguments
original_argv = sys.argv
sys.argv = sys.argv[:3]

import third_party.pddl_parser.pddl_file as pddl_parsing
import third_party.normalize as normalize
import third_party.translate as translate
import didppy as dp


sys.argv = original_argv

parser = argparse.ArgumentParser()
parser.add_argument("domainFile", help="path to domain.pddl")
parser.add_argument("problemFile", help="path to problem.pddl")
# parser.add_argument("mappingType", help="choose between using int or set variables", choices=["int", "set"])
parser.add_argument("-z", "--zeroHeuristic", help="use the zero heuristic", action="store_true")
parser.add_argument("-g", "--goalHeuristic", help="use the goal heuristic", action="store_true")

args = parser.parse_args()

# It's assumed that all variables have 2 values -> #TODO: add check?
def main():
    task = pddl_parsing.open(
        domain_filename=args.domainFile, task_filename=args.problemFile)
    
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
        
    fulfilled_goals = model.add_int_var(target = 0)     # used in the dual bound
    
    variable = model.add_object_type(number=len(sas_task.variables.value_names)) # used in transitions

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
        model.add_transition(transition)
        
        
    # ------------------#
    #    DUAL BOUNDS    #
    # ------------------#
    if args.zeroHeuristic:
        model.add_dual_bound(0)     # trivial dual bound - still increases performance

    # dual bound which expresses nr of goals not fulfilled
    if args.goalHeuristic:
        max_var_count = max(len({var for var, _, val, _ in action.pre_post}) for action in sas_task.operators)

        fulfilled_goals = sum(
            (dypdl_vars[var] == val).if_then_else(1, 0)
            for var, val in sas_task.goal.pairs
        )
        model.add_dual_bound((len(sas_task.goal.pairs) - fulfilled_goals) / max_var_count)
    
    #-------#
    # Solver
    #-------#
    solver = dp.CAASDy(model, time_limit=300)
    solution = solver.search()

    print("Transitions to apply:")

    for t in solution.transitions:
        print(t.name)

    print("Cost: {}".format(solution.cost))

if __name__ == "__main__":
    main()
