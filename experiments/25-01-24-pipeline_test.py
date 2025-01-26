#! /usr/bin/env python

import os
import platform
import sys
from pathlib import Path

from lab.experiment import Experiment
from lab.parser import Parser
from lab.environments import BaselSlurmEnvironment, LocalEnvironment
from downward.reports.absolute import AbsoluteReport

from downward import suites

class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["time_limit", "memory_limit"]
    ERROR_ATTRIBUTES = [
        "domain",
        "problem",
        "algorithm",
        "unexplained_errors",
        "error",
        "node",
    ]

# Check if on cluster
NODE = platform.node()
REMOTE = NODE.endswith(".scicore.unibas.ch") or NODE.endswith(".cluster.bc2.ch")

SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent
BENCHMARKS_DIR = Path(os.environ["DOWNWARD_BENCHMARKS"])

TIME_LIMIT = 1800
MEMORY_LIMIT = 3584

if REMOTE:
    ENV = BaselSlurmEnvironment(email="maria.desteffani@unibas.ch", partition="infai_2")
else:
    ENV = LocalEnvironment(processes=2)
    
ATTRIBUTES = [
    "cost",
    "solve_time",
    "error",
    "solver_exit_code",
]

'''ALGORITHMS = {
    "baseline_int": ["int"],
    "baseline_set": ["set"],
    "int_zero" : ["int", "-zh"],
    "set_zero" : ["set", "-zh"],
    "int_goal" : ["int" , "-gh"],
    "set_goal" : ["set", "-gh"],
    "int_zero_goal" : ["int", "-zh", "-gh"],
    "set_zero_goal" : ["set", "-zh", "-gh"],
    "int_zero_goal_ignore" : ["int", "-zh", "-gh", "-i"],
    "set_zero_goal_ignore" : ["set", "-zh", "-gh", "-i"]
}'''

ALGORITHMS = {
    "int_baseline" : ["int", "-zh"],
    "int_track" : ["int", "-zh", "-t"],
    "set_baseline" : ["set", "-zh"],
    "set_track" : ["set", "-zh", "-t"],
}

def make_parser():
    parser = Parser()
    parser.add_pattern(
        "node", 
        r"node: (.+)\n", 
        type=str, 
        file="driver.log", 
        required=True
    )
    parser.add_pattern(
        "solver_exit_code", 
        r"solve exit code: (.+)\n", 
        type=int, 
        file="driver.log"
    )
    parser.add_pattern("cost", r"cost: (\d+)", type = int)
    parser.add_pattern("solve_time", r"Solve time: (.+)s", type=float)    
    return parser

# Create the experiment
exp = Experiment(environment=ENV)
'''exp.add_resource("solver", os.path.join(SCRIPT_DIR, "main.py"))
exp.add_resource("int_mapping", os.path.join(SCRIPT_DIR, "int_mapping.py"), symlink=True)
exp.add_resource("set_mapping", os.path.join(SCRIPT_DIR, "set_mapping.py"), symlink=True)
exp.add_resource("third_party", os.path.join(SCRIPT_DIR, "third_party"), symlink=True)
exp.add_resource("int_mapping_mod", os.path.join(SCRIPT_DIR, "int_mapping_mod.py"), symlink=True)
exp.add_resource("set_mapping_mod", os.path.join(SCRIPT_DIR, "set_mapping_mod.py"), symlink=True)'''
exp.add_resource("solver", REPO_DIR/"src")

exp.add_parser(make_parser())

# all optimal_strips benchmarks
#optimal_strips = ["agricola-opt18-strips", "airport", "barman-opt11-strips", "barman-opt14-strips", "blocks", "childsnack-opt14-strips", "data-network-opt18-strips", "depot", "driverlog", "elevators-opt08-strips", "elevators-opt11-strips", "floortile-opt11-strips", "floortile-opt14-strips", "freecell", "ged-opt14-strips", "grid", "gripper", "hiking-opt14-strips", "logistics00", "logistics98", "miconic", "movie", "mprime", "mystery", "nomystery-opt11-strips", "openstacks-opt08-strips", "openstacks-opt11-strips", "openstacks-opt14-strips", "openstacks-strips", "organic-synthesis-opt18-strips", "organic-synthesis-split-opt18-strips", "parcprinter-08-strips", "parcprinter-opt11-strips", "parking-opt11-strips", "parking-opt14-strips", "pathways", "pegsol-08-strips", "pegsol-opt11-strips", "petri-net-alignment-opt18-strips", "pipesworld-notankage", "pipesworld-tankage", "psr-small", "quantum-layout-opt23-strips", "rovers", "satellite", "scanalyzer-08-strips", "scanalyzer-opt11-strips", "snake-opt18-strips", "sokoban-opt08-strips", "sokoban-opt11-strips", "spider-opt18-strips", "storage", "termes-opt18-strips", "tetris-opt14-strips", "tidybot-opt11-strips", "tidybot-opt14-strips", "tpp", "transport-opt08-strips", "transport-opt11-strips", "transport-opt14-strips", "trucks-strips", "visitall-opt11-strips", "visitall-opt14-strips", "woodworking-opt08-strips", "woodworking-opt11-strips", "zenotravel"]
strips_tasks = ["blocks"]
benchmarks = suites.build_suite(BENCHMARKS_DIR, strips_tasks)

for algo, options in ALGORITHMS.items():
    for benchmark in benchmarks[:2]:        # CHANGE BENCHMARKS HERE: currently only the first 5 blocks tasks run
        domain_file = benchmark.domain_file
        problem_file = benchmark.problem_file
        
        run = exp.add_run()
        
        run.add_resource("domain", domain_file, symlink=True)
        run.add_resource("problem", problem_file, symlink=True)
        
        run.add_command(
            "solve",
            [sys.executable, "{solver}/main.py", "{domain}", "{problem}"] + options,
            time_limit=TIME_LIMIT,
            memory_limit=MEMORY_LIMIT
        )
        
        domain = os.path.basename(os.path.dirname(domain_file))
        task_name = os.path.basename(problem_file)
        run.set_property("domain", domain)
        run.set_property("problem", task_name)
        run.set_property("algorithm", algo)
        run.set_property("options", options)
        
        run.set_property("time_limit", TIME_LIMIT)
        run.set_property("memory_limit", MEMORY_LIMIT)
        
        run.set_property("id", [algo, domain, task_name])

exp.add_step("build", exp.build)
exp.add_step("start", exp.start_runs)
exp.add_step("parse", exp.parse)
exp.add_fetcher(name="fetch")
exp.add_report(BaseReport(attributes=ATTRIBUTES), outfile="report.html")
exp.run_steps()
