# import opensees.openseespy as ops  # Import OpenSeesPy module
# import numpy as np                  # For numerical operations (unused in this snippet)
# import math                         # For floating-point comparisons
# import csv                          # For writing CSV outputs
# import os                           # For filesystem operations

# ############################
# # Start of model generation#
# ###########################

# def create_model(walk_edge=False):
#     # Create ModelBuilder: 3 dimensions, 6 DOF per node
#     model = ops.Model(ndm=3, ndf=6)

#     E = 3.0e3  # Elastic modulus placeholder (kips/in^2)

#     # Define materials and section
#     # ----------------------------------
#     cover_1, rebar, total = 4, 1, 12
#     core = total - cover_1 - rebar

#     model.eval(r"""
#         nDMaterial ASDConcrete3D 1 30000.0 0.2 \
#         -Te 0.0 9e-05 0.00015 0.00507 0.0250501 0.250501 \
#         -Ts 0.0   2.7     3.0     0.6 0.003 0.003 \
#         -Td 0.0 0.0 0.0 0.960552268244576 0.9999800399998403 0.9999995660869531 \
#         -Ce 0.0 0.0005 0.0006666666666666666 0.0008333333333333333 0.001 0.0011666666666666665 0.0013333333333333333 0.0015 0.0016666666666666666 0.0018333333333333333 0.002 0.18327272727272728 0.18377272727272728 \
#         -Cs 0.0 15.0 19.282032302755088 22.459666924148337 24.852813742385703 26.6515138991168 27.979589711327122 28.92304845413264 29.54451150103322 29.891252930760572 30.0 3.0 3.0 \
#         -Cd 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 -2.220446049250313e-16 0.0 0.0 0.9981618744961699 0.9981786141748574 \
#         -autoRegularization 8.97663211186248
#     """)

#     model.uniaxialMaterial('Steel01', 2, 60.0, 30000.0, 0.01)
#     model.nDMaterial('PlateRebar', 3, 2,  0.0)
#     model.nDMaterial('PlateRebar', 4, 2, 90.0)
#     model.section('LayeredShell', 1,
#                   5,
#                   1, cover_1,
#                   3, rebar,
#                   1, core,
#                   4, rebar,
#                   1, cover_1)

#     model.uniaxialMaterial("Concrete01", 6, -6.0, -0.004, -5.0, -0.014)
#     model.section('Fiber', 5, '-GJ', 1.0)
#     model.patch('rect', 6, 10, 10, -0.5, -0.5, 0.5, 0.5)

#     # Geometry
#     nx, ny = 10, 10
#     points = {
#         1: [ 0.0    , 0.0,  0.0],
#         2: [-33.282 , 0.0, 49.923],
#         3: [ 0.0    , 0.0, 72.111],
#         4: [33.282  , 0.0, 22.077]
#     }
#     surface = model.surface((nx, ny), element='ShellMITC4', args=(1,), points=points)

#     # Optional edge frame
#     for nodes in surface.walk_edge():
#         model.element('PrismFrame', None, nodes, section=5, vertical=[0, 0, 1])

#     # Boundary conditions
#     model.fixZ( 0.0  , 1,1,1, 1,1,1)
#     model.fixZ(72.111, 1,1,1, 1,1,1)

#     def fix_at(x0, y0, z0, tol):
#         fixed = []
#         for nid in model.getNodeTags():
#             x, y, z = model.nodeCoord(nid)
#             if (math.isclose(x, x0, abs_tol=tol) and
#                 math.isclose(y, y0, abs_tol=tol) and
#                 math.isclose(z, z0, abs_tol=tol)):
#                 fixed.append(nid)
#         for n in fixed:
#             model.fix(n, 1,1,1, 1,1,1)

#     fix_at(-33.282, 0.0, 49.923, tol=1e-6)
#     fix_at( 33.282, 0.0, 22.077, tol=1e-6)
#     fix_at(  0.0  , 0.0, 36.0555, tol=1e-1)

#     return model

