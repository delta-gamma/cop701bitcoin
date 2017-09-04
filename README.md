# cop701DistributedLedger

# Normal Execution

When we run start.py from the terminal using the command "sudo python start.py", the user is asked for the number of nodes. 

On giving as input the number of nodes, the topology is created and the terminals for each host is opened.

start.py executes nodes.py on each host. 

Before running start.py, make sure to change the path mentioned in start.py to the path where nodes.py is stored.

Each host is given two options:
1. Making a transaction: The host is given an option to make a transaction of bitcoins to some other host.
2. Verifying the ledger: At any point of time, a host can verify its ledger with the ledger's of all other nodes.

# To stop the execution
 
 Use the command "exit".

# For Adding Host on the fly:

For adding a host in the already genrated network, type " py execfile("addHostonfly.py") " command in the mininet terminal. Then, enter the identifier of the host created.(Suppose host h5 is to be created, '5' is the identifier of the host).
Remeber hosts are created in sequential order.


