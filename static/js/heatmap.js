function heatmap_maker(selector, width, height, min, max) {
  return function(heatmap) {
    var dx = heatmap[0].length,
        dy = heatmap.length;

    if (height == 0) height = width * dy / dx;
    if (width == 0) width = height * dx / dy;
    // Fix the aspect ratio.
    // var ka = dy / dx, kb = height / width;
    // if (ka < kb) height = width * ka;
    // else width = height / ka;

    var x = d3.scale.linear()
        .domain([0, dx])
        .range([0, width]);

    var y = d3.scale.linear()
        .domain([0, dy])
        .range([height, 0]);

    var colormap = ["#0a0", "#6c0", "#ee0", "#eb4", "#eb9", "#fff"];
    var domain = [];
    for (i = 0; i < 6; i++) {
        domain[i] = min + i * (max - min) / 6;
    }
    var color = d3.scale.linear()
        .domain(domain)
        .range(colormap);

    d3.select(selector).append("canvas")
        .attr("width", dx)
        .attr("height", dy)
        .style("width", width + "px")
        .style("height", height + "px")
        .call(drawImage).on("mouseover", onMouseover).on("mousemove", onMousemove).on("mouseout", onMouseout);

    // Compute the pixel colors; scaled by CSS.
    function drawImage(canvas) {
      var context = canvas.node().getContext("2d"),
          image = context.createImageData(dx, dy);

      for (var y = 0, p = -1; y < dy; ++y) {
        for (var x = 0; x < dx; ++x) {
          var c = d3.rgb(color(heatmap[y][x]));
          image.data[++p] = c.r;
          image.data[++p] = c.g;
          image.data[++p] = c.b;
          image.data[++p] = 255;
        }
      }

      context.putImageData(image, 0, 0);
    }
    
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
