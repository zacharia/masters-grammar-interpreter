#!/usr/bin/env python

#==========================import stuff
import sys
import math3D
import copy

#==========================class definitions

class Node:
    "Represents a node in the derivation tree and stores all related information"
    
    def __init__(self, in_name = "", in_position = math3D.zero3(), in_extents = math3D.zero3(), in_orientation = math3D.zeroQ(), in_parent = None, in_active = True, in_children = None):
        #position of the centre of the node's shape
        self.position = in_position
        #radii of the extents of the node's shape
        self.extents = in_extents
        #the node's shape's orientation in 3D space
        self.orientation = in_orientation
        #the name/type of the node
        self.name = in_name
        #pointer to parent node
        self.parent = in_parent
        #whether the node is active or not
        self.active = in_active
        #a list of children object
        if in_children == None:
            self.children = []
        else:
            self.children = in_children

        #the stuff for symmetry
        self.symmetry_type = "" #can be rotation or reflection
        self.symmetry_num = 1 #this is how many times to repeat the thing in the 360 degrees for rotational symmetry
        self.symmetry_point = math3D.zero3()
        self.symmetry_vector = math3D.zero3()

    def toString(self, computer_readable = False, verbose = True):
        """This method returns a string representation of the current node, if verbose is true, all
        attributes are included in the string, if not, then only a summary string is returned. If the second
        argument is true, then the output is produced for easy parsing by a program."""
        if computer_readable:
            ret_string = ""
            #this is assumed to always be verbose
            ret_string += "%s %s" % (self.name, self.active)
            for i in self.position:
                ret_string += " %s" % i
            for i in self.extents:
                ret_string += " %s" % i
            for i in self.orientation:
                ret_string += " %s" % i
            return ret_string
        else:
            if verbose:
                return "name: %s | active: %s | position: %s | extents: %s | orientation: %s" % (self.name, self.active, self.position, self.extents, self.orientation)
            else:
                return "name: %s | active: %s" % (self.name, self.active)

    def displayTree(self, depth = 0):
        """this method displays a tree to the command line."""
        #add the correct indentation
        ret = "\t" * depth
        #add the node's details (just name atm)
        ret = ret + self.toString(False, False) + "\n"
        #recurse on the children, adding their results to the return string
        for i in self.children:
            ret += i.displayTree(depth + 1)
        #return the return string
        return ret

    def displayActiveNodes(self):
        """This method creates a string containing only the active nodes of the tree, basically the nodes that
        actually make up the final product of the derivation tree."""
        ret = ""
        #if the current node is active, then add it to the return string
        if self.active:
            ret += self.toString(True)
            ret += " # "

        #recurse on the children of this node
        for i in self.children:
            ret += i.displayActiveNodes()

        #return the final string that we produce.
        return ret

    def setSymmetry(self, sym_type = "rotational", num = 2, point = math3D.zero3(), vector = math3D.zero3()):
        self.symmetry_type = sym_type
        self.symmetry_num = num
        self.symmetry_point = point
        self.symmetry_vector = vector

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

    if root.active and root.name in globals():
        return True
    
    #recursive part - loop through the children
    for i in root.children:
        #if a child has non-terminals, then the whole tree does. Return true
        if hasNonTerminals(i):
            return True
    #if we go through all the children trees, and none have non-terminals, then return false
    return False


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

    for i in root.children:
        doParallelIteration(i)
    
    #if the current is active
    if root.active:
        #then get that rule's method and store a reference to it in rule_method
        if root.name in globals():
            rule_method = globals()[root.name]
            #then execute the rule on the current node and add the result as a child
            root.children.extend( rule_method(root) )
            root.active = False
    

def doSerialIteration(root):
    """This method does one iteration of serial rule execution on the tree, using a breadth-first
    search to find the next node to operate on."""
    #this list is the queue used for the breadth first search
    bfs_queue = [root]
    #loop through the queue of nodes to check
    for i in bfs_queue:
        #if the current node is active and non-terminal
        if i.active and i.name in globals():
        #then get that rule's method and store a reference to it in rule_method
            rule_method = globals()[i.name]
            #then execute the rule on the current node and add the result as a child
            i.children.extend( rule_method(root) )
            i.active = False
            #we're only doing one derivation per iteration, so we can quit after doing one.
            return
        #if the current node is not eligible to derive
        else:
            #then add it's children to the bfs queue.
            bfs_queue.extend(i.children)

    
def deriveTree(axiom, options):
    """This method takes the given input axiom and creates the derivation tree from it.
    It assumes that the grammar has already been exec'd into the program."""
    iterations = 0
    axiom.parent = None
    
    while continueDerivation(axiom, iterations, options["max_iterations"]):

        if options["verbose"]:
            print "----------after iteration: %d----------\n" % (iterations+1)
        
        #do an iteration of either parallel or serial execution
        if options["parallel_execution"]:
            doParallelIteration(axiom)
        else:
            doSerialIteration(axiom)
        
        #increase the iteration counter
        iterations += 1

        if options["verbose"]:
            print axiom.displayTree()

    return axiom


def makeRotationalSymmetryCopy(root, sym_num = 2, sym_point = math3D.zero3(), sym_vector = math3D.zero3()):
    """This method takes a subtree and rotational symmetry parameters and returns a list of subtrees that
    represent the rotational reflections of the input subtree."""
    ret = [ copy.deepcopy(root) for i in range(sym_num) ]
    
    return ret


def makeReflectiveSymmetryCopy(root, sym_point = math3D.zero3(), sym_vector = math3D.zero3()):
    """This method takes a subtree and some reflective symmetry parameters and returns a subtree
    that is the reflective rotation of the original subtree."""
    ret = copy.deepcopy(root)

    return ret


def doSymmetry(root):
    """This method is called after the deriveTree method has run, and searches the tree for
    any subtrees with symmetry information set. It then creates the symmetric reflections
    of those subtrees."""
    
    for i in root.children:
        doSymmetry(i)
        
    for i in root.children:
        if i.symmetry_type == "rotational":
            root.children.extend(makeRotationalSymmetryCopy(root, i.symmetry_num, i.symmetry_point, i.symmetry_vector))
        if i.symmetry_type == "reflective":
            root.children.append(makeReflectiveSymmetryCopy(root, i.symmetry_point, i.symmetry_vector))

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

    if options["verbose"]:
        print "AXIOM:\n" + axiom.displayTree()

    result = deriveTree(axiom, options)

    if options["verbose"]:
        print "Creating symmetry branches."
    doSymmetry(result)

    if options["verbose"]:
        print "===================FINAL RESULT===================\n"
        print result.displayTree()

    print result.displayActiveNodes()
