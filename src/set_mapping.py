import didppy as dp

def mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions):
    model = dp.Model(float_cost=True)
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    strips_var = model.add_object_type(number=len(sas_task.variables.value_names))
    true_strips_vars = model.add_set_var(
        object_type=strips_var,
        target=[float(i) for i, _ in enumerate(sas_task.variables.value_names) if sas_task.init.values[i] == 0]
    )
    variable = model.add_object_type(number=len(sas_task.variables.value_names))  # used in transitions
    
    #---------------#
    #   CONSTANTS   #
    #---------------#
    action_costs = [float(action.cost) for action in sas_task.operators]
    cost_table = model.add_float_table(action_costs)
    
    # set-constants for each action
    pre_consts = []
    prev_consts = []
    effect_consts = []
    for action in sas_task.operators:
        # preconditions
        pre_const = model.create_set_const(
            object_type=variable,
            value=[var for var, pre, _, _ in action.pre_post if pre == 0]
        )
        pre_consts.append(pre_const)
        
        # prevail conditions
        prev_const = model.create_set_const(
            object_type=variable,
            value=[var for var, val in action.prevail if val == 0]
        )
        prev_consts.append(prev_const)
        
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
    model.add_base_case([true_strips_vars.issuperset(goal_const)])
    
    # ------------------#
    #    TRANSITIONS   #
    # ------------------#
    for i, action in enumerate(sas_task.operators):
        # base preconditions which need to always hold
        base_precondition = [
            true_strips_vars.issuperset(pre_consts[i]),
            true_strips_vars.issuperset(prev_consts[i])
        ]
        
        if ignore_actions:
            # additional preconditions for ignoring actions
            ignore_precondition = ~effect_consts[i].issubset(true_strips_vars)
            pre = base_precondition + [ignore_precondition]
        else:
            pre = base_precondition
        
        transition = dp.Transition(
            name=str(i) + ": " + str(action.name),
            cost=cost_table[i] + dp.FloatExpr.state_cost(),
            preconditions=pre,
            effects=[(true_strips_vars, true_strips_vars.union(effect_consts[i]))]
        )
        model.add_transition(transition)
    
    # ------------------#
    #    DUAL BOUNDS    #
    # ------------------#
    if zero_heuristic:
        model.add_dual_bound(0)
    
    if goal_heuristic:

        max_effects = max(float(len(action.pre_post)) for action in sas_task.operators) + 0.1
            
        model.add_dual_bound(
            #(dp.FloatExpr(max_effects) > 0).if_then_else(((goal_const - true_strips_vars).len() / max_effects), 0)
            (goal_const - true_strips_vars).len()/ max_effects
        )
    
    return model
