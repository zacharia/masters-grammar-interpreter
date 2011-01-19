#!/usr/bin/env python

#==========================import stuff
import sys
#import math3D
from cgkit.cgtypes import *
import copy
import math

#==========================class definitions

class Node:
    "Represents a node in the derivation tree and stores all related information"
    
    def __init__(self, in_name = "", in_position = vec3(), in_extents = vec3(), in_orientation = mat3(1.0), in_parent = None, in_active = True, in_children = None, in_additive = True, in_priority = 0):
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
        #whether this node is additive or subtractive
        self.additive = in_additive
        #a list of children object
        if in_children == None:
            self.children = []
        else:
            self.children = in_children

        #the stuff for symmetry
        self.symmetry_type = "None" #can be rotation or reflection
        self.symmetry_num = 1 #this is how many times to repeat the thing in the 360 degrees for rotational symmetry
        self.symmetry_point = vec3()
        self.symmetry_vector = vec3()

        #this number indicates when the node should be added into the voxel grid. Higher means sooner.
        self.priority = in_priority

    def toString(self, computer_readable = False, verbose = True):
        """This method returns a string representation of the current node, if verbose is true, all
        attributes are included in the string, if not, then only a summary string is returned. If the second
        argument is true, then the output is produced for easy parsing by a program."""
        if computer_readable:
            ret_string = ""
            #this is assumed to always be verbose
            ret_string += "name %s active %s additive %s" % (self.name, self.active, self.additive)
            
            ret_string += " position "
            for i in self.position:
                ret_string += " %s" % i
                
            ret_string += " extents "
            for i in self.extents:
                ret_string += " %s" % i
                
            ret_string += " orientation "
            for i in self.orientation.toList():
                ret_string += " %s" % i
                
            ret_string += " priority "
            ret_string += " %s " % self.priority
            
            return ret_string
        else:
            if verbose:
                return "name: %s | active: %s | position: %s | extents: %s | orientation: %s | symmetry: %s | additive: %s | priority: %s" % (self.name, self.active, self.position, self.extents, self.orientation.toList(), self.symmetry_type, self.additive, self.priority)
            else:
                return "name: %s | active: %s | symmetry: %s" % (self.name, self.active, self.symmetry_type)

    def displayTree(self, depth = 0, verbose = False):
        """this method displays a tree to the command line."""
        #add the correct indentation
        ret = "\t" * depth
        #add the node's details (just name atm)
        if verbose:
            ret = ret + self.toString(False, True) + "\n"
        else:
            ret = ret + self.toString(False, False) + "\n"
        #recurse on the children, adding their results to the return string
        for i in self.children:
            ret += i.displayTree(depth + 1, verbose)
        #return the return string
        return ret

    def displayActiveNodes(self):
        """This method creates a string containing only the active nodes of the tree, basically the nodes that
        actually make up the final product of the derivation tree."""
        ret = ""
        #if the current node is active, then add it to the return string
        if self.active:
            ret += self.toString(True)
            ret += " # \n"

        #recurse on the children of this node
        for i in self.children:
            ret += i.displayActiveNodes()

        #return the final string that we produce.
        return ret

    def setSymmetry(self, sym_type = "rotational", point = vec3(), vector = vec3(0,0,1), num = 2):
        self.symmetry_type = sym_type
        self.symmetry_num = num
        self.symmetry_point = point
        self.symmetry_vector = vector

    def copy(self, copy_children = False):
        if copy_children:
            return copy.deepcopy(self)
        else:
            ret = Node()
            ret.name = copy.deepcopy(self.name)

            ret.position = copy.deepcopy(self.position)
            ret.extents = copy.deepcopy(self.extents)
            ret.orientation = copy.deepcopy(self.orientation)

            ret.additive = copy.deepcopy(self.additive)

            ret.priority = copy.deepcopy(self.priority)
            return ret

    #this method splits a node up along on of it's axes.  if in_place
    #is true, the current node is made inactive and the resultant
    #splits are added to it as children otherwise, the node is
    #deactivated, and the splitted nodes are returned.
    def splitNode(self, axis = "y", num_splits = 2, in_place = True):
        #make a list containing the splits, initially as copies of the current node
        ret = [self.copy() for i in range(num_splits)]

        #loop through ret and update the elements as appropriate
        #count is used as a counter since looping over ret doesn't have any associated number
        count = 0
        for i in ret:
            if axis == "x":
                i.extents.x = self.extents.x / num_splits
                i.position.x = self.corner().x + i.extents.x + (count * i.extents.x * 2)
            elif axis == "y":
                i.extents.y = self.extents.y / num_splits
                i.position.y = self.corner().y + i.extents.y + (count * i.extents.y * 2)
            elif axis == "z":
                i.extents.z = self.extents.z / num_splits
                i.position.z = self.corner().z + i.extents.z + (count * i.extents.z * 2)
            #increase our counter
            count += 1

        #deactivate the current node
        self.active = False
        #either return the splits or append, depending on the argument in_place
        if in_place:
            self.children.extend(ret)
        else:
            return ret

    #this method returns the position of a corner of the node's bounding box as a vector.
    #which corner is desired is specified in the other arguments (which represent which corner to choose in local coordinates of the node) i.e. if this was called for a unit cube centred on the origin, 1,1,1 would return 0.5,0.5,0.5
    def corner(self, x = -1, y = -1, z = -1):
        #this makes the chosen corner values all either 1 or -1
        if x != -1:
            x = 1
        if y != -1:
            y = 1
        if z != -1:
            z = 1

        #make a vector out of the chosen corner values
        corner_specification = vec3(x,y,z)
    
        #then find the chosen corner's coordinates
        ret = vec3()
        ret.x = self.position.x + (self.extents.x * corner_specification.x)
        ret.y = self.position.y + (self.extents.y * corner_specification.y)
        ret.z = self.position.z + (self.extents.z * corner_specification.z)
                
        return ret

    #these methods return the node's local coordinate axes
    def get_x_axis(self):
        return self.orientation.getColumn(0)

    def get_y_axis(self):
        return self.orientation.getColumn(1)

    def get_z_axis(self):
        return self.orientation.getColumn(2)

    #this method hollows out the shape it is called on, by creating a copy of the shape, shrinking the copy
    #slightly (by hollow_size_factor given as an argument), and then inverting the copy's additive-ness.
    def makeHollow(self, hollow_size_factor = 0.9, and_children = True):
        #do a post-order recursive walk of the tree, to avoid infinite
        #loop problems with children being added and then recursed on
        if and_children:
            #recurse on the children of the node
            for i in self.children:
                i.makeHollow(hollow_size_factor, True)

        #make a hollow copy of the current node and attach it to the
        #node as a child
        subtractive_copy = self.copy()
        subtractive_copy.invertNodeAdditivity(False)
        subtractive_copy.scaleNode(hollow_size_factor, False)
        subtractive_copy.position = vec3(0.0)
        subtractive_copy.priority = self.priority - 1
        self.children.append(subtractive_copy)

        
    #move the node, and it's children by the offset given as an
    #argument this only works properly when using relative
    #coordinates, and may cause unintended results if running the
    #program with absolute coordinates on (-a)
    def moveNode(self, offset):
        self.position += offset

    #rotate the node, and it's children, by the axis angle given. as
    #with moveNode(), this only works properly for relative
    #coordinates
    def rotateNode(self, angle, x, y, z):
        self.orientation.rotate(angle, vec3(x,y,z))

    #this method recursively scales a node by the scalar value of
    #scaling_factor. If and_children is True, then it will scale the
    #entire branch rooted by self, with the scaling centred on self.
    def scaleNode(self, scaling_factor, and_children = True):
        #first scale self.
        self.extents = self.extents * scaling_factor
        
        #if we need to recurse on self's children
        if and_children:
            #loop through the children of the current node.
            children_list = self.children
            for i in children_list:
                #adjust each of the children's extents and positions
                i.extents = i.extents * scaling_factor
                i.position = i.position * scaling_factor
                #add the child's children to the list (instead of recursing on them)
                children_list.extend(i.children)

    #this method inverts a node's additivity, and optionally the rest
    #of the branch it roots
    def invertNodeAdditivity(self, and_children = True):
        self.additive = not self.additive
        
        if and_children:
            children_list = self.children
            for i in children_list:
                i.additive = not i.additive
                children_list.extend(i.children)
                

