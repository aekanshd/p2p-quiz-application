#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) quiz application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
# Run tkinter code in another thread
import json
import tkinter as tk
from tkinter import messagebox
import threading

def buildInfo(msgKey, msgValue):
    msg = {
        "type": "info",
        msgKey: msgValue
    }
    return json.dumps(msg)

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    if msg is not None and type(msg) is str:
        msg = bytes(msg, "utf8")

    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)


def on_closing():
    global clients
    global addresses
    for sock in clients:
        sock.close()
    SERVER.close()
    clients = {}
    addresses = {}

class QuizMaster(threading.Thread):

    HOST = None
    PORT = None
    question = None
    client_list = list()
    clients_string = None

    def __init__(self, HOST=None, PORT=None):
        self.HOST = HOST
        self.PORT = PORT
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()
        on_closing()

    def addClientToList(self, client_name):
        self.client_list.append(client_name)
        self.buildClientList()

    def buildClientList(self):
        clients = ""
        for client in self.client_list:
            clients = clients + str(client) + ", "
        self.clients_string.set(clients)

    def checkAnswer(self, answer):
        print(type(answer),"answer",answer)
        print(type(self.correct_option.get()),"correct_option",self.correct_option.get())
        return True if str(answer) == str(self.correct_option.get()) else False

    def sendQuestion(self):
        if(self.question.get() == ""):
            tk.messagebox.showerror("Oops!", "Question cannot be empty!")
        else:
            msg = {
                "type": "question",
                "question": self.question.get()
            }
            msg['choices'] = list()
            msg['choices'].append({
                "text": self.choice1.get(),
                # "value": "True" if self.correct_option == 1 else "False" 
            })
            msg['choices'].append({
                "text": self.choice2.get(),
                # "value": "True" if self.correct_option == 2 else "False" 
            })
            msg['choices'].append({
                "text": self.choice3.get(),
                # "value": "True" if self.correct_option == 3 else "False" 
            })
            msg['choices'].append({
                "text": self.choice4.get(),
                # "value": "True" if self.correct_option == 4 else "False" 
            })
            broadcast(msg=json.dumps(msg))

    def run(self):
        self.root = tk.Tk()
        self.clients_string = tk.StringVar()
        self.root.title("Quiz Master")
        l1 = tk.Label(self.root, text="Quiz Master", font=("Arial Bold", 25))
        l1.grid(column=0, row=0)
        l2 = tk.Label(self.root, text="Welcome to the Quiz Master, master!\nYou can define a question, its options, and only one can be correct.\nThen watch your friends try answering them.\nSee who gets most of them right!", anchor="w")
        l2.grid(column=0, row=1, sticky=tk.W)
        clients_info = tk.Label(self.root, text="Active Players:") 
        clients_info.grid(column=1, row=1)
        clients_display = tk.Label(self.root, textvariable=self.clients_string) 
        clients_display.grid(column=2, row=1)
        l3 = tk.Label(self.root, text="HOST: "+str(self.HOST))
        l3.grid(column=0, row=2, sticky=tk.W)
        l4 = tk.Label(self.root, text="PORT: "+str(self.PORT))
        l4.grid(column=0, row=3, sticky=tk.W)
        l5 = tk.Label(self.root, text="Use the below form to generate your question.")
        l5.grid(column=0, row=5, sticky=tk.W)
        
        self.question = tk.Entry(self.root)
        self.question.grid(column=0, row=6, columnspan=3, sticky=tk.W)
        
        l6 = tk.Label(self.root, text="Choice 1: ")
        l6.grid(column=0, row=7, sticky=tk.W)
        self.choice1 = tk.Entry(self.root)
        self.choice1.grid(column=1, row=7, columnspan=3, sticky=tk.W)
        self.correct_option = tk.IntVar()
        self.c1 = tk.Radiobutton(self.root, text="Correct Answer", variable=self.correct_option, value=1)
        self.c1.grid(column=2, row=7)
        
        l7 = tk.Label(self.root, text="Choice 2: ")
        l7.grid(column=0, row=8, sticky=tk.W)        
        self.choice2 = tk.Entry(self.root)
        self.choice2.grid(column=1, row=8, columnspan=3, sticky=tk.W)
        self.c2 = tk.Radiobutton(self.root, text="Correct Answer", variable=self.correct_option, value=2)
        self.c2.grid(column=2, row=8)
        
        l8 = tk.Label(self.root, text="Choice 3: ")
        l8.grid(column=0, row=9, sticky=tk.W)
        self.choice3 = tk.Entry(self.root)
        self.choice3.grid(column=1, row=9, columnspan=3, sticky=tk.W)
        self.c3 = tk.Radiobutton(self.root, text="Correct Answer", variable=self.correct_option, value=3)        
        self.c3.grid(column=2, row=9)

        l9 = tk.Label(self.root, text="Choice 4: ")
        l9.grid(column=0, row=10, sticky=tk.W)
        self.choice4 = tk.Entry(self.root)
        self.choice4.grid(column=1, row=10, columnspan=3, sticky=tk.W)
        self.c4 = tk.Radiobutton(self.root, text="Correct Answer", variable=self.correct_option, value=4)
        self.c4.grid(column=2, row=10)

        submit_question = tk.Button(self.root, text='Send Question', command=self.sendQuestion)
        submit_question.grid(column=1, row=6, columnspan=3, sticky=tk.W)
        print("Hi here.")
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.mainloop()

"""
Payload:
{
    "type": "question",
    "question": "How is the best?",
    "choices": [
        {
            "text": "me?",
            "value": false
        },
        {
            "text": "ME?",
            "value": false
        },
        {
            "text": "ME",
            "value": false
        },
        {
            "text": "Me.",
            "value": true
        }
    ]
}
"""


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes(buildInfo("greeting", "Greetings player! Now type your name and press enter!"), "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(buildInfo("welcomeMsg", welcome), "utf8"))
    msg = "%s has joined the chat!" % name
    quizMaster.addClientToList(name)
    broadcast(bytes(buildInfo("joined", msg), "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ).decode("utf8")
        msg = json.loads(msg)
        if msg['type'] == "answer":
            client.send(bytes(buildInfo("answer", str(quizMaster.checkAnswer(msg["answer"]))), "utf8"))

        # if msg != bytes("{quit}", "utf8"):
        #     broadcast(msg, name+": ")
        # else:
        #     client.send(bytes("{quit}", "utf8"))
        #     client.close()
        #     del clients[client]
        #     broadcast(bytes(buildInfo("left","%s has left the chat." % name), "utf8"))
        #     break


clients = {}
addresses = {}

import socket as sock
HOST = sock.gethostname() if sock.gethostname().find('.')>=0 else sock.gethostbyaddr(sock.gethostname())[0]

PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    quizMaster = QuizMaster(HOST=HOST, PORT=PORT)
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()