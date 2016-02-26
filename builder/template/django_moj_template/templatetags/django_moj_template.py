import re

from django import template

register = template.Library()


class CollapseWhitespaceNode(template.Node):
    def __init__(self, node_list, stripped):
        self.node_list = node_list
        self.stripped = stripped

    def render(self, context):
        output = self.node_list.render(context)
        if isinstance(output, str):
            output = re.sub(r'\s+', ' ', output)
            if self.stripped:
                output = output.strip()
        return output


@register.tag(name='collapsewhitespace')
def do_collapse_whitespace(parser, token):
    args = token.split_contents()[1:]
    arg_count = len(args)
    stripped = False
    try:
        if arg_count == 1:
            if args[0] == 'stripped':
                stripped = True
            else:
                raise ValueError
        elif arg_count > 1:
            raise ValueError
    except ValueError:
        raise template.TemplateSyntaxError('"stripped" is the only valid argument')
    node_list = parser.parse(('endcollapsewhitespace',))
    parser.delete_first_token()
    return CollapseWhitespaceNode(node_list, stripped=stripped)
