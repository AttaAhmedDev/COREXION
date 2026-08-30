"""Template tags that render database content with the design as fallback.

Each tag wraps the markup that was already in the page, so an empty or missing
section leaves the original wording and artwork untouched:

    <h1>{% cms_text sections "hero" "heading" %}CONTROL<br>COMPLEXITY.{% endcms_text %}</h1>
    <img src="{% cms_src sections "hero" "../../assets/images/room.png" %}">
    <span>{% cms_item sections "vision-cards2" 0 %}Integrity{% endcms_item %}</span>

Stored values are marked safe, because sections are authored in the Django admin
by staff and are expected to contain markup such as <br>.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

LIST_SEPARATORS = ("\r\n", "\n", ",")


def _section(sections, key):
    if not sections:
        return None
    return sections.get(key)


def _value(sections, key, field):
    section = _section(sections, key)
    if section is None:
        return None
    value = getattr(section, field, None)
    return value or None


def _items(sections, key):
    """Split a single stored field into list items, one per line or comma."""
    value = _value(sections, key, "paragraph")
    if not value:
        return []
    text = value.replace("\r\n", "\n")
    parts = [text]
    for separator in ("\n", ","):
        expanded = []
        for part in parts:
            expanded.extend(part.split(separator))
        parts = expanded
    return [part.strip() for part in parts if part.strip()]


class FallbackNode(template.Node):
    """Renders a stored value, or the wrapped markup when there is none."""

    def __init__(self, nodelist, resolve):
        self.nodelist = nodelist
        self.resolve = resolve

    def render(self, context):
        value = self.resolve(context)
        if value:
            return mark_safe(value)
        return self.nodelist.render(context)


def _parse_block(parser, token, end_tag, expected_args):
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) != expected_args + 1:
        raise template.TemplateSyntaxError(
            "%s takes %d arguments" % (tag_name, expected_args)
        )
    args = [parser.compile_filter(bit) for bit in bits[1:]]
    nodelist = parser.parse((end_tag,))
    parser.delete_first_token()
    return args, nodelist


@register.tag("cms_text")
def do_cms_text(parser, token):
    args, nodelist = _parse_block(parser, token, "endcms_text", 3)
    sections_arg, key_arg, field_arg = args

    def resolve(context):
        return _value(
            sections_arg.resolve(context),
            key_arg.resolve(context),
            field_arg.resolve(context),
        )

    return FallbackNode(nodelist, resolve)


@register.tag("cms_item")
def do_cms_item(parser, token):
    args, nodelist = _parse_block(parser, token, "endcms_item", 3)
    sections_arg, key_arg, index_arg = args

    def resolve(context):
        items = _items(sections_arg.resolve(context), key_arg.resolve(context))
        index = int(index_arg.resolve(context))
        return items[index] if 0 <= index < len(items) else None

    return FallbackNode(nodelist, resolve)


@register.simple_tag
def cms_src(sections, key, default=""):
    """URL of the section's uploaded image, or the design's own image path.

    The file is checked because a row can outlive its upload; falling back keeps
    the designed image on the page instead of serving a broken link.
    """
    section = _section(sections, key)
    if section is not None and section.image:
        name = section.image.name
        try:
            if name.startswith("http://") or name.startswith("https://"):
                return name
            if section.image.storage.exists(name):
                return section.image.url
        except Exception:
            return default
    return default
