import didppy as dp
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select mapping type")
    
    parser.add_argument("domain", type=str, help="Path to the domain file")
    parser.add_argument("problem", type=str, help="Path to the problem file")
    parser.add_argument("mapping_type", choices=["int", "set"], help="Type of mapping to use")
    parser.add_argument("-zh", "--zero_heuristic", help="Use the zero heuristic", action="store_true")
    parser.add_argument("-gh", "--goal_heuristic", help="Use the goal heuristic", action="store_true")
    parser.add_argument("-t", "--track_actions", help="Use the modification which tracks actions", action="store_true")
    parser.add_argument("-i", "ignore_actions", help="Ignore actions whose effects do not add any new variable values")

    args = parser.parse_args()
    domain_file = args.domain
    problem_file = args.problem
    mapping_type = args.mapping_type
    zero_heuristic = args.zero_heuristic
    goal_heuristic = args.goal_heuristic
    track_actions = args.track_actions
    ignore_actions = args.ignore_actions
    
    sys.argv = sys.argv[:3]         # fast downward translator will complain about the args otherwise

    # choosing model
    if mapping_type == "int":
        import int_mapping
        import int_mapping_mod
        if track_actions:
            model = int_mapping_mod.mapping(domain_file, problem_file, zero_heuristic, goal_heuristic, ignore_actions)
        else:
            model = int_mapping.mapping(domain_file, problem_file, zero_heuristic, goal_heuristic, ignore_actions)
    elif mapping_type == "set":
        import set_mapping
        import set_mapping_mod
        if track_actions:
            model = set_mapping_mod.mapping(domain_file, problem_file, zero_heuristic, goal_heuristic, ignore_actions)
        else:
            model = set_mapping.mapping(domain_file, problem_file, zero_heuristic, goal_heuristic, track_actions, ignore_actions)
    
    
    # solving
    solver = dp.CAASDy(model, time_limit=300)
    solution = solver.search()

    print("Transitions to apply:")

    for t in solution.transitions:
        print(t.name)

    print("Cost: {}".format(solution.cost))
