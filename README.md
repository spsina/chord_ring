# Simple Chord Ring Implementation in Python
###### Author: Ali Parvizi 

## Introduction

### Node
A node is a chord in the ring.
every node starts a Websocket server (connection information 
will be saved in an AccessInfo Object), by which one can connect to the node
and execute commands (Eg. ask the node to locate a specific key in the ring)
on it

### AccessInfo
contain information such as address, port, and id of a node
using access info, we can connect to a node and
execute commands (Eg: locate a key)


### Network
network.py is a mini terminal that provides basic utility to
connect to and run commands on the nodes of a ring

### Network test
network_test.py start an automated test, to quickly test the ring network and node functionality

#### test structure
in this test, we will create a ring of 4 nodes

##### These are the nodes
Node | address | port | ID | chord |
-----|---------|------|----|------|
node 1| localhost | 1212 | 1| N/A |
node 2| localhost | 4545| 4 | 1   |
node 3| localhost | 6565| 13| 1   | 
node 4| localhost | 7878| 20| 1   | 

*chord indication the node id, the given node will use to connect to the ring

first we define AccessInfo objects for each of the above nodes
and the run the nodes

##### Test Criteria
1. Position of each node in the ring
2. Finger Table of each node
3. Storage location (node) of a given key


##### Position of each node in the ring
according to the nodes table and their ids:

node id | next node in the ring(id) | previous node in the ring
--------|---------------------------|---------------------------
1       |      4                    | 20
4       |   13                      | 1
13      | 4                         |   20
20      | 13                        | 1


the first part of network test will assert the correctness of the ring according to the above table

##### Finger Table Of each node

according to the nodes table, this is how the finger tables should be

node id | finger table
--------|-------------
1       |  4, 4, 13, 13, 20
4       |  13, 13, 13, 13, 20
13      | 20, 20, 20, 1, 1
20      | 1, 1, 1, 1, 4

the second part of network_test.py will assert the correctness of finger tables according the above table


##### Storage location (node) of a given key

key to locate | node id that initiates the key location | location of the key
--------------|-----------------------------------------|--------------------|
    3         |                 1                       | 4
    13        |                 20                      |   13
    26        |                 4                       | 1
    39        |                 13                      |   13



the third part of the network_test.py asserts the correctness of key location

# how run
_*this project is created and tested with python 3.8.2*_
first, install the requirements by running the following command

```pip install -r requirements.text```

