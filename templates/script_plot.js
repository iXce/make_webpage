nv.addGraph(function() {
    var chart = nv.models.lineChart();

    chart.options({
        showXAxis: true,
        showYAxis: true,
        tooltips: false,
    });

    chart.margin({left: 100});

    {% if item.xlabel %}chart.xAxis
            .axisLabel("{{ item.xlabel }}");{% endif%}

    {% if item.ylabel %}chart.yAxis
            .axisLabel("{{ item.ylabel }}");{% endif%}

    {% if "minx" in item and "maxx" in item %}chart.forceX([{{ item.minx }}, {{ item.maxx }}]);{% endif %}

    {% if "miny" in item and "maxy" in item %}chart.forceY([{{ item.miny }}, {{ item.maxy }}]);{% endif %}

    d3.select("#td{{ itemid }} svg")
        .datum({{ item.data }})
        .transition().duration(500).call(chart);

    nv.utils.windowResize(
            function() {
                chart.update();
            }
        );

    return chart;
});
