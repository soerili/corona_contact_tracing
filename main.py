import argparse

import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.spatial import KDTree
from tqdm import tqdm
import matplotlib.pyplot as plt

from utils import AGENT_STATES


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-dp', '--data-path', type=str, required=True,
                    help='Path to data')
args = parser.parse_args()

data_path = args.data_path

data = pd.read_csv(data_path)

# determin start and end time
time_start = data["t"].min()
time_end = data["t"].max()
number_of_agents = len(set(data["agent"]))

# create dataframe for book keeping of contacts
contacts = pd.DataFrame(columns=["agent_a", "agent_b", "t", "x", "y", "agent_a_state", "agent_b_state"])

# iterate over time
print("find all first order contacts")
for t in tqdm(range(time_start, time_end+1)):
    # filter for time and find pairwise distances
    current_data = data[data["t"]==t]
    pair_distances = pdist(current_data[["x","y"]], "euclidean")

    # wip accelerated data structure
    kdtree = KDTree(current_data[["x","y"]])
    kdtree.query_ball_point([6,10],r=.5)

    try:
        # use square form of pairwise distances and add diagonal to it, to avoid self matches
        con = np.argwhere(squareform(pair_distances) + np.eye(squareform(pair_distances).shape[0]) == 0)[0]
        # derive contact and add it to contacts
        current_agent_a = current_data[current_data["agent"] == con[0]]
        current_agent_b = current_data[current_data["agent"] == con[1]]
        contact = pd.DataFrame({"agent_a": current_agent_a["agent"].values[0],
                                "agent_b": current_agent_b["agent"].values[0],
                                "t": t,
                                "x": current_agent_a["x"].values[0], # Note: Since both agents are at the same position the
                                "y": current_agent_a["y"].values[0], #       coordinates of agent a are chosen arbitrarily here
                                "agent_a_state": current_agent_a["state"].values[0],
                                "agent_b_state": current_agent_b["state"].values[0],},
                                index=[0])
                                # TODO: It could make sense to add the AB pair as well as the reversed BA pair. In this situation, both columns agent_a and agent_b hold all agents.
        contacts = pd.concat([contacts, contact])
    except IndexError as e:
        pass

# Work in Progress!
# create matrices in numpy
beta = 0.05 # this is a guess of beta
infection_matrix = np.array([[0,0,0],[beta,0,0],[0,0,0]])

gamma = 0.04 # this is a guess of gamma
health_transition = np.array([[1,0,0],[0, 1-gamma, gamma],[0,0,1]])

# adjacency matrix from contacts
for t in tqdm(range(time_start, time_end+1)):
    adjacencies = np.array(contacts[contacts["t"] == t][["agent_a", "agent_b"]])
    adjacency_matrix = np.zeros((number_of_agents,number_of_agents))
    for adj in adjacencies:
        adjacency_matrix[adj[0],adj[1]] += 1
    # build the whole adjacency_matrix

    H = np.ndarray((number_of_agents,3))



