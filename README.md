# P2P (PEER-TO-PEER) MESSAGING APPLICATION

This P2P Messaging Application is a terminal-based chat application that enables direct messaging between users over a network without the need for a centralized server. Utilizing Python's socket programming and threading, it offers a simple but effective platform for real-time communication. 

## Features

- **Direct Peer-to-Peer Messaging:** Communicate directly with peers without the need for a central server.
- **Dynamic User Discovery:** Register and discover users through a central server for initial connection setup.
- **Contact Management:** Accept or block contacts, managing who can send you messages.
- **Offline Messaging:** Send messages to users who are offline, which will be delivered when they come online.
- **Real-Time Communication:** Utilize sockets for real-time message exchange.
- **Multi-threaded Input Handling:** Manage user inputs efficiently in a multi-threaded environment, ensuring a smooth user experience.

## Requirements
- Python 3.6 or higher
- SQLite3 for Python

## Getting started
How to clone the repository:
```bash
git clone https://github.com/iperezgamiz/P2P-messaging-app/
```
Install dependencies: 

```bash
pip install -r requirements.txt
```

## Usage guide
It is first necessary to create each client's database by running the create_database.py script
```bash
python create_database.py
```

and introducing the *username* parameter that is asked.

To initialize the central server that handles users connections:
```bash
python server.py
```
To start a client connection:
```bash
python client.py
```
