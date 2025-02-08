import didppy as dp

def mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions):
    # Create the model
    model = dp.Model(float_cost =True)
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    # Object types remain unchanged.
    strips_var = model.add_object_type(number=len(sas_task.variables.value_names))
    true_strips_vars = model.add_set_var(
        object_type=strips_var,
        target=[i for i, var in enumerate(sas_task.variables.value_names) 
                if sas_task.init.values[i] == 0]
    )
    
    variable = model.add_object_type(number=len(sas_task.variables.value_names))
    
    # Instead of an integer variable, we use a continuous (real) variable.
    forced_action = model.add_float_var(target=-1.0)
    
    action = model.add_object_type(number=len(sas_task.operators))
    actions_considered = model.add_set_var(object_type=action, target=[])
    
    #---------------#
    #   CONSTANTS   #
    #---------------#
    action_costs = [op.cost for op in sas_task.operators]
    # Replace integer table with a real table
    cost_table = model.add_float_table(action_costs)
    
    #-----------------#
    #   BASE CASES    #
    #-----------------#
    model.add_base_case([
        true_strips_vars.issuperset(
            model.create_set_const(
                object_type=variable, 
                value=[var for var, val in sas_task.goal.pairs if val == 0]
            )
        )
    ])
    
    # ------------------#
    #    TRANSITIONS   #
    # ------------------#
    for i, op in enumerate(sas_task.operators):
        # In the following, note that:
        #   - cost expressions are built using dp.RealExpr.state_cost()
        #   - any check on forced_action uses -1.0 (and float(i) for comparisons)
        if ignore_actions:
            force_transition = dp.Transition(
                name="forcing action nr " + str(i) + ": " + str(op.name),
                cost=dp.FloatExpr.state_cost(),  # free cost
                preconditions=[
                    ~actions_considered.contains(i)  # action not yet considered
                ] + [
                    true_strips_vars.issuperset(
                        model.create_set_const(
                            object_type=variable, 
                            value=[var for var, pre, _, _ in op.pre_post if pre == 0]
                        )
                    )
                ] + [
                    true_strips_vars.issuperset(
                        model.create_set_const(
                            object_type=variable, 
                            value=[var for var, val in op.prevail if val == 0]
                        )
                    )
                ] + [
                    ~model.create_set_const(
                        object_type=variable, 
                        value=[var for var, _, val, _ in op.pre_post if val == 0]
                    ).issubset(true_strips_vars)
                ] + [
                    forced_action == -1.0
                ],
                effects=[
                    (forced_action, float(i))
                ]
            )
        else:
            force_transition = dp.Transition(
                name="forcing action nr " + str(i) + ": " + str(op.name),
                cost=dp.FloatExpr.state_cost(),
                preconditions=[
                    ~actions_considered.contains(i)
                ] + [
                    true_strips_vars.issuperset(
                        model.create_set_const(
                            object_type=variable, 
                            value=[var for var, pre, _, _ in op.pre_post if pre == 0]
                        )
                    )
                ] + [
                    true_strips_vars.issuperset(
                        model.create_set_const(
                            object_type=variable, 
                            value=[var for var, val in op.prevail if val == 0]
                        )
                    )
                ] + [
                    forced_action == -1.0
                ],
                effects=[
                    (forced_action, float(i))
                ]
            )
        model.add_transition(force_transition, forced=True)
        
        # Transition in which the forced action is applied.
        use_transition = dp.Transition(
            name=str(i) + ": " + str(op.name),
            cost=cost_table[i] + dp.FloatExpr.state_cost(),
            preconditions=[
                forced_action == float(i)
            ],
            effects=[
                (true_strips_vars,
                 true_strips_vars.union(
                     model.create_set_const(
                         object_type=variable, 
                         value=[var for var, _, val, _ in op.pre_post if val == 0]
                     )
                 )
                ),
                (actions_considered, actions_considered.add(i)),
                (forced_action, -1.0)
            ]
        )
        model.add_transition(use_transition)
        
        # Transition to ignore the forced action.
        ignore_transition = dp.Transition(
            name="ignore " + str(i) + ": " + str(op.name),
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
        max_var_count = max(len({var for var, _, _, _ in op.pre_post})
                            for op in sas_task.operators)
        bound_expr = (len(sas_task.goal.pairs) - sum(
            (true_strips_vars.contains(var)).if_then_else(1.0, 0.0)
            for var, val in sas_task.goal.pairs if val == 0
        )) / max_var_count
        model.add_dual_bound(bound_expr)
        
    return model
