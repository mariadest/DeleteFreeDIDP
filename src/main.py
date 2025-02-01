import sys
import os
import argparse

import didppy as dp


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select mapping type")
    
    parser.add_argument("domain", type=str, help="Path to the domain file")
    parser.add_argument("problem", type=str, help="Path to the problem file")
    parser.add_argument("mapping_type", choices=["int", "set"], help="Type of mapping to use")
    parser.add_argument("-zh", "--zero_heuristic", help="Use the zero heuristic", action="store_true")
    parser.add_argument("-gh", "--goal_heuristic", help="Use the goal heuristic", action="store_true")
    parser.add_argument("-t", "--track_actions", help="Use the modification which forces and tracks actions", action="store_true")
    parser.add_argument("-i", "--ignore_actions", help="Add precondition which ignores actions whose effects do not add any new variable values", action="store_true")

    args = parser.parse_args()
    domain_file = args.domain
    problem_file = args.problem
    mapping_type = args.mapping_type
    zero_heuristic = args.zero_heuristic
    goal_heuristic = args.goal_heuristic
    track_actions = args.track_actions
    ignore_actions = args.ignore_actions
    
    sys.argv = sys.argv[:3]         # fast downward translator will complain about the args otherwise
    sys.path.append(os.path.join(os.path.dirname(__file__), "third_party"))

    import third_party.pddl_parser.pddl_file as pddl_parsing
    import third_party.normalize as normalize
    import third_party.translate as translate
    
    try:
        # creating sas task
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
            print(f"unsolvable: " +  str(True))
            print(f"finished: " + str(True))
        else: 
            # choose model
            if mapping_type == "int":
                import int_mapping
                import int_mapping_mod
                if track_actions:
                    model = int_mapping_mod.mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions)
                else:
                    model = int_mapping.mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions)
            elif mapping_type == "set":
                import set_mapping
                import set_mapping_mod
                if track_actions:
                    model = set_mapping_mod.mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions)
                else:
                    model = set_mapping.mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions)
        
            # solving
            solver = dp.CAASDy(model)
            solution = solver.search()

            print("Transitions to apply:")

            for t in solution.transitions:
                print(t.name)
            
            print(f"finished: " + str(True))
            print(f"cost: {solution.cost}")
            print(f"solve time: {solution.time}s")
            print(f"nodes generated: {solution.generated}")
            print(f"nodes expanded: {solution.expanded}")
            
    except MemoryError:
        print("MemoryError")
       
    finally: 
        sys.stdout.flush()  # flush output stream
