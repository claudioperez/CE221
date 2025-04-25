# OpenSees -- Open System for Earthquake Engineering Simulation
#         Pacific Earthquake Engineering Research Center

#
# 3D Shell Structure
# ------------------
#  Shell roof modeled with three dimensional linear shell elements

# Example Objectives
# ------------------
#  test linear-elastic shell element
#  free vibration analysis starting from static deflection
#
# Units: kips, in, sec
#
# Written: Andreas Schellenberg (andreas.schellenberg@gmail.com)
# Date: September 2017

# import the OpenSees Python module
import opensees.openseespy as ops
import math

    ############################
    # Start of model generation#
    ############################

def create_model(walk_edge=False):
    # create ModelBuilder (with three-dimensions and 6 DOF/node)
    model = ops.Model(ndm=3, ndf=6)

    E = 3.0e3

    # Define the section
    # ------------------
    #                                           tag E   nu     h    rho
    model.section("ElasticShell", 1, E, 0.25, 1.175, 1.27)
    model.section('ElasticFrame', 2, E, 1, area=10, Iy=1, Iz=1, J=1)

    # Define geometry
    # ---------------
    # these should both be even
    nx = 20
    ny = 20

    # # loaded nodes
    # mid   = int(((nx+1)*(ny+1) + 1)/2)
    # side1 = int((nx+2)/2)
    # side2 = int((nx+1)*(ny+1) - side1 + 1)


    # generate the surface nodes and elements
    surface = model.surface((nx, ny),
                  element="ShellMITC4", args=(1,),
                  points = {
                            1: [ 0.0 , 0.0, 0.0],  
                            2: [-33.282, 0.0, 49.923],  
                            3: [ 0.0 , 0.0, 72.111],   
                            4: [33.282 , 0.0, 22.077],  
                            # 1: [ 0.0 , 0.0, 0.0],  
                            # 2: [-20.0, 0.0, 0.0],  
                            # 3: [ 20.0 , 0.0, 40.0],   
                            # 4: [0.0 , 0.0, 40.0],   
                            })


    for nodes in surface.walk_edge():
        # Note that supplying "None" as the tag
        # will cause the model to find the next
        # available tag and use it for the new
        # element
        model.element("PrismFrame", None, nodes, section=2, vertical=[0, 0, 1])

    #########################################################
    # define the boundary conditions                        #
    # rotation free about x-axis (remember right-hand-rule) #
    #########################################################

    model.fixZ( 0.0, 1, 1, 1, 1, 1, 1)
    model.fixZ(72.111, 1, 1, 1, 1, 1, 1)

    #################################################################
    # Fix nodes based on the coordinate where you want to fix a node#
    #################################################################

    x0, y0, z0 = -33.282, 0.0, 49.923
    tol = 1e-6   # tolerance for floating‐point comparison
    # collect node IDs whose coords match (x0,y0,z0)
    fixed_nodes = []
    for nid in model.getNodeTags():           # all node IDs in the model
        x,y,z = model.nodeCoord(nid)          # get that node’s coords
        if (math.isclose(x, x0, abs_tol=tol) and
            math.isclose(y, y0, abs_tol=tol) and
            math.isclose(z, z0, abs_tol=tol)):
            fixed_nodes.append(nid)

    # now apply fixities to each matching node
    # e.g. fix all translations, free all rotations:
    for nid in fixed_nodes:
        model.fix(nid, 1,1,1,  1,1,1)

    x1, y1, z1 = 33.282 , 0.0, 22.077
    tol = 1e-6   # tolerance for floating‐point comparison
        # collect node IDs whose coords match (x0,y0,z0)
    fixed_nodes = []
    for nid in model.getNodeTags():           # all node IDs in the model
        x,y,z = model.nodeCoord(nid)          # get that node’s coords
        if (math.isclose(x, x1, abs_tol=tol) and
            math.isclose(y, y1, abs_tol=tol) and
            math.isclose(z, z1, abs_tol=tol)):
            fixed_nodes.append(nid)

        # now apply fixities to each matching node
        # e.g. fix all translations, free all rotations:
    for nid in fixed_nodes:
        model.fix(nid, 1,1,1,  1,1,1)

    x2, y2, z2 = 0.0, 0.0, 36.0555
    tol = 1e-1   # tolerance for floating‐point comparison
        # collect node IDs whose coords match (x0,y0,z0)
    fixed_nodes = []
    for nid in model.getNodeTags():           # all node IDs in the model
        x,y,z = model.nodeCoord(nid)          # get that node’s coords
        if (math.isclose(x, x2, abs_tol=tol) and
            math.isclose(y, y2, abs_tol=tol) and
            math.isclose(z, z2, abs_tol=tol)):
            fixed_nodes.append(nid)

        # now apply fixities to each matching node
        # e.g. fix all translations, free all rotations:
    for nid in fixed_nodes:
        model.fix(nid, 1,1,1,  1,1,1)


    ################################################################################
    # Apply area load to the shell (For now what I have is apply load at each node)#
    ################################################################################

    # create a pattern with a Linear time series
    # and add some loads
    model.pattern("Plain", 1, "Linear")
    # model.load(mid  , 0.0, -0.50, 0.0, 0.0, 0.0, 0.0, pattern=1)
    # model.load(side1, 0.0, -0.25, 0.0, 0.0, 0.0, 0.0, pattern=1)
    # model.load(side2, 0.0, -0.25, 0.0, 0.0, 0.0, 0.0, pattern=1)
    
    # 2) define uniform pressure p (force per area)
    p = 0.02  # e.g. kips/ft²

    # 3) loop over elements and distribute to nodes
    ele_tags = model.getEleTags()    # returns a Python list of all element IDs

    for ele in ele_tags:
        # get the four nodes of this quad
        nids = model.eleNodes(ele)    # e.g. [n1,n2,n3,n4]
        # now you can distribute loads, etc.
        area = 1200                # your element area
        q = p * area / 4.0
        for n in nids:
            model.load(n, 0.0, -q, 0.0, 0.0, 0.0, 0.0, pattern=1)

    return model


