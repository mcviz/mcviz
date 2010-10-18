
def subscripts(layout):
    # Label particles by id if --show-id is on the command line.
    if "id" in layout.options.subscript:
        def label_particle_no(particle):
            if not particle.gluon:
                return particle.reference
        layout.annotate_particles(graph.particles, label_particle_no)

    if "color" in layout.options.subscript:
        layout.annotate_particles(graph.particles, lambda p: p.color)
        layout.annotate_particles(graph.particles, lambda p: -p.anticolor)

def svg(layout):
    edge_args = {}
    edge_args["energy"] = 0.2
    edge_args["stroke"] = "black"
    edge_args["fill"] = "black"
    edge_args["stroke-width"] = 0.05
    edge_args["scale"] = 0.1

    for edge in layout.edges:
        edge.style_line_type = "identity"
        edge.style_args.update(edge_args)

    node_args = {"stroke":"black", "fill":"none", "stroke-width" : "0.05"}
    for node in layout.nodes:
        node.style_args.update(node_args)

def simple(layout):
    """ just do some simple coloring of lines """
    for edge in layout.edges:
        particle = edge.item
        if particle.gluon:
            edge.style_args["stroke"] = edge.style_args["fill"] = "green"
        elif particle.photon:
            edge.style_args["stroke"] = edge.style_args["fill"] = "orange"
        elif particle.colored:
            if particle.color:
                edge.style_args["stroke"] = edge.style_args["fill"] = "red"
            else:
                edge.style_args["stroke"] = edge.style_args["fill"] = "blue"
        elif particle.lepton:
            edge.style_args["stroke"] = edge.style_args["fill"] = "black"
        else:
            edge.style_args["stroke"] = edge.style_args["fill"] = "black"

def fancylines(layout):
    """ set fancy line types, curly gluons, wavy photons etc."""
    for edge in layout.edges:
        particle = edge.item
        # colouring
        if "jet" in particle.tags:
            edge.style_line_type = "hadron"
            edge.style_args["scale"] = 0.8
            edge.style_args["stroke-width"] = 0.4
        elif particle.gluon:
            edge.style_line_type = "gluon"
        elif particle.photon:
            if particle.final_state:
                edge.style_line_type = "final_photon"
            else:
                edge.style_line_type = "photon"
        elif particle.colored:
            edge.style_line_type = "fermion"
        elif particle.lepton:
            edge.style_line_type = "fermion"
        elif particle.boson:
            edge.style_line_type = "boson"
        else:
            edge.style_line_type = "hadron"

