#!/usr/bin/env python

#==========================import stuff
import sys
import math3D

#==========================class definitions

class Node:
    "Represents a node in the derivation tree and stores all related information"
    
    def __init__(self):
        #position of the centre of the node's shape
        self.position = math3D.zero3()
        #radii of the extents of the node's shape
        self.extents = math3D.zero3()
        #the node's shape's orientation in 3D space
        self.orientation = math3D.zeroQ()
        #the name/type of the node
        self.name = ""
        #pointer to parent node
        self.parent = None
        #whether the node is active or not
        self.active = True
        #a list of children object
        self.children = []

    def displayTree(self, depth = 0):
        """this method displays a tree to the command line."""
        ret = "\t" * depth
        ret = ret + self.name + "\n"
        for i in self.children:
            ret += i.displayTree(depth + 1)
        return ret

#==========================methods:

#this takes the raw input arguments and returns a dictionary of the option names mapped onto their values
def handle_args(args):
    #dictionary containing default values
    options = {"input_file" : None, "output_file" : None}

    #while args is non-empty
    while args:
        if args[0] == "-i":
            options["input_file"] = args[1]
            args = args[2:]
        elif args[0] == "-o":
            options["output_file"] = args[1]
            args = args[2:]
        else:
            print "unrecognized argument: %s" % args[0]
            args = args[1:]
            
    #return dictionary of options
    return options


#this method reads the input file's contents and evals them
def get_input(infile):
    if infile != None:
        input = open(infile, "r")
    else:
        input = sys.stdin

    #read the entire input file into code and close the file
    code = input.read()
    input.close()
    
    #this does an eval of everything in code and puts it into the global symbol table thing
    exec code in globals()

#===========================main code:

if __name__ == "__main__":
    #get the arguments into args
    args = sys.argv[1:]

    #parse the arguments
    options = handle_args(args)

    #get the input file
    get_input(options["input_file"])

    root, c1, c2 = [Node() for i in range(3)]
    root.name = "root"
    c1.name = "c1"
    c2.name = "c2"
    root.children.append(c1)
    root.children.append(c2)
    print root.displayTree()