def static_analysis(model):
    # Load control with variable load steps
    #                              init  Jd  min  max
    model.integrator("LoadControl", 1.0, 1, 1.0, 10.0)

    # Convergence test
    #                  tolerance maxIter displayCode
    model.test("EnergyIncr", 1.0e-10, 20, 0)

    # Solution algorithm
    model.algorithm("Newton")

    # DOF numberer
    model.numberer("RCM")

    # Constraint handler
    model.constraints("Plain")

    # System of equations solver
    model.system("SparseGeneral", "-piv")
    #system("ProfileSPD")

    # Analysis for gravity load
    model.analysis("Static")

    # Perform the gravity load analysis
    return model.analyze(5)
    #return model.nodeDisp(5)



# def dynamic_analysis(model,mid):
#     # ----------------------------
#     # Start of recorder generation
#     # ----------------------------

#     model.recorder("Node", "-file", "Node.out", "-time", "-node", mid, "-dof", 2, "disp")


#     # ------------------------------------------
#     # Configure and Perform the dynamic analysis
#     # ------------------------------------------

#     # Remove the static analysis & reset the time to 0.0
#     model.wipeAnalysis()
#     model.setTime(0.0)

#     # Now remove the loads and let the beam vibrate
#     model.remove("loadPattern", 1)

#     # Create the transient analysis
#     model.test("EnergyIncr", 1.0e-10, 20, 0)
#     model.algorithm("Newton")
#     model.numberer("RCM")
#     model.constraints("Plain")
#     model.system("SparseGeneral", "-piv")
#     model.integrator("Newmark", 0.50, 0.25)
#     model.analysis("Transient")

#     # record once at time 0
#     model.record()

#     # Perform the transient analysis (20 sec)
#     return model.analyze(100, 0.2)
#     # model.analyze(250, 0.50)


if __name__ == "__main__":
    model = create_model()
    static_analysis(model)
    
    # --- print out all nodal displacements (UX, UY, UZ) after the static solve ---
    for nid in model.getNodeTags():
        ux = model.nodeDisp(nid, 1)
        uy = model.nodeDisp(nid, 2)
        uz = model.nodeDisp(nid, 3)
        print(f"Node {nid:3d} -> ux = {ux:.6f}, uy = {uy:.6f}, uz = {uz:.6f}")

     # these should both be even
    # nx = 10
    # ny = 10

    # loaded nodes
    # mid   = int(((nx+1)*(ny+1) + 1)/2)
    # dynamic_analysis(model,mid)

###########################
# Rendering the slab model#
# #########################    
import veux
model = create_model()
static_analysis(model)

    #
    # Render the model in the undeformed state
    #

model_config = {
        "extrude_outline": "square",
        "extrude_scale": 2.0
    }
    
artist = veux.render(model,
                         show={"frame.surface", "plane.surface"},
                         model_config=model_config)

    # Save the rendering using the GLTF2.0 format
veux.serve(artist, port=8086)
#   artist.save("model.glb")

    #
    # Render the deformed state of the structure
    #
artist.draw_surfaces(state= model.nodeDisp,
                         scale=0.1,
   #                     reference={"plane.outline"},
   #                     displaced={"plane.surface", "plane.outline"},
    )

   
veux.serve(artist, port=8086)
#   artist.save("gravity.glb")

    
    
    
    

