import sys
import os

# Add the third_party directory to sys.path - it won't work otherwise??
sys.path.append(os.path.join(os.path.dirname(__file__), "third_party"))

import third_party.pddl_parser.pddl_file as pddl_parsing
import third_party.options as options

def main():
    print("start")
    
    task = pddl_parsing.open(
        domain_filename=options.domain, task_filename=options.task)

    print("parsing done")
   
if __name__ == "__main__":
    main()
