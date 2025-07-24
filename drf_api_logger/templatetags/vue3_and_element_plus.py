from django import template
from django.template.base import Node
from django.templatetags.static import static

register = template.Library()


class Vue3AndElementPlusNode(Node):
    child_nodelists = ()

    def render(self, context):
        return f"""
        <link rel="stylesheet" href="{static('drf_api_logger/css/elementPlus.css')}" />
        <script src="{static('drf_api_logger/js/vue3.js')}"></script>
        <script src="{static('drf_api_logger/js/elementPlus.js')}"></script>
        <script src="{static('drf_api_logger/js/zhCn.js')}"></script>
        """


@register.tag
def use_vue3_element_plus(parser, token):
    return Vue3AndElementPlusNode()
