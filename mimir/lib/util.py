import lxml.etree
import lxml.html


def sane_prettify(soup):
    # produces unicode string
    doc = soup.decode(formatter="html")
    frag = lxml.html.fragment_fromstring(doc, create_parent='destroy')
    # frag now contains all the tags, wrapped in a tag called destroy.
    # we can iterate over it and stringify each bit. we must remove whitespace at the end, though.
    html_parts = [lxml.etree.tostring(x, encoding='unicode', pretty_print=True).rstrip() for x in frag]
    return '\n'.join(html_parts).strip()