#==========================Standard helper methods to be used in the rule sets

#==========================interpreter methods

def handle_args(args):
    """this takes the raw input arguments and returns a dictionary of the option names mapped
    onto their values"""
    #dictionary containing default values
    options = {"input_file" : None, "output_file" : None, "max_iterations" : -1, "parallel_execution" : False, "verbose" : False, "quiet" : False, "relative_coordinates" : True}

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
        #if this flag is used, then the program shouldn't output the final machine readable code of the product.
        elif args[0] == "-q":
            options["quiet"] = True
            args = args[1:]
        #This flag indicates whether to use relative coordinates or absolute coordinates when interpreting the grammar.
        elif args[0] == "-a":
            options["relative_coordinates"] = False
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


#This does a recursive depth first walk of the tree rooted at the argument 'node' and updates all of it's children
# to their correct symmetrical positions based on the other arguments.
def updateRotationalSymmetryCopy(node, count, sym_num = 2, sym_point = vec3(), sym_vector = vec3(0,0,1)):
    #recurse on the children
    for i in node.children:
        updateRotationalSymmetryCopy(i, count, sym_num, sym_point, sym_vector)

    #update the current node's position
    temp_v = node.position - sym_point

    rot_quat = quat(((math.pi * 2) / sym_num) * count, sym_vector)
    temp_v = rot_quat.rotateVec(temp_v)

    node.position = temp_v + sym_point
        
    #update in's orientation using quaternion slerping
    #do this by rotating the orientation of i by the axis angle quaternion formed from the symmetry_vector
    #and the appropriate angle.

    node.orientation = node.orientation.rotate(((-math.pi * 2) / sym_num) * count, sym_vector)
    
        
