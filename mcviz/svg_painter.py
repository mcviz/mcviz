from pdgid import get_glyph, glyph_dimensions

def label_pseudohtml(pdgid):
    w, h = glyph_dimensions(pdgid)
    return '<<table border="1" cellborder="0"><tr>\
           <td height="%.2f" width="%.2f">\E</td></tr></table>' % (h, w)


