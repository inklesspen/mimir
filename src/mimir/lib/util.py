import lxml.etree
import lxml.html


def sane_prettify(soup):
    # produces unicode string
    doc = soup.decode(formatter="html")
    # we have to roundtrip to ascii and back, creating xml entities for non-ascii chars
    # this is because lxml currently barfs on emoji, and possibly other unicode chars
    # that lie outside the BMP.
    doc = doc.encode("ascii", "xmlcharrefreplace").decode("ascii")
    frag = lxml.html.fragment_fromstring(doc, create_parent="destroy")
    # frag now contains all the tags, wrapped in a tag called destroy.
    # Previously we would iterate over it and stringify each bit, but this approach
    # is actually simpler, and introduces fewer modifications.
    return (
        lxml.etree.tostring(frag, encoding="unicode", pretty_print=True)
        .rstrip()[9:-10]
        .strip()
    )
