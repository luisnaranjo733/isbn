import os
from sys import exit
from isbn import path

def remove():
    try:
        os.remove(path) 
        print("Deleted.")
    except OSError:
        print("Already gone!")

def show():
    try:
        with open(path, 'r') as fhandle:
            print(fhandle.read())
    except IOError:
        with open(path, 'a') as fhandle:
            print(fhandle.read())     

commands = [remove, show]

print "USE INDICES\n"

while True:
    for cmd in commands:
        print "%d: %s" % (commands.index(cmd)+1, cmd.func_name)

    ask = raw_input("> ")
    if ask in 'end exit leave bye'.split():
        break
    try:
        commands[int(ask)-1]()
    except:
        print("Try again!\n")

exit(0)
