# treasure_hunt

1. Enter .src/, run `javac *.java`, then `java Raft -p Port -i s0.in`
1. In a new window, run `python agent.py`, the agent will request the default port 31415, 
    or you can assign a new port by using `python agent.py --port Port`. 
    
    \* Make sure you are using the same port as the java game engine
1. Icons and instructions
  * The obstacles and tools within the environment are represented as follows:

    * Obstacles  Tools
    * T 	tree      	a 	axe
    * \-	door	k	key
    * \*	wall	d	dynamite
    * \~	water	$	treasure
  * The agent will be represented by one of the characters ^, v, <  or  >, depending on which direction it is pointing. The agent is capable of the following instructions:

    *  L   turn left
    *  R   turn right
    *  F   (try to) move forward
    *  C   (try to) chop down a tree, using an axe
    *  B   (try to) blast a wall or tree, using dynamite
