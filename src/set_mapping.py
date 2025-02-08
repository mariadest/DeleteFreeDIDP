# Translator mapping all STRIPS variables to a single DyPDL set variable
import didppy as dp

# It's assumed that all variables have 2 values -> #TODO: add check?
def mapping(sas_task, zero_heuristic, goal_heuristic, ignore_actions):
    # NOTE: While we use 0 as the default value for negated variables, SAS+ (and therefore this translator) use 1 instead
    model = dp.Model(float_cost = True)
    
    #----------------#
    #   VARIABLES    #
    #----------------#
    strips_var = model.add_object_type(number=len(sas_task.variables.value_names))
    true_strips_vars = model.add_set_var(object_type=strips_var, target=[float(i) for i, var in enumerate(sas_task.variables.value_names) if sas_task.init.values[i] == 0])    # used to track which strips variables have accumulated

    variable = model.add_object_type(number=len(sas_task.variables.value_names)) # used in transitions
    
    #---------------#
    #   CONSTANTS   #
    #---------------#
    action_costs = []
    for action in sas_task.operators:
        action_costs.append(float(action.cost))
    cost_table = model.add_float_table(action_costs)


    #-----------------#
    #   BASE CASES    #
    #-----------------#
    model.add_base_case([true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, val in sas_task.goal.pairs if val == 0]))])   

    
    # ------------------#
    #    TRANSITIONS
    # ------------------#
    for i, action in enumerate(sas_task.operators):
        if ignore_actions:  
            transition = dp.Transition(
                name=str(i) +": " + str(action.name),
                cost = cost_table[i] + dp.FloatExpr.state_cost(),
                preconditions=[
                    true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, pre, _, _ in action.pre_post if pre == 0]))
                ] + [
                    true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, val in action.prevail if val == 0])) 
                ] + [
                    ~model.create_set_const(object_type = variable, value = [var for var, _, val, _ in action.pre_post if val == 0]).issubset(true_strips_vars)
                ],
                effects=[
                    (true_strips_vars, true_strips_vars.union(model.create_set_const(object_type=variable, value=[var for var, _, val, _ in action.pre_post if val == 0])))
                ]
            )
        else:
            transition = dp.Transition(
                name=str(i) +": " + str(action.name),
                cost = cost_table[i] + dp.FloatExpr.state_cost(),
                preconditions=[
                    true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, pre, _, _ in action.pre_post if pre == 0]))
                ] + [
                    true_strips_vars.issuperset(model.create_set_const(object_type=variable, value = [var for var, val in action.prevail if val == 0])) 
                ],
                effects=[
                    (true_strips_vars, true_strips_vars.union(model.create_set_const(object_type=variable, value=[var for var, _, val, _ in action.pre_post if val == 0])))
                ]
            )
        model.add_transition(transition)
    
    # ------------------#
    #    DUAL BOUNDS    #
    # ------------------#
    if zero_heuristic:
        model.add_dual_bound(0)
    
    if goal_heuristic:
        max_var_count = max(len({var for var, _, _, _ in action.pre_post}) for action in sas_task.operators)
        model.add_dual_bound((len(sas_task.goal.pairs) - sum(
        (true_strips_vars.contains(var)).if_then_else(1, 0)
        for var, val in sas_task.goal.pairs if val == 0)) / max_var_count)   
        
    return model
