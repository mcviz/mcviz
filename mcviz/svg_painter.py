import re
from time import time
from sys import stderr

from svg import SVGDocument
from svg import photon, final_photon, gluon, boson, fermion, hadron, vertex

from .graphviz import PlainOutput

def paint_svg(plain, event, style):
    data = PlainOutput(plain)
    doc = SVGDocument(data.width, data.height, data.scale)

    t0 = time()
    for no, spline in data.edge_lines.iteritems():
        particle = event.particles[no]

        # set garish defaults args to make oversights obvious
        display_func = hadron
        args = {}
        args["energy"] = 0.2
        args["stroke"] = "pink"
        args["fill"] = "pink"
        args["stroke-width"] = 0.05
        args["scale"] = 0.1

        # colouring
        if particle.gluon:
            display_func = gluon
            args["stroke"] = "green"
        elif particle.photon:
            if particle.final_state:
                display_func = final_photon
            else:
                display_func = photon
            args["stroke"] = "orange"
        elif particle.colored:
            display_func = fermion
            if particle.color:
                args["stroke"] = "red"
                args["fill"] = "red"
            else:
                args["stroke"] = "blue"
                args["fill"] = "blue"
        elif particle.lepton:
            display_func = fermion
            args["stroke"] = "black"
            args["fill"] = "black"
        elif particle.boson:
            display_func = boson
            args["stroke"] = "black"
            args["fill"] = "black"
        else:
            display_func = hadron
            args["stroke"] = "black"
            args["fill"] = "black"
        
        doc.add_object(display_func(spline = spline, **args))

        if data.edge_label[no]:
            x, y = data.edge_label[no]
            pid = no if style.options.show_id else None
            doc.add_glyph(particle.pdgid, x, y, style.options.label_size, pid)

    for vno, pt in data.nodes.iteritems():        
        vx = event.vertices[vno]
        if vx.is_final:
            continue
        vertex_args = {"stroke":"black", "fill":"none", "stroke-width" : "0.05"}
        doc.add_object(vertex(pt, vx.layout.w, vx.layout.h, **vertex_args))


    t1 = time()
    print >> stderr, t1-t0
    return doc.toprettyxml()

