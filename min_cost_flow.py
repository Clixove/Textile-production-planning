"""
Reference: https://developers.google.com/optimization/flow/assignment_min_cost_flow
"""
from ortools.graph.python import min_cost_flow
import pandas as pd
import numpy as np
from itertools import product


def allocate(order_id, order_weight, order_efficiency, batch_id, batch_efficiency, round_n_decimal=3):
    # Verify input.
    assert order_id.shape[0] == order_weight.shape[0] == order_efficiency.shape[0], \
        'Orders\' attributes aren\'t aligned.'
    assert batch_id.shape[0] == batch_efficiency.shape[0], \
        'Batches\' attributes aren\'t aligned.'

    # Instantiate a SimpleMinCostFlow solver.
    smcf = min_cost_flow.SimpleMinCostFlow()

    # Define the directed graph for the flow.
    n_batches = batch_id.shape[0]
    weights = np.round(order_weight).astype(int)
    round_threshold = 10 ** round_n_decimal
    benefit = order_efficiency[:, np.newaxis] * batch_efficiency
    benefit = np.round(benefit * round_threshold).astype(int)

    n_orders = order_id.shape[0]
    nodes_label = {
        'source': 0,
        'workers': range(1, 1 + n_orders),
        'tasks': range(1 + n_orders, 1 + n_orders + n_batches),
        'sink': 1 + n_orders + n_batches,
    }

    # Add each arc.
    # [1] Source -> Workers (orders)
    for i in range(n_orders):
        smcf.add_arc_with_capacity_and_unit_cost(
            tail=nodes_label['source'],
            head=nodes_label['workers'][i],
            capacity=0,
            unit_cost=0,
        )
    # [2] Workers (orders) -> Tasks (batches)
    for (i, j) in product(range(n_orders), range(n_batches)):
        smcf.add_arc_with_capacity_and_unit_cost(
            tail=nodes_label['workers'][i],
            head=nodes_label['tasks'][j],
            capacity=weights[i],
            unit_cost=- benefit[i, j],
        )
    # [3] Tasks (batches) -> Sink
    for j in range(n_batches):
        smcf.add_arc_with_capacity_and_unit_cost(
            tail=nodes_label['tasks'][j],
            head=nodes_label['sink'],
            capacity=weights.sum(),
            unit_cost=0,
        )

    # Add node supplies.
    smcf.set_node_supply(nodes_label['source'], 0)
    for i in range(n_orders):
        smcf.set_node_supply(nodes_label['workers'][i], weights[i])
    for j in range(n_batches):
        smcf.set_node_supply(nodes_label['tasks'][j], 0)
    smcf.set_node_supply(nodes_label['sink'], - weights.sum())

    # Find the minimum cost flow between node 0 and node 10.
    status = smcf.solve()
    if status != smcf.OPTIMAL:
        raise Exception(f"There was an issue with the min cost flow input. Status: {status}")

    average_efficiency = - smcf.optimal_cost() / weights.sum() / round_threshold
    plan = []
    for arc in range(smcf.num_arcs()):
        # Can ignore arcs leading out of source or into sink.
        if smcf.tail(arc) != nodes_label['source'] and smcf.head(arc) != nodes_label['sink']:
            # Arcs in the solution have a flow value of 1. Their start and end nodes
            # give an assignment of worker to task.
            worker_id = smcf.tail(arc) - 1
            task_id = smcf.head(arc) - 1 - n_orders
            if smcf.flow(arc) > 0:
                plan.append({
                    'order_id': order_id[worker_id],
                    'order_weight': weights[worker_id],
                    'allocate': smcf.flow(arc),
                    'batch_id': batch_id[task_id],
                    'efficiency': - smcf.unit_cost(arc) / round_threshold
                })
    plan = pd.DataFrame(plan)
    return average_efficiency, plan
