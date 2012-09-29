function heatmap_maker(selector, width, height, min, max) {
  return function(heatmap) {
    var dx = heatmap[0].length,
        dy = heatmap.length;

    if (height == 0) height = width * dy / dx;
    if (width == 0) width = height * dx / dy;

    d3.select(selector + " img")
        .on("mouseover", onMouseover).on("mousemove", onMousemove).on("mouseout", onMouseout);

    var x2 = d3.scale.linear()
        .domain([0, width])
        .range([0, dx]);

    var y2 = d3.scale.linear()
        .domain([0, height])
        .range([0, dy]);

    function onMouseover() {
        var mouse = d3.mouse(this);
        var curx = mouse[0], cury = mouse[1];
        value = heatmap[Math.floor(y2(cury))][Math.floor(x2(curx))];
        tooltip =  $("<div class='heatmap-tooltip'></div>");
        tooltip.html("<div class='heatmap-tooltipFill'><p>" + value + "</p></div>");
        tooltip.css({
          left: curx + 5 + $(selector).offset().left,
          top: cury + 5 + $(selector).offset().top
        });
        $(selector).append(tooltip);
    }
    
    function onMousemove() {
        var mouse = d3.mouse(this);
        var curx = mouse[0], cury = mouse[1];
        value = heatmap[Math.floor(y2(cury))][Math.floor(x2(curx))];
        $(".heatmap-tooltip").css({
          left: curx + 5 + $(selector).offset().left,
          top: cury + 5 + $(selector).offset().top
        });
        $(".heatmap-tooltip").find("p").eq(0).html(value);
    }
    
    function onMouseout() {
        $(".heatmap-tooltip").remove();
    }
  }
}
