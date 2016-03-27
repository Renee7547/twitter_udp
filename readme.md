#Simple twitter
We will be using a virtual network to make the connection between a server and a total of three clients. For this purpose we are going to use [Mininet](http://mininet.org/walkthrough/).
One of the ways to define a custom topology in Mininet is to define the topology in Python and use the following command to run this topology 
```
sudo mn --custom finalTopol.py --topo mytopo
```

We run this program by typing ``./server.py`` in server terminal window and ``./client.py`` in client terminal windows.
For client side, we have three optional login name: *Mike(passwd:0000)*, *Chao(passwd:1111)* and *Wenhao(passwd:2222)*