def makeRotationalSymmetryCopy(root, sym_num = 2, sym_point = vec3(), sym_vector = vec3(0,0,1)):
    """This method takes a subtree and rotational symmetry parameters and returns a list of subtrees that
    represent the rotational reflections of the input subtree."""
    #make a working copy of the node for each reflection we need to make
    ret = [ copy.deepcopy(root) for i in range(sym_num-1) ]

    #this acts as a counter of which symmetric copy we're one
    count = 0

    #loop through all of the copies
    for i in ret:
        #update our counter
        count += 1

        #call the method to update each copy to it's correct position, and give it the necessary arguments
        updateRotationalSymmetryCopy(i, count, sym_num, sym_point, sym_vector)
            
    #return the list of reflections
    return ret


#this method just reflects a vector about a plane with normal given be plane_normal
def reflectVector(vector, plane_normal):
    ret = vector - ((2 * plane_normal.normalize()) * (vector * plane_normal.normalize()))

    return ret


def makeReflectiveSymmetryCopy(root, sym_point = vec3(), sym_vector = vec3(0,0,1)):
    """This method takes a subtree and some reflective symmetry parameters and returns a subtree
    that is the reflective rotation of the original subtree."""
    #make a working copy of the subtree to reflect. This will be transformed into the relfection
    ret = copy.deepcopy(root)

    #do an iterative walk of the tree (breadth first walk), updating the nodes as we walk through them
    nodes = []
    #add root to the front of the list
    nodes.insert(0, ret)
    for i in nodes:
        #update i
        
        #the formula that this code does was provided by julian. It's apparently a generalized reflection equation.
        #this does the change in position.
        v = i.position - sym_point
        i.position = i.position - ((2 * sym_vector.normalize()) * (v * sym_vector.normalize()))
        
        #mirror the orientation of the object by reflecting each of the columns of the matrix about the reflection plane.        
        #first extract the axes from the rotation matrix
        v1 = i.orientation.getRow(0)
        v2 = i.orientation.getRow(1)
        v3 = i.orientation.getRow(2)
        #then reflect them
        v1 = reflectVector(v1, sym_vector)
        v2 = reflectVector(v2, sym_vector)
        v3 = reflectVector(v3, sym_vector)
        #then put them back into the orientation_mat variable of the reflection
        i.orientation.setRow(0, v1)
        i.orientation.setRow(1, v2)
        i.orientation.setRow(2, v3)
                        
        #add i's children to the nodes list
        nodes.extend(i.children)
    
    #return the reflection
    return ret


def doSymmetry(root):
    """This method is called after the deriveTree method has run, and searches the tree for
    any subtrees with symmetry information set. It then creates the symmetric reflections
    of those subtrees."""

    #loop through the children of the node
    for i in root.children:
        #recurse on the children (depth-first walk)
        doSymmetry(i)
        
    #if the current node is symmetric, then create the relfection(s) of it and return it/them
    if root.symmetry_type == "rotational":        
        root.children.extend(makeRotationalSymmetryCopy(root, root.symmetry_num, root.symmetry_point, root.symmetry_vector))        
    elif root.symmetry_type == "reflective":
        root.children.insert(0, makeReflectiveSymmetryCopy(root, root.symmetry_point, root.symmetry_vector))
    #if it's not symmetric, then do nothing.


#This method goes through the derivation tree, from the root downwards, and updates each node's
#position and orientation to be relative to that of it's parent.
def updateNodePositionsRelative(root):

    #loop through the children
    for i in root.children:
        #update their positions to be relative to their parent
        i.position = (i.position * root.orientation) + root.position
        #update their orientation to be relative to their parent
        i.orientation = root.orientation * i.orientation
    
    #loop through the children of the node
    for i in root.children:
        #recurse on the children (depth-first walk)
        updateNodePositionsRelative(i)
    

#===========================main code

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
        if options["relative_coordinates"]:
            print "relative coordinates"
        else:
            print "absolute coordinates"        
        print "\n"

    #get the input file
    get_input(options["input_file"])

    if options["verbose"]:
        print "AXIOM:\n" + axiom.displayTree()

    result = deriveTree(axiom, options)

    if options["relative_coordinates"]:
        if options["verbose"]:
            print "Updating node coordinates relative to their parents."
        updateNodePositionsRelative(result)
    
    if options["verbose"]:
        print "Creating symmetry branches."
    doSymmetry(result)
    
    if options["verbose"]:
        print "===================FINAL RESULT===================\n"
        print result.displayTree(verbose=True)

    if not options["quiet"]:
        print result.displayActiveNodes()
