#! /usr/bin/env python

import os
import platform
import sys
import re
from pathlib import Path
import math

from lab.experiment import Experiment
from lab.parser import Parser
from lab.environments import BaselSlurmEnvironment, LocalEnvironment
from downward.reports.absolute import AbsoluteReport
from lab.reports import geometric_mean
from lab.reports import arithmetic_mean
from lab.reports import Attribute

from downward import suites


class GeometricMeanReport(AbsoluteReport):
    def compute_aggregates(self, values):
        """Override this method to use geometric mean instead of sum."""
        '''aggregates = {}
        for key, val_list in values.items():
            # Check if values exist before computing the geometric mean
            if val_list:
                aggregates[key] = geometric_mean(val_list)
            else:
                aggregates[key] = None  # Handle empty lists safely
        return aggregates'''

    INFO_ATTRIBUTES = ["time_limit", "memory_limit", "solve_time"]
    ERROR_ATTRIBUTES = [
        "domain",
        "problem",
        "algorithm",
        "unexplained_errors",
        "error",
        "node",
    ]

memory = Attribute("memory", function=arithmetic_mean)
time_score = Attribute("time_score", function=geometric_mean)
ATTRIBUTES = [
    memory,
    time_score
]

# Check if on cluster
NODE = platform.node()
REMOTE = NODE.endswith(".scicore.unibas.ch") or NODE.endswith(".cluster.bc2.ch") or NODE.endswith("login12")

SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent
BENCHMARKS_DIR = Path(os.environ["DOWNWARD_BENCHMARKS"])

TIME_LIMIT = 900
MEMORY_LIMIT = 3584


# benchmarks
optimal_strips = ["agricola-opt18-strips", "airport", "barman-opt11-strips", "barman-opt14-strips", "blocks", "childsnack-opt14-strips", "data-network-opt18-strips", "depot", "driverlog", "elevators-opt08-strips", "elevators-opt11-strips", "floortile-opt11-strips", "floortile-opt14-strips", "freecell", "ged-opt14-strips", "grid", "gripper", "hiking-opt14-strips", "logistics00", "logistics98", "miconic", "movie", "mprime", "mystery", "nomystery-opt11-strips", "openstacks-opt08-strips", "openstacks-opt11-strips", "openstacks-opt14-strips", "openstacks-strips", "organic-synthesis-opt18-strips", "organic-synthesis-split-opt18-strips", "parcprinter-08-strips", "parcprinter-opt11-strips", "parking-opt11-strips", "parking-opt14-strips", "pathways", "pegsol-08-strips", "pegsol-opt11-strips", "petri-net-alignment-opt18-strips", "pipesworld-notankage", "pipesworld-tankage", "psr-small", "quantum-layout-opt23-strips", "rovers", "satellite", "scanalyzer-08-strips", "scanalyzer-opt11-strips", "snake-opt18-strips", "sokoban-opt08-strips", "sokoban-opt11-strips", "spider-opt18-strips", "storage", "termes-opt18-strips", "tetris-opt14-strips", "tidybot-opt11-strips", "tidybot-opt14-strips", "tpp", "transport-opt08-strips", "transport-opt11-strips", "transport-opt14-strips", "trucks-strips", "visitall-opt11-strips", "visitall-opt14-strips", "woodworking-opt08-strips", "woodworking-opt11-strips", "zenotravel"]

if REMOTE:
    ENV = BaselSlurmEnvironment(email="maria.desteffani@unibas.ch", partition="infai_2", qos="infai")
    strips_tasks =  optimal_strips
else:
    ENV = LocalEnvironment(processes=2)
    tasks = ["blocks", "miconic"]
    strips_tasks = tasks
    

ALGORITHMS = {
    "int_goal" : ["int", "-gh"],
    "set_goal" : ["set", "-gh"],
}

def make_parser():
    parser = Parser()
    parser.add_pattern("solve_time", r"solve time: (.+)s", type=float)
    parser.add_pattern("memory", r"memory used: (.+) MB", type=float)
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

    return parser


# Create the experiment
exp = Experiment(environment=ENV)
exp.add_resource("solver", REPO_DIR/"src")

exp.add_parser(make_parser())

benchmarks = suites.build_suite(BENCHMARKS_DIR, strips_tasks)

for algo, options in ALGORITHMS.items():
    strips_tasks = ["blocks"]
    benchmarks = suites.build_suite(BENCHMARKS_DIR, strips_tasks)

    for benchmark in benchmarks[:3]:        
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
        
    strips_tasks = ["miconic"]
    benchmarks = suites.build_suite(BENCHMARKS_DIR, strips_tasks)

    for benchmark in benchmarks[:3]:        
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

def remove_allocation_errors(run):
    '''pattern_allocation = re.compile(r"run.err: memory allocation of \d+ bytes failed\n")
    pattern_driver = re.compile(
        r"driver\.err: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} ERROR\s+solve finished and wrote \d+\.\d+ KiB to run\.log \(soft limit: 1024\.00 KiB\)"
    )

    if 'unexplained_errors' in run:
        run['unexplained_errors'] = [pattern_allocation.sub('', msg).strip() for msg in run['unexplained_errors']]
        run['unexplained_errors'] = [msg for msg in run['unexplained_errors'] if msg]
        
        run['unexplained_errors'] = [pattern_driver.sub('', msg).strip() for msg in run['unexplained_errors']]
        run['unexplained_errors'] = [msg for msg in run['unexplained_errors'] if msg]

    if "memory_error" not in run or run["memory_error"] is None:
        run["memory_error"] = False
        
    if "memory_allocation_error" not in run or run["memory_allocation_error"] is None:
        run["memory_allocation_error"] = 0
        
    if "finished" not in run or run["finished"] is None:
        run["finished"] = False
    
    if "time_limit_reached" not in run or run["time_limit_reached"] is None:
        run["time_limit_reached"] = False
        
    '''
    if "solve_time" in run and run["solve_time"] is not None:
        T = run["solve_time"]
        print("test")
        if T <= 1:
            run["time_score"] = 1
        elif T > TIME_LIMIT or run.get("time_limit_reached", False):
            run["time_score"] = 0
        else:
            run["time_score"] = 1 - math.log(T) / math.log(TIME_LIMIT)
    else:
        run["time_score"] = 0  # Default if solve_time is missing
        
    print("test")

    return run


    
     
exp.add_report(GeometricMeanReport(attributes = ATTRIBUTES, filter=remove_allocation_errors), outfile="time_score_report.html")

#exp.add_report(report, outfile="report.html")
exp.run_steps()
