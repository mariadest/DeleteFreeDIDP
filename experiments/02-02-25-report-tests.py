#! /usr/bin/env python

import os
import platform
import sys
import subprocess
from pathlib import Path

from lab.experiment import Experiment
from lab.parser import Parser
from lab.environments import BaselSlurmEnvironment, LocalEnvironment
from downward.reports.absolute import AbsoluteReport
from downward.reports import  PlanningReport

from downward import suites
# Check if on cluster
NODE = platform.node()
REMOTE = NODE.endswith(".scicore.unibas.ch") or NODE.endswith(".cluster.bc2.ch")

SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent
BENCHMARKS_DIR = Path(os.environ["DOWNWARD_BENCHMARKS"])

TIME_LIMIT = 300    
MEMORY_LIMIT = 3584


# benchmarks
optimal_strips = ["agricola-opt18-strips", "airport", "barman-opt11-strips", "barman-opt14-strips", "blocks", "childsnack-opt14-strips", "data-network-opt18-strips", "depot", "driverlog", "elevators-opt08-strips", "elevators-opt11-strips", "floortile-opt11-strips", "floortile-opt14-strips", "freecell", "ged-opt14-strips", "grid", "gripper", "hiking-opt14-strips", "logistics00", "logistics98", "miconic", "movie", "mprime", "mystery", "nomystery-opt11-strips", "openstacks-opt08-strips", "openstacks-opt11-strips", "openstacks-opt14-strips", "openstacks-strips", "organic-synthesis-opt18-strips", "organic-synthesis-split-opt18-strips", "parcprinter-08-strips", "parcprinter-opt11-strips", "parking-opt11-strips", "parking-opt14-strips", "pathways", "pegsol-08-strips", "pegsol-opt11-strips", "petri-net-alignment-opt18-strips", "pipesworld-notankage", "pipesworld-tankage", "psr-small", "quantum-layout-opt23-strips", "rovers", "satellite", "scanalyzer-08-strips", "scanalyzer-opt11-strips", "snake-opt18-strips", "sokoban-opt08-strips", "sokoban-opt11-strips", "spider-opt18-strips", "storage", "termes-opt18-strips", "tetris-opt14-strips", "tidybot-opt11-strips", "tidybot-opt14-strips", "tpp", "transport-opt08-strips", "transport-opt11-strips", "transport-opt14-strips", "trucks-strips", "visitall-opt11-strips", "visitall-opt14-strips", "woodworking-opt08-strips", "woodworking-opt11-strips", "zenotravel"]

if REMOTE:
    ENV = BaselSlurmEnvironment(email="maria.desteffani@unibas.ch", partition="infai_2")
    strips_tasks = optimal_strips
else:
    ENV = LocalEnvironment(processes=2)
    tasks = ["blocks"]
    strips_tasks = tasks
    
    
ATTRIBUTES = [
    "finished",
    "unsolvable",
    "solve_time",
    "generated_nodes",
    "expanded_nodes",
    "memory_error",
    "memory"
]


ALGORITHMS = {
    "int_goal" : ["int", "-gh"],
    "int_goal_ignore" : ["int", "-gh", "-i"],
}

def make_parser():
    parser = Parser()
    parser.add_pattern("finished", r"(finished)", type=bool)
    parser.add_pattern("unsolvable", r"(Generating unsolvable task)", type=bool)
    parser.add_pattern("solve_time", r"solve time: (.+)s", type=float)
    parser.add_pattern("generated_nodes", r"nodes generated: (\d+)", type=int)
    parser.add_pattern("expanded_nodes", r"nodes expanded: (\d+)", type=int)
    parser.add_pattern("memory_error", r"(MemoryError)", type=str)
    parser.add_pattern("memory_error", r"(memory allocation of \d+ bytes failes)", type=str, file="run.err")
    parser.add_pattern("memory", r"memory used: (.+) MB", type=float)

    return parser

# Create the experiment
exp = Experiment(environment=ENV)
exp.add_resource("solver", REPO_DIR/"src")

exp.add_parser(make_parser())

# benchmarks = suites.build_suite(BENCHMARKS_DIR, strips_tasks)
benchmarks = suites.build_suite(BENCHMARKS_DIR, strips_tasks)

for algo, options in ALGORITHMS.items():
    for benchmark in benchmarks:        
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
exp.add_report(BaseReport(attributes=ATTRIBUTES), outfile="absolute.html")

    
'''class TestReport(PlanningReport):
    INFO_ATTRIBUTES = ["time_limit", "memory_limit"]
    ERROR_ATTRIBUTES = [
        "domain",
        "problem",
        "algorithm",
        "unexplained_errors",
        "error",
        "node",
    ]
exp.add_report(BaseReport(attributes=ATTRIBUTES), outfile="planning.html")'''

exp.run_steps()
