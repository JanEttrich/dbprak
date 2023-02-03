import os
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


loop_query = """MATCH (l:Loop{time:$time}) RETURN l.global_id as id"""
junction_query = """MATCH (j:Junction{time: $time}) RETURN j.global_id, j.type"""
create_eloop_query = """MERGE (:ELoop{time: $time, id:$id, jtypes:$jtypes})"""
create_connections_query = """MERGE (:ELoop{time: $time1, id:$id1})-[:CONNECTION]-((:ELoop{time: $time2, id:$id2}))"""

final_dict = {
    "id": [],
    "time": [],
    "jtypes": [],
    "connected_loops": []
}

for ts in range(50, 10000, 50):
    print(ts)
    all_loops = run_query(loop_query, {"time": ts})
    for _, loop in all_loops.iterrows():
        final_dict["id"].append(loop["id"])
        final_dict["time"].append(ts)
        final_dict["jtypes"].append([])
        final_dict["connected_loops"].append([])

    final_df = pd.DataFrame(final_dict)
    final_df.set_index(["id", "time"], inplace=True)
    all_junctions = run_query(junction_query, {"time": ts})
    for _, junction in all_junctions.iterrows():
        loops = junction["j.global_id"].split("-")
        for loop in loops:
            loop_id = int(loop)
            jtype = junction["j.type"]
            final_df.loc[loop_id, ts]["jtypes"].append(jtype)
            final_df.loc[loop_id, ts]["connected_loops"].extend(
                [int(loop) for loop in loops if int(loop) != loop_id])

curr_time = 50
for index, row in final_df.iterrows():
    run_query(create_eloop_query, {
              "id": index["id"], "time": index["time"], "jtypes": row["jtypes"]})
    if (index["time"] != curr_time):
        curr_time = index["time"]
        print(curr_time)

for index, row in final_df.iterrows():
    for loop in row["connected_loops"]:
        run_query(create_connections_query, {
                  "id1": index["id"], "time1": index["time"], "id2": loop, "time2": index["time"]})
    if (index["time"] != curr_time):
        curr_time = index["time"]
        print(curr_time)