# Pitchers in Parks Graph (2024)

### Intro
This is another quick visualization where I created a directed graph representing all pitchers and locations they pitched in in 2024. Each team's park has a node in the graph, which is significantly larger than the nodes for players. Each edge on the graph goes from player to park, where the weight attached to the node is the number of times they appeared at that park in 2024.

### Goal
Create the visualization described above!

### Method

#### Data Retrieval
I once again used `pybaseball` Python library to get the game logs for each team in 2024. Each game log had a `PitchersUsed` field, which, with some string manipulation, I was able to convert into a Python list. This was added back to the game log data frame as its own field.

I then created a set for each team to exclude duplicate appearences, and this yielded the node list (along with a node for every park). 

The edges were a slightly bigger challenge - I had to go row by row through the game log and use the newly calculated `pitcher_list` field to create an edge from pitcher to stadium. Along the way, I made sure to increment the weights if an edge was already present, so that we could have a count of appearences. 

I did this for each team and then dumped a list into .csvs for nodes and edges, which you can find at `gephi-test/mlb_nodes_2024.csv` and `gephi-test/mlb_edges_2024.csv`, respectively.

#### Data Visualization
I originally wanted to do this with Tableau, but my free trial is running out, and I found that creating digraphs in Tableau is pretty cumbersome. [This article](https://nicole-klassen.medium.com/building-a-network-graph-in-tableau-bdaec20d79e4) by [Nicole Klassen](https://x.com/NicoleKlassen12) was incredibly helpful, even though I didn't go all the way with Tableau. Along the way, she uses an app called Gephi, which is an open source graph visualizer. I figured out how to accomplish my need with my data, and even found a way to publish it complete with filtering interactivity, which what I wanted to achieve with Tableau anyways.


### Result
You can view the result of this project [here](https://ouestware.gitlab.io/retina/beta/#/graph/?url=https%3A%2F%2Fgist.githubusercontent.com%2FShashComandur%2F8401e9dddf151149361bffb287e94d8e%2Fraw%2F757ae0655529ab535f098de21057e460a77be5dc%2Fnetwork-89bd9a8a-6b9.gexf)!