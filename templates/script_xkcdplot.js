var plot = xkcdplot("{{ item.xlabel }}", "{{ item.ylabel }}", "{{ item.title }}");
plot("#xkcdplotholder{{ itemid }}");

{% for curve in item.curves %}
    plot.plot([{% for p in curve %}{x: {{p.x}}, y: {{p.y}}},{% endfor %}]{% if curve.color %}, {stroke: "{{ curve.color }}"}{% endif %});
{% endfor %}

plot.xlim([{{ item.minx }}, {{ item.maxx }}]).ylim([{{ item.miny }}, {{ item.maxy }}]).draw();
