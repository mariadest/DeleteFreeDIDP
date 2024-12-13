import sys
import os

# Add the third_party directory to sys.path 
sys.path.append(os.path.join(os.path.dirname(__file__), "third_party"))

import third_party.pddl_parser.pddl_file as pddl_parsing
import third_party.options as options
import third_party.normalize as normalize
import third_party.timers as timers
import third_party.translate as translate

def main():
    print("start")
    timer = timers.Timer()
    with timers.timing("Parsing", True):
        task = pddl_parsing.open(
            domain_filename=options.domain, task_filename=options.task)

    with timers.timing("Normalizing task"):
        normalize.normalize(task)
    
    # always relaxing tasks
    for action in task.actions:
            for index, effect in reversed(list(enumerate(action.effects))):
                if effect.literal.negated:
                    del action.effects[index]
    
    sas_task = translate.pddl_to_sas(task)
    translate.dump_statistics(sas_task)

    with timers.timing("Writing output"):
        with open(options.sas_file, "w") as output_file:
            sas_task.output(output_file)
    print("Done! %s" % timer)

   
if __name__ == "__main__":
    main()

    