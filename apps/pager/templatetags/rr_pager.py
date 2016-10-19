
import re
import math
import urllib

from django import template

register = template.Library()

PAGE_RANGE = 3


def _pager(num_results, params, page_size=10):
    def page_url(params, page):
        vars = params.copy()
        vars['page'] = page
        return '?'+vars.urlencode()
    page_min = 1
    page_max = int(math.ceil(float(num_results)/page_size))
    page_max = max(page_max, 1)
    try:
        page_current = int(params.get('page', '1'))
    except ValueError:
        page_current = 1
    page_current = max(1, page_current)
    page_current = min(page_current, page_max)

    range_min = max(1, page_current - PAGE_RANGE)
    range_max = min(page_max, page_current + PAGE_RANGE)

    pages = []
    pages.append(('Prev', page_current-1))
    if range_min > 1:
        pages.append((1, 1))
    if range_min == 3:
        pages.append((2, 2))
    if range_min > 3:
        pages.append(('...', None))
    for page in range(range_min, range_max+1):
        pages.append((page, page))
    if range_max < page_max-2:
        pages.append(('...', None))
    if range_max == page_max-2:
        pages.append((page_max-1, page_max-1))
    if range_max < page_max:
        pages.append((page_max, page_max))
    pages.append(('Next', page_current+1))

    # Process
    pages2 = []
    for name, page in pages:
        d = {'name': str(name)}
        if page is None:
            d['url'] = ''
        else:
            page = max(1, page)
            page = min(page, page_max)
            d['url'] = page_url(params, page)
        d['active'] = (page == page_current)
        d['meta'] = not d['name'].isdigit()
        pages2.append(d)

    pager = {}
    pager['page_max'] = page_max
    pager['pages'] = pages2
    return pager


@register.simple_tag(takes_context=True)
def rr_url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return '?'+urllib.urlencode(query)

@register.simple_tag(takes_context=True)
def rr_pager(context, **kwargs):
    num_result = int(kwargs.get('size', '0'))
    context['pager'] = _pager(num_result, context['request'].GET)
    return ''
