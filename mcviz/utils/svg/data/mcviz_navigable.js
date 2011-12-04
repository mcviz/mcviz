const SVG = "http://www.w3.org/2000/svg";
const XLINK = "http://www.w3.org/1999/xlink";

var main_trans = null, cur_trans = null;
var everything = null, marker = null;
var zoom_value = 0;
var ex = 0, ey = 0, mouse_position_in_lumispace = 0;


var viewdata = null;
var eventdata = null;
var ui = null;
var particle_selector = null;

function mcviz_init(event) {
    // Performed on script load

    c = $("#whole_document")[0];
    c.addEventListener("mousemove", on_mouse_move, false);
    c.addEventListener("mouseup", on_mouse_up, false);
    c.addEventListener("mousedown", on_mouse_down, false);
    
    window.addEventListener("DOMMouseScroll", on_mouse_scroll, false);  
    window.addEventListener("mousewheel", on_mouse_scroll, false);        
    window.onmousewheel = document.onmousewheel = on_mouse_scroll;
    
    everything = $("#everything")[0];
    
    doc = everything.getBBox();
    winw = window.innerWidth; winh = window.innerHeight;
    
    // Set the scale 
    if (winw / winh > doc.width / doc.height)
    {
        everything.vScale = 0.9 * window.innerHeight / doc.height;
    } else
    {
        everything.vScale = 0.9 * window.innerWidth / doc.width;
    }
    
    zoom_value = Math.log(everything.vScale)*20;
    
    // Center the document!
    doc_window_w = everything.vScale * doc.width;
    doc_window_h = everything.vScale * doc.height;
    y = window.innerHeight / 2 - doc_window_h / 2;
    x = window.innerWidth  / 2 - doc_window_w / 2;
    main_trans = everything.vTranslate = [x, y];
    
    update_transform();
       
    viewdata = get_mcvizns("viewdata");
    eventdata = get_mcvizns("eventdata");
    ui = $("#interface");
    particle_selector = $("#selected-particle");
    
    function get_x(element) {
        if (element.x)  return element.x.baseVal.value;
        if (element.cx) return element.cx.baseVal.value;
    }
    
    function get_y(element) {
        if (element.y)  return element.y.baseVal.value;
        if (element.cy) return element.cy.baseVal.value;
    }
    
    function hover_particle(event) {
        use_element = get_element(event);
        
        // Get interesting references
        reference = $(use_element).attr("mcviz:r").split("_");
        particle_ref = reference[0];
        
        // selector_positioning_element = $("ellipse[mcviz\\:r=" + particle_ref + "]");
        // if (selector_positioning_element) use_element = selector_positioning_element[0];
        
        particle_selector.attr("cx", get_x(use_element));
        particle_selector.attr("cy", get_y(use_element));
        particle_selector.attr("transform", $(use_element).attr("transform"));
        
        
        particle_element = viewdata.find("particle[id=" + particle_ref + "]");
        vertex_in  = viewdata.find("vertex[id=" + particle_element.attr("vin") + "]");
        vertex_out = viewdata.find("vertex[id=" + particle_element.attr("vout") + "]");
        
        ui.find("#id")  .text(particle_element.attr("id"));
        ui.find("#vin") .text(particle_element.attr("vout"));
        ui.find("#vout").text(particle_element.attr("vin"));
        
        represented_particles = particle_element.attr("event").split(" ");
        represented_particles = $.map(represented_particles, 
            function(value) { 
                return eventdata.find("particle[id=" + value + "]"); 
            });
        
        
        ui.find("#contents").text("Eta: " + represented_particles[0].attr("eta"));
        
        return;
        items = ["id", "pdgid", "pt", "phi", "e", "m"];
        for (var i = 0; i < items.length; i++) {
            var value = items[i];
            ui.find("#" + value).text(particle_element.attr(value));
        }
        
    }
    
    // pt: eventdata.find("particle").map(function(i, p) { return $(p).attr(""); })
    
    $("use").hover(hover_particle);
    //$("ellipse[mcviz\\:r]").hover(hover_particle);
    
    $("button.#reset").click(function(event) {
        $("[mcviz\\:r]").attr("opacity", null);
    });
    
    function filter_particles(func) {
        $("[mcviz\\:r]").attr("opacity", 0.25);
        
        good_ids = eventdata.find("particle")
            .filter(func)
            .map(function(i, p) { return $(p).attr("id"); });
        
        for (var i = 0; i < good_ids.length; i++) {
            $("[mcviz\\:r=P" + good_ids[i] + "]").attr("opacity", null);
        }
    }
    
    $("button.#hidelowpt").click(function(event) {
        //viewdata.find("particle").filter(function(p) { return p.attr(pt) < 
        filter_particles(function(i, p) { return $(p).attr("pt") > 10; });
    });
    $("button.#hidehieta").click(function(event) {
        //viewdata.find("particle").filter(function(p) { return p.attr(pt) < 
        filter_particles(function(i, p) { return Math.abs($(p).attr("eta")) < 2; });
    });
}

function get_mcvizns(what) {
    var result = null;
    result = $(what);
    if (result.size()) return result;
    result = $("mcviz\\:" + what);
    return result;
}

function get_element(evt) {
    var el = null;
    if (evt.target.correspondingUseElement)
        el = evt.target.correspondingUseElement;
    else
        el = evt.target;
    return el
}

function update_transform() 
{
    trans = everything.vTranslate; scale = everything.vScale;
    everything.setAttribute(
        "transform", 
        "translate(" + trans[0] + ", " + trans[1] + ") " +
        "scale(" + scale + ", " + scale + ")");
}

function on_mouse_scroll(ev) 
{
    if (ev.wheelDelta) delta = ev.wheelDelta / 120 * 3;
    if (ev.detail) delta = -ev.detail;
    update_zoom(delta, ev.clientX, ev.clientY);
    
    // Prevent usual window scrolling
    ev.preventDefault();
}

function update_zoom(scroll, ex, ey) 
{
    s_before = s = everything.vScale;
    new_zoom = zoom_value+scroll;
    
    //if (new_zoom > 55) return; // too far zoomed in
    
    s = Math.exp(new_zoom / 20);
    if (s < 0.01) return; // Too far zoomed out (primitive)
    
    zoom_value += scroll;
    everything.vScale = s;
    
    // Translate canvas to keep mouse stationary with respect to image
    main_trans[0] += (s / s_before - 1)*(main_trans[0] - ex);
    main_trans[1] += (s / s_before - 1)*(main_trans[1] - ey);
    
    update_transform();
}

function on_mouse_down(ev) 
{
    // ignore if something else is already going on
    if (cur_trans != null)
        return;

    cur_trans = { s: everything.vScale, t: everything.vTranslate,
                  x: ev.clientX, y: ev.clientY };
       
    ev.preventDefault();
}

function on_mouse_move(ev) 
{
    if (ev.button != 0)
        alert(ev.button);
    ex = ev.clientX; ey = ev.clientY;
    
    if (!("cur_trans" in window) || cur_trans == null)
    {
        return;
    }

    // If we get here, the mouse is held down.

    main_trans[0] += ex - cur_trans.x; cur_trans.x = ex;
    main_trans[1] += ey - cur_trans.y; cur_trans.y = ey;

    update_transform();
    ev.preventDefault();
}

function on_mouse_up(ev) 
{
    // Transform complete
    cur_trans = null;
    ev.preventDefault();
}
