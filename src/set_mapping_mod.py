import didppy as dp

def mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions):
    model = dp.Model(float_cost=True)
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    strips_var = model.add_object_type(number=len(sas_task.variables.value_names))
    true_strips_vars = model.add_set_var(
        object_type=strips_var,
        target=[i for i, _ in enumerate(sas_task.variables.value_names) 
                if sas_task.init.values[i] == 0]
    )
    
    variable = model.add_object_type(number=len(sas_task.variables.value_names))
    
    forced_action = model.add_float_var(target=-1.0)
    action = model.add_object_type(number=len(sas_task.operators))
    actions_considered = model.add_set_var(object_type=action, target=[])
    
    #---------------#
    #   CONSTANTS   #
    #---------------#
    action_costs = [op.cost for op in sas_task.operators]
    cost_table = model.add_float_table(action_costs)
    
    # set-constants for each action
    pre_consts  = []  
    prevail_consts = [] 
    effect_consts = []  
    
    for action in sas_task.operators:
        # preconditions
        pre_const = model.create_set_const(
            object_type=variable,
            value=[var for var, pre, _, _ in action.pre_post if pre == 0]
        )
        pre_consts.append(pre_const)
        
        # prevail conditions
        prevail_const = model.create_set_const(
            object_type=variable,
            value=[var for var, val in action.prevail if val == 0]
        )
        prevail_consts.append(prevail_const)
        
        # effects
        effect_const = model.create_set_const(
            object_type=variable,
            value=[var for var, _, val, _ in action.pre_post if val == 0]
        )
        effect_consts.append(effect_const)
    
    # goals
    goal_const = model.create_set_const(
        object_type=variable, 
        value=[var for var, val in sas_task.goal.pairs if val == 0]
    )
    
    #-----------------#
    #   BASE CASES    #
    #-----------------#
    model.add_base_case([
        true_strips_vars.issuperset(goal_const)
    ])
    
    # ------------------#
    #    TRANSITIONS   #
    # ------------------#
    for i, action in enumerate(sas_task.operators):
        if ignore_actions:
            force_transition = dp.Transition(
                name="forcing action nr " + str(i) + ": " + str(action.name),
                cost=dp.FloatExpr.state_cost(),  # free 
                preconditions=[
                    ~actions_considered.contains(i),
                    true_strips_vars.issuperset(pre_consts[i]),
                    true_strips_vars.issuperset(prevail_consts[i]),
                    ~effect_consts[i].issubset(true_strips_vars),
                    forced_action == -1.0
                ],
                effects=[
                    (forced_action, float(i))
                ]
            )
        else:
            force_transition = dp.Transition(
                name="forcing action nr " + str(i) + ": " + str(action.name),
                cost=dp.FloatExpr.state_cost(),
                preconditions=[
                    ~actions_considered.contains(i),
                    true_strips_vars.issuperset(pre_consts[i]),
                    true_strips_vars.issuperset(prevail_consts[i]),
                    forced_action == -1.0
                ],
                effects=[
                    (forced_action, float(i))
                ]
            )
        model.add_transition(force_transition, forced=True)
        
        # applying forced action
        use_transition = dp.Transition(
            name=str(i) + ": " + str(action.name),
            cost=cost_table[i] + dp.FloatExpr.state_cost(),
            preconditions=[
                forced_action == float(i)
            ],
            effects=[
                (true_strips_vars, true_strips_vars.union(effect_consts[i])),
                (actions_considered, actions_considered.add(i)),
                (forced_action, -1.0)
            ]
        )
        model.add_transition(use_transition)
        
        # ignoring forced action
        ignore_transition = dp.Transition(
            name="ignore " + str(i) + ": " + str(action.name),
            cost=dp.FloatExpr.state_cost(),
            preconditions=[
                forced_action == float(i)
            ],
            effects=[
                (actions_considered, actions_considered.add(i)),
                (forced_action, -1.0)
            ]
        )
        model.add_transition(ignore_transition)
    
    # ------------------#
    #    DUAL BOUNDS    #
    # ------------------#
    if zero_heuristic:
        model.add_dual_bound(0.0)
    
    if goal_heuristic:
        max_effects = max(float(len(action.pre_post)) for action in sas_task.operators) + 0.1
            
        model.add_dual_bound(
            (dp.FloatExpr(max_effects) > 0).if_then_else(((goal_const - true_strips_vars).len() / max_effects), 0)
        )
        
    return model
