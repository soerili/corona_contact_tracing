import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
from tqdm import tqdm

# TODO: Use Argparse to get this from the commandline
data = pd.read_csv("simulation.csv")

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
    
    # use square form of pairwise distances and add diagonal to it, to avoid self matches
    con = np.argwhere(squareform(pair_distances) + np.eye(squareform(pair_distances).shape[0]) == 0)[0]
    # derive contact and add it to contacts
    current_agent_a = current_data[current_data["agent"] == con[0]]
    current_agent_b = current_data[current_data["agent"] == con[1]]
    contact = pd.DataFrame({"agent_a": current_agent_a["agent"].item(),
                            "agent_b": current_agent_b["agent"].item(),
                            "t": t,
                            "x": current_agent_a["x"].item(),
                            "y": current_agent_a["y"].item(),
                            "agent_a_state": current_agent_a["state"].item(),
                            "agent_b_state": current_agent_b["state"].item(),},
                            index=[0])
                            # TODO: It could make sense to add the AB pair as well as the reversed BA pair. In this situation, both columns agent_a and agent_b hold all agents.
    contacts = pd.concat([contacts, contact])

# sort/create table of ids by number of contacts with infected people
# if one agent, a or b, is state==2, increase count for the other

sick_agent_a = contacts[(contacts["agent_a_state"]==2) & (contacts["agent_b_state"] != 3)]
sick_agent_b = contacts[(contacts["agent_b_state"]==2) & (contacts["agent_a_state"] != 3)]

# count all contacts towards each agent
contact_counts = [0] * number_of_agents
all_contacts_of_sicks = list(sick_agent_b["agent_a"]) + list(sick_agent_a["agent_b"])
for ac in all_contacts_of_sicks:
    contact_counts[ac] += 1

# reformat as dataframe
contact_counts = pd.DataFrame(data={"agent": range(number_of_agents),
                                    "contact_counts": contact_counts,
                                    "secondary_contact_counts": None}).sort_values(by="contact_counts",
                                                ascending=False)

print(contact_counts)


# contacts of contacts
# TODO: Use contacts to second order contact count
print("find second order contacts")
for t in tqdm(range(time_start, time_end+1)):
    secondary_contact_counts = [0] * number_of_agents
    for index, row in contact_counts.iterrows():
        current_agent = row["agent"]
        # previous contacts of current_agent have to be unknown/susceptible, otherwise we cannot infect them.
        contacts_a = contacts[(contacts["t"] <= t) & (contacts["agent_a"]==current_agent) & (contacts["agent_b_state"]<=1)]
        contacts_b = contacts[(contacts["t"] <= t) & (contacts["agent_b"]==current_agent) & (contacts["agent_a_state"]<=1)]

        
        all_secondary_contacts = list(contacts_a["agent_b"]) + list(contacts_b["agent_a"])
        for sc in all_secondary_contacts:
            secondary_contact_counts[sc] += 1
    # print(secondary_contact_counts)

# TODO: put this into a nice data frame, but this is time dependend data
# contact_counts.assign(secondary_contact_counts = pd.Series(secondary_contact_counts).values)



# IDEA: view agents as nodes and contacts as edges -> graph. Analyse graph who to limit infection