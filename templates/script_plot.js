var r = Raphael("plotholder{{ itemid }}");
var div = $("#plotholder{{ itemid }}");
var chart = r.linechart(
    20, 10,
    div.width() - 20, div.height() - 20,
    {{ item.xdata }},
    {{ item.ydata }},
    {
       axis: "0 0 1 1",
       smooth: true,
       {% if item.options %}{{ item.options }}{% endif %}
     });
{% if item.labels %}
var labels = [{% for label in item.labels %}"{{ label }}", {% endfor %}];
chart.labels = r.set();
var x = 15; var h = 5;
for( var i = 0; i < labels.length; ++i ) {
  var clr = chart.lines[i].attr("stroke");
  chart.labels.push(r.set());
  chart.labels[i].push(r["circle"](x + 5, h, 5)
                       .attr({fill: clr, stroke: "none"}));
  chart.labels[i].push(txt = r.text(x + 15, h, labels[i])
                       .attr(Raphael.g.txtattr)
                       .attr({fill: "#000", "text-anchor": "start"}));
  x += 15 + txt.getBBox().width + 10;
};
{% endif %}
