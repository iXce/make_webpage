{% set thisitem = item %}
    {% if item.header %}
            {% for item in item.header %}
                {% include "script_type_switch.html" %}
            {% endfor %}
    {% endif %}
    <tbody>
    {% for item0 in item.rows %}
        <tr>
        {% if item0 is sequence and not item0 is string and not item0 is mapping %}
            {% for item in item0 %}
                {% include "script_type_switch.html" %}
            {% endfor %}
        {% else %}
            {% with item = item0 %}
                {% include "script_type_switch.html" %}
            {% endwith %}
        {% endif %}
    {% endfor %}
{% set item = thisitem %}
