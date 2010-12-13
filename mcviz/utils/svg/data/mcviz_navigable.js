const SVG = "http://www.w3.org/2000/svg";
const XLINK = "http://www.w3.org/1999/xlink";

var main_trans = null, cur_trans = null;
var everything = null, marker = null;
var zoom_value = 0;
var ex = 0, ey = 0, mouse_position_in_lumispace = 0;

$(function() {
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
    
});


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
