# cop701DistributedLedger

# Normal Execution:
We start by executing start.py from the terminal using the command "sudo python start.py", then the user is asked for the number of nodes. 

On giving as input the number of nodes, the topology is created and the xterms for each host is opened.

start.py executes nodes.py on each host of mininet topology. 

Before running start.py, make sure to change the path mentioned in start.py to the path where nodes.py is stored.

Each host is given two options:
1. Making a transaction: The host is given an option to make a transaction of bitcoins to some other host.
2. Verifying the ledger: At any point of time, a host can verify its ledger with the ledger's of all other nodes.

# To stop the execution:
 
 Type the command "exit" on the main terminal.

# For Adding Host on the fly:

For adding a host in the already generated network, type " py execfile("addHostonfly.py") " command in the mininet terminal. Then, enter the identifier of the host created.(Suppose host h5 is to be created, '5' is the identifier of the host).
Change the path of the nodes.py in the python script for execution.
Remember hosts are created in sequential order.



