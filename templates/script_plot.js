nv.addGraph(function() {
    var chart = nv.models.lineChart();

    chart.options({
        showXAxis: true,
        showYAxis: true,
        {% if not item.tooltips %}tooltips: false,{% endif %}
    });

    {% if item.title %}chart.margin({top: 80, left: 100});
    {% else %}chart.margin({left: 100});{% endif%}

    {% if item.xlabel %}chart.xAxis
            .axisLabel("{{ item.xlabel }}");{% endif%}

    {% if item.ylabel %}chart.yAxis
            .axisLabel("{{ item.ylabel }}");{% endif%}

    {% if item.extrascript %}{{ item.extrascript }}{% endif %}

    {% if "minx" in item and "maxx" in item %}chart.forceX([{{ item.minx }}, {{ item.maxx }}]);{% endif %}

    {% if "miny" in item and "maxy" in item %}chart.forceY([{{ item.miny }}, {{ item.maxy }}]);{% endif %}

    d3.select("#td{{ itemid }} svg")
        .datum({{ item.data }})
        .transition().duration(500).call(chart);

    {% if item.title %}
    d3.select('#td{{ itemid }} svg')
      .append("text")
      .attr("x", 20)
      .attr("y", 20)
      .attr("text-anchor", "left")
      .text("{{ item.title }}");
    {% endif %}

    nv.utils.windowResize(
            function() {
                chart.update();
            }
        );

    return chart;
});
