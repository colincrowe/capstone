# Capstone

This repository contains all the pieces of my capstone.

The file capstone_utils.py contains the implementation of the simulation. Specifically, the sample_simulate function was used during development and for debugging purposes, while the write_to_file_simulate function was used to create the datasets.

The two jupyter notebooks contain the code used to create the datasets and to analyze those datasets, respectively. The jupyter notebook for creating the datasets also has the code to create visualizations for the graphs.

The .txt files contain the parameters used to create the various graphs. sample_weights.txt was used to create the toy network, while fork3.txt and fork3_intercon.txt were used to create the isolated and interconnected graphs, respectively. These files are parsed by the build_weighted_net function in capstone_utils.py. Specifically, these files should be interpreted as follows. The first section corresponds to the SIR layer, with each line corresponding to a node and each pair of numbers corresponds to the nodes it is connected to. So, for instance, in sample_weights.txt, node 0 is connected to node 1 with weight 10 and node 2 with weight 8. Note that github displays line numbers starting at 1 rather than 0. The second section corresponds to connecting the SIR layer to the sewer layer, and uses the same notation as before; in sample_weights.txt, the line "0 3    1 1    2 2    3 2" means that there is a sewer node that each of node 0, 1, 2, and 3 feeds into. Lastly, the final section connects sewer nodes to sewer nodes, using the notation that the first node connects to the second node with weight equal to the final number on each line.
