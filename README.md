# rlcomp2020
This is sample source code for Reinforcement Learning Competition, hosted by FPT-Software (Hanoi, Vietnam). The game is Gold Miner.

Sample source code description: training and competition
During the competition, the following State information will be returned after an Action is performed:
- Information about competing Agents ("playerId": Agent's ID, integer; "posx": Agent's X position, integer; "posy": Agent's Y position, integer; "score": Agent's amount of gold mined, integer; "energy"": Agent's amount of remaining energy, integer; "lastAction": the last action, integer).
-	Information about the remaining obstacles on the map (their position and the amount of energy that will be subtracted when an Agent passes by).
-	Information about the remaining gold mines on the map (their position and the amount of gold). 
- Map size (height and witdth)
Based on the returned State information, teams can decide their own training strategies, such as designing Reward Function and defining State Space. In the two sample source code (Miner-Training-Local-CodeSample and Miner-Testing-CodeSample) provided to teams (described below), we will give an example on designing Reward Function and defining State Space using 02 functions get_state() and get_reward() respectively. Below is an overview of the two sample source code provided for training and competition:
A.	Source code for training - Miner-Training-Local-CodeSample
This is the sample source code used for training. The source code contains 02 major parts: Miner Game Environment and Deep reinforcement learning algorithm (Deep-Q learning - DQN). Figure 1 illustrates the information flow between programs.
 
Figure 1: The information flow between programs in the sample source code
used for training
Details of the two parts are as follows:

