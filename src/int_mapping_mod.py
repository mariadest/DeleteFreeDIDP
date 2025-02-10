# Translator mapping each STRIPS variable to a DIDP variable
import didppy as dp


# It's assumed that all variables have 2 values -> #TODO: add check?
def mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions):
    # NOTE: While we use 0 as the default value for negated variables, SAS+ (and this translator) use 1 instead
    model = dp.Model(float_cost = True)
    
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    initial_state = (sas_task.init.values)
    dypdl_vars = []     # store all dydpl variables for later access
    
    for i, var in enumerate(sas_task.variables.value_names):
        var = model.add_float_var(target=initial_state[i])
        dypdl_vars.append(var)
        
    action = model.add_object_type(number=len(sas_task.operators))
    actions_considered = model.add_set_var(object_type=action, target=[])
    
    forced_action = model.add_float_var(target=-1.0)    # tracks which action is currently forced
            
                    
    #---------------#
    #   CONSTANTS   #
    #---------------#
    action_costs = []
    for action in sas_task.operators:
        action_costs.append(action.cost)
    cost_table = model.add_float_table(action_costs)
    
    
    #-----------------#
    #   BASE CASES    #
    #-----------------#
    model.add_base_case([dypdl_vars[var] == val for var,val in sas_task.goal.pairs])    
    
    
    # ------------------#
    #    TRANSITIONS
    # ------------------#
    # There is a forced transition for every action which "forces" it
    # Once "forced" an action will either be 
    #   (a): ignored
    #   (b): applied 
    # afterwards the action is marked as "considered" and cannot be forced again
    for i, action in enumerate(sas_task.operators):
        if ignore_actions:
            force_transition = dp.Transition(
                name = "forcing action nr " + str(i) + ": " + str(action.name),
                cost = dp.FloatExpr.state_cost(),     # free
                preconditions = [
                    ~actions_considered.contains(i)     # action not yet considered
                ] + [
                    dypdl_vars[pre] == val              # prevail conditions
                    for pre, val in action.prevail
                ] + [
                    dypdl_vars[pre] == val              # preconditions
                    for pre, val, _, _ in action.pre_post if val != -1
                ] + [
                    forced_action == -1     # no other action is being enforced curently
                ] + [
                    sum(
                        (dypdl_vars[var] != val).if_then_else(1, 0)
                        for var, _, val, _ in action.pre_post
                    ) > 0
                ],      
                effects = [(forced_action, i)]      # "force" action i
            )
        else:
            force_transition = dp.Transition(
                name = "forcing action nr " + str(i) + ": " + str(action.name),
                cost = dp.FloatExpr.state_cost(),     # free
                preconditions = [
                    ~actions_considered.contains(i)     # action not yet considered; technically not needed as we have forced transitions
                ] + [
                    dypdl_vars[pre] == val              # prevail conditions
                    for pre, val in action.prevail
                ] + [
                    dypdl_vars[pre] == val              # preconditions
                    for pre, val, _, _ in action.pre_post if val != -1
                ] + [
                    forced_action == -1.0     # no other action is being enforced curently
                ],      
                effects = [(forced_action, i)]      # "activate" action
            ) 
        model.add_transition(force_transition, forced=True)   # add forced transition
    
        use_transition = dp.Transition(
            name = str(i) +": " + str(action.name),
            cost = cost_table[i] + dp.FloatExpr.state_cost(),
            preconditions=[
                forced_action == i      # action needs to be marked as "forced"
            ],
            effects=[
                (dypdl_vars[var], val)
                for var, _, val, _ in action.pre_post
            ] + [
                (actions_considered, actions_considered.add(i)),
                (forced_action, -1)     # transition is no longer forced -> new action can be forced
            ]
        )
        model.add_transition(use_transition)
        
        ignore_transition = dp.Transition(
            name = "ignore " + str(i) +": " + str(action.name),
            cost = dp.FloatExpr.state_cost(),
            preconditions=[
                forced_action == i
            ],
            effects=[
                (actions_considered, actions_considered.add(i)),
                (forced_action, -1.0)     # transition is no longer forced -> new action can be forced
            ]
        )
        model.add_transition(ignore_transition)

        
    # ------------------#
    #    DUAL BOUNDS    #
    # ------------------#
    if zero_heuristic:
        model.add_dual_bound(0)     # trivial dual bound - still increases performance

    # dual bound which expresses nr of goals not fulfilled
    if goal_heuristic:
        epsilon = 0.000001
        max_effects = max(float(len(action.pre_post)) for action in sas_task.operators) 
        model.add_dual_bound(
            (sum(
            (dypdl_vars[var] != val).if_then_else(1, 0)
            for var, val in sas_task.goal.pairs)
            / max_effects) - epsilon
        )
    
    return model