import numpy as np
import pandas as pd
from neo4j import GraphDatabase
from dbconfig import *

uri = "bolt://localhost:7689"
driver = GraphDatabase.driver(uri, auth=(user, password))


def run_query(query, params):
    with driver.session() as session:
        result = session.run(query, params)
        df = pd.DataFrame(result.data())
    return df


def compute_box_constraints(p1, p2):
    """Compute 3d box constraints based on
    diagonal vector from p1 to p2.

    Args:
        p1 (point): point 1 of diagonal
        p2 (point): point 2 of diagonal

    Returns:
        constraints in order min_x, max_x, min_y, etc.
    """
    min_x = min(p1[0], p2[0])
    max_x = max(p1[0], p2[0])
    min_y = min(p1[1], p2[1])
    max_y = max(p1[1], p2[1])
    min_z = min(p1[2], p2[2])
    max_z = max(p1[2], p2[2])

    contraints = [min_x, max_x, min_y, max_y, min_z, max_z]
    return contraints


def check_same_box(p1, p2, p3, p4):
    """Check whether box defined by diagonal of p1, p2 and p3, p4 is the same.

    Args:
        p1 (point): point 1 of diagonal 1
        p2 (point): point 2 of diagonal 1
        p3 (point): point 1 of diagonal 2
        p4 (point): point 2 of diagonal 2
    """
    return compute_box_constraints(p1, p2) == compute_box_constraints(p3, p4)


def sort_by_distance(points, to, asc: True):
    """Return sorted list of points based on their euclidian distance
    to the point 'to'. Default order is ascending.

    Args:
        points (list): list of points to sort
        to (point): used for distance computation
        asc (bool): order of sorting
    """
    distances = [np.linalg.norm(to - point) for point in points]
    sorted_index = np.argsort(distances)
    if not asc:
        sorted_index = sorted_index[::-1]

    return [points[i] for i in sorted_index]  # maybe also return sorted indexes


def get_nodes_in_box(p1, p2, timestamp, where_clause: str = None):
    """Return all nodes with coordinates in the box defined by p1 and p2.

    Args:
        p1 (point): point 1 in diagonal
        p2 (point): point 2 in diagonal
        timestamp (int): timestamp in database
        where_clause (str): Add additional constraints to query

    Returns:
        Dataframe with node ids, coordinates and corresponding loop candidates
    """
    constraints = compute_box_constraints(p1, p2)

    query_nodes = f"""
    match (n:Node{{time:{timestamp}}})--(l:Loop)
    where {constraints[0]} <= n.x <= {constraints[1]}
    and {constraints[2]} <= n.y <= {constraints[3]}
    and {constraints[4]} <= n.z <= {constraints[5]}
    return n.time as timestamp,
    n.id as node_id,
    n.x as x,
    n.y as y,
    n.z as z,
    collect(distinct l.global_id) as loop_candidates
    """

    res = run_query(query_nodes, {})

    return res


def convert_df_to_points(df: pd.DataFrame):
    # TODO implement
    pass


def fit_box_to_loop(loop_gid, timestamp):
    """Fit bounding box to specified loop. Takes the extremes of the
    loop-nodes to generate the bounding box.

    Args:
        loop_gid: global loop id
        timestamp (int): timestamp in database

    Returns:
        Diagonal points and constraints of the bounding box
    """
    query_loop_nodes = f"""
    match
    (n:Node{{time:{timestamp}}})--(l:Loop{{global_id:{loop_gid}, time:{timestamp}}})
    return n.time as timestamp,
    n.id as node_id,
    n.x as x,
    n.y as y,
    n.z as z
    """

    res = run_query(query_loop_nodes, {})
    min_x, min_y, min_z = res["x", "y", "z"].min()
    max_x, max_y, max_z = res["x", "y", "z"].max()

    p1 = np.array([min_x, min_y, min_z])
    p2 = np.array([max_x, max_y, max_z])

    constraints = [min_x, max_x, min_y, max_y, min_z, max_z]
    assert compute_box_constraints(p1, p2) == constraints
    
    return p1, p2, constraints


# maybe add option to fit box to loop with densest points in coordinate space
# TODO statistics on coordinate distribution, e.g. boxplots for x,y,z, respectively


def find_loops_in_box(p1, p2, timestamp):
    """Find all loops in bounding box defined by p1 and p2.
    Based on all nodes in bounding box,

    Args:
        p1 (point): point 1 of diagonal
        p2 (point): point 2 of diagonal

    Returns:
        box_corners, contained_loops, loop_candidates
    """
    # TODO implement
    pass
    # return constraints, contained_loops, loop_candidates


def plot_bounding_box(p1, p2):
    """Plot bounding box in 3d space.
    Maybe add option to animate loops through time.

    Args:
        p1 (point): point 1 in diagonal
        p2 (point): point 2 in diagonal
    """
    # TODO implement
    pass
