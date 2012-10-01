{% set thisitem = item %}
{% do 'stacktabid'|inc(0, None, True) %}
{% for item in thisitem.stack %}
{% include "script_type_switch.html" %}
{% endfor %}
{% set item = thisitem %}