# def static_analysis(model, p):
#     # Load pattern
#     model.pattern('Plain', 1, 'Linear')
#     ele_tags = model.getEleTags()
#     for ele in ele_tags:
#         nids = model.eleNodes(ele)
#         # Distribute pressure p as nodal force
#         for nid in nids:
#             model.load(nid, 0.0, -p, 0.0, 0.0, 0.0, 0.0, pattern=1)

#     # Define analysis components
#     model.integrator('LoadControl', 1.0, 1, 1.0, 10.0)
#     model.test('EnergyIncr', 1.0e-10, 20, 0)
#     model.algorithm('Newton')
#     model.numberer('RCM')
#     model.constraints('Plain')
#     model.system('SparseGeneral', '-piv')
#     model.analysis('Static')
#     return model.analyze(1)
# ##############################################################################################


# if __name__ == '__main__':
#     # First, build one model and write out the node coordinates just once
#     model0 = create_model()
#     coord_fname = 'node_coordinates_p.csv'
#     with open(coord_fname, 'w', newline='') as f_coord:
#         writer = csv.writer(f_coord)
#         writer.writerow(['Node','x','y','z'])
#         for nid in model0.getNodeTags():
#             x, y, z = model0.nodeCoord(nid)
#             writer.writerow([nid, x, y, z])
#     print(f"Wrote {coord_fname} in {os.getcwd()}")

#     # Now loop only to compute & write displacements
#     p_values = [0.1, 0.2, 0.3, 0.4]  # your pressure series
#     for idx, p in enumerate(p_values, start=1):
#         model = create_model()
#         static_analysis(model, p)

#         # use iteration number (idx) in the filename
#         disp_fname = f'node_displacements_{idx}.csv'
#         with open(disp_fname, 'w', newline='') as f_disp:
#             writer = csv.writer(f_disp)
#             writer.writerow(['Node','ux','uy','uz'])
#             for nid in model.getNodeTags():
#                 writer.writerow([nid,
#                                 model.nodeDisp(nid,1),
#                                 model.nodeDisp(nid,2),
#                                 model.nodeDisp(nid,3)])
#         print(f"Wrote {disp_fname} for iteration {idx} (p = {p})")


import opensees.openseespy as ops  # Import OpenSeesPy module
import numpy as np                  # For numerical operations (unused in this snippet)
import math                         # For floating-point comparisons
import csv                          # For writing CSV outputs
import os                           # For filesystem operations

############################
# Start of model generation#
############################

def create_model(walk_edge=False):
    # Create ModelBuilder: 3 dimensions, 6 DOF per node
    model = ops.Model(ndm=3, ndf=6)

    E = 3.0e3  # Elastic modulus placeholder (kips/in^2)

    # Define materials and section
    # ----------------------------------
    cover_1, rebar, total = 2, 2, 12
    core = total - 2*cover_1 - 2*rebar

    model.eval(r"""
        nDMaterial ASDConcrete3D 1 30000.0 0.2 \
        -Te 0.0 9e-05 0.00015 0.00507 0.0250501 0.250501 \
        -Ts 0.0   2.7     3.0     0.6 0.003 0.003 \
        -Td 0.0 0.0 0.0 0.960552268244576 0.9999800399998403 0.9999995660869531 \
        -Ce 0.0 0.0005 0.0006666666666666666 0.0008333333333333333 0.001 0.0011666666666666665 0.0013333333333333333 0.0015 0.0016666666666666666 0.0018333333333333333 0.002 0.18327272727272728 0.18377272727272728 \
        -Cs 0.0 15.0 19.282032302755088 22.459666924148337 24.852813742385703 26.6515138991168 27.979589711327122 28.92304845413264 29.54451150103322 29.891252930760572 30.0 3.0 3.0 \
        -Cd 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 -2.220446049250313e-16 0.0 0.0 0.9981618744961699 0.9981786141748574 \
        -autoRegularization 8.97663211186248
    """)

    model.uniaxialMaterial('Steel01', 2, 60.0, 30000.0, 0.01)
    model.nDMaterial('PlateRebar', 3, 2,  0.0)
    model.nDMaterial('PlateRebar', 4, 2, 90.0)
    model.section('LayeredShell', 1,
                  7,
                  1, cover_1,
                  3, rebar,
                  4, rebar,
                  1, core,
                  4, rebar,
                  3, rebar,
                  1, cover_1)

    model.uniaxialMaterial("Concrete01", 6, -6.0, -0.004, -5.0, -0.014)
    model.section('Fiber', 5, '-GJ', 1.0)
    model.patch('rect', 6, 10, 10, -0.5, -0.5, 0.5, 0.5)

    # Geometry
    nx, ny = 10, 10
    points = {
        1: [ 0.0    , 0.0,  0.0],
        2: [-33.282 , 0.0, 49.923],
        3: [ 0.0    , 0.0, 72.111],
        4: [33.282  , 0.0, 22.077]
    }
   
    surface = model.surface((nx, ny), element='ShellMITC4', args=(1,), points=points)

    # Optional edge frame
    for nodes in surface.walk_edge():
        model.element('PrismFrame', None, nodes, section=5, vertical=[0, 0, 1])

    # Boundary conditions
    model.fixZ( 0.0  , 1,1,1, 1,1,1)
    model.fixZ(72.111, 1,1,1, 1,1,1)

    def fix_at(x0, y0, z0, tol):
        fixed = []
        for nid in model.getNodeTags():
            x, y, z = model.nodeCoord(nid)
            if (math.isclose(x, x0, abs_tol=tol) and
                math.isclose(y, y0, abs_tol=tol) and
                math.isclose(z, z0, abs_tol=tol)):
                fixed.append(nid)
        for n in fixed:
            model.fix(n, 1,1,1, 1,1,1)

    fix_at(-33.282, 0.0, 49.923, tol=1e-6)
    fix_at( 33.282, 0.0, 22.077, tol=1e-6)
    fix_at(  0.0  , 0.0, 36.0555, tol=1e-1)

    return model

