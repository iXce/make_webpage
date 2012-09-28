var r = Raphael("plotholder{{ 'plotid'|inc }}");
var chart = r.linechart(
    10, 10,
    390, 180,
    {{ item.xdata }},
    {{ item.ydata }},
    {
       axis: "0 0 1 1",
       smooth: true,
       {% if item.options %}{{ item.options }}{% endif %}
     });

