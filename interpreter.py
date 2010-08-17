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
        #add the correct indentation
        ret = "\t" * depth
        #add the node's details (just name atm)
        ret = ret + self.name + "\n"
        #recurse on the children, adding their results to the return string
        for i in self.children:
            ret += i.displayTree(depth + 1)
        #return the return string
        return ret

#==========================methods:

def handle_args(args):
    """this takes the raw input arguments and returns a dictionary of the option names mapped
    onto their values"""
    #dictionary containing default values
    options = {"input_file" : None, "output_file" : None, "max_iterations" : -1, "parallel_execution" : False, "verbose" : False}

    #while args is non-empty
    while args:
        #this flag gets the input file containing the rules and axiom
        if args[0] == "-i":
            options["input_file"] = args[1]
            args = args[2:]
        #this contains the output file where the output is written to
        elif args[0] == "-o":
            options["output_file"] = args[1]
            args = args[2:]
        #this stores the maximum number of iterations to do, a negative value means infinite
        elif args[0] == "-m":
            options["max_iterations"] = int(args[1])
            args = args[2:]
        #if this flag is set, then the program should execute rules in parallel, instead of serial
        elif args[0] == "-p":
            options["parallel_execution"] = True
            args = args[1:]
        #if this flag is used, then the program should produce verbose output
        elif args[0] == "-v":
            options["verbose"] = True
            args = args[1:]
        else:
            print "unrecognized argument: %s" % args[0]
            args = args[1:]
            
    #return dictionary of options
    return options

def get_input(infile):
    """this method reads the input file's contents and evals them."""
    if infile != None:
        input = open(infile, "r")
    else:
        input = sys.stdin

    #read the entire input file into code and close the file
    code = input.read()
    input.close()
    
    #this does an eval of everything in code and puts it into the global symbol table thing
    exec code in globals()

    
def hasNonTerminals(root):
    """This method determines whether there are any non-terminals nodes left in the derivation tree
    given as an argument."""
    #don't forget to check for non-active nodes as well
    return True


def continueDerivation(root, iterations, maxIterations):
    """Determines whether derivation should continue or not. Checks if non-terminals are present,
    and whether the max number of iterations has been reached."""

    #print "its: %s / %s" % (iterations, maxIterations)

    #if the number of iterations is capped and we've hit that cap, then stop derivation
    if maxIterations < 0:
        underMaxIterations = True
    else:
        if iterations >= maxIterations:
            underMaxIterations = False
        else:
            underMaxIterations = True
    
    #if we're under max iterations and there are non-terminals, then return true
    if underMaxIterations and hasNonTerminals(root):
        return True
    else:
        return False


def doParallelIteration(root):
    """This recursively does one iteration of parallel rule execution on the tree"""
    #if the current is active and there is a rule for doing something to it
    if root.active and hasattr(self, root.name):
        #then get that rule's method and store a reference to it in rule_method
        rule_method = getattr(self, root.name)
        #then execute the rule on the current node and add the result as a child
        root.children.append( rule_method(root.parent) )
        root.active = False

    for i in root.children:
        doParallelIteration(i)
    

def doSerialIteration(root):
    """This recursively does one iteration of serial rule execution on the tree"""
    pass

    
def deriveTree(axiom, maxIterations = -1, parallel_execution = False):
    """This method takes the given input axiom and creates the derivation tree from it.
    It assumes that the grammar has already been exec'd into the program."""
    iterations = 0
    axiom.parent = None
    
    while continueDerivation(axiom, iterations, maxIterations):

        #do an iteration of either parallel or serial execution
        if parallel_execution:
            doParallelIteration(axiom)
        else:
            doSerialIteration(axiom)
        
        #increase the iteration counter
        iterations += 1

    return axiom
    
#===========================main code:

#The file that gets read in and exec'd needs to define a Node object called 'axiom', which is the
#starting symbol, and a method per grammar rule with the same name as the LHS of the rule.

if __name__ == "__main__":
    #get the arguments into args
    args = sys.argv[1:]

    #parse the arguments
    options = handle_args(args)

    if options["verbose"]:
        print "\n"
        print "Python Shape Grammar Interpreter"
        print "input file: %s" % options["input_file"]
        print "output file: %s" % options["output_file"]
        print "max iterations: %d" % options["max_iterations"]
        if options["parallel_execution"]:
            print "parallel rule execution"
        else:
            print "serial rule execution"
        print "\n"

    #get the input file
    get_input(options["input_file"])

    # root, c1, c2 = [Node() for i in range(3)]
    # root.name = "root"
    # c1.name = "c1"
    # c2.name = "c2"
    # root.children.append(c1)
    # root.children.append(c2)
    # print root.displayTree()

    result = deriveTree(axiom, options["max_iterations"], options["parallel_execution"])
    print result.displayTree()