def static_analysis(model, p):
    # Load pattern
    model.pattern('Plain', 1, 'Linear')
    ele_tags = model.getEleTags()
    for ele in ele_tags:
        nids = model.eleNodes(ele)
        # Distribute pressure p as nodal force
        for nid in nids:
            model.load(nid, 0.0, -p, 0.0, 0.0, 0.0, 0.0, pattern=1)

    # Define analysis components
    model.integrator('LoadControl', 1.0, 1, 1.0, 10.0)
    model.test('EnergyIncr', 1.0e-10, 20, 0)
    model.algorithm('Newton')
    model.numberer('RCM')
    model.constraints('Plain')
    model.system('SparseGeneral', '-piv')
    model.analysis('Static')
    return model.analyze(1)
##############################################################################################


if __name__ == '__main__':
    # First, write out the node coordinates once
    model0 = create_model()
    coord_fname = 'node_coordinates.csv'
    with open(coord_fname, 'w', newline='') as f_coord:
        writer = csv.writer(f_coord)
        writer.writerow(['Node','x','y','z'])
        for nid in model0.getNodeTags():
            x, y, z = model0.nodeCoord(nid)
            writer.writerow([nid, x, y, z])
    print(f"Wrote {coord_fname} in {os.getcwd()}")

    # Now ramp p until failure
    p     = 0   # starting pressure
    dp    = 0.5    # pressure increment
    itr   = 1
    while True:
        model = create_model()
        try:
            res = static_analysis(model, p)
        except Exception as e:
            print(f"Analysis threw exception at p={p:.3f}: {e}")
            break

        # OpenSeesPy analyze returns 0 on success, non‑zero on failure
        if res != 0:
            print(f"Analysis failed to converge at iteration {itr}, p = {p:.3f}")
            break

        # If here, analysis succeeded → write displacements
        disp_fname = f'node_displacements_{itr}.csv'
        with open(disp_fname, 'w', newline='') as f_disp:
            writer = csv.writer(f_disp)
            writer.writerow(['Node','ux','uy','uz'])
            for nid in model.getNodeTags():
                writer.writerow([nid,
                                 model.nodeDisp(nid,1),
                                 model.nodeDisp(nid,2),
                                 model.nodeDisp(nid,3)])
        print(f"Wrote {disp_fname} for iteration {itr} (p = {p:.3f})")

        # prepare next step
        itr += 1
        p   += dp
