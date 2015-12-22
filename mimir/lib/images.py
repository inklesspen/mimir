from ..models import FetchedImage
from PIL import Image
from io import BytesIO
import requests

EXTS = {
    'JPEG': '.jpeg',
    'PNG': '.png',
    'GIF': '.gif',
}


class MirrorError(Exception):
    pass


class NotAnImage(MirrorError):
    pass


class CantConnect(MirrorError):
    pass


def mirror_image(request, img_tag, referer):
    did_fetch = False
    if 'data-mirrored' in img_tag.attrs:
        img_src = img_tag['data-orig-src']
    else:
        img_src = img_tag['src']
    img_query = request.db_session.query(FetchedImage).filter_by(orig_url=img_src)
    prefetched = img_query.one_or_none()
    if prefetched is not None:
        address = request.hashfs.get(prefetched.id)
        if address is None:
            request.db_session.delete(prefetched)
            prefetched = None
        else:
            img = Image.open(request.hashfs.open(address.id))
    if prefetched is None:
        # this is not an else, since prefetched may have become None in the earlier block
        did_fetch = True
        try:
            r = requests.get(img_src, headers={'referer': referer}, timeout=5)
        except requests.exceptions.ConnectionError as err:
            raise CantConnect(err)
        if not r.headers['Content-Type'].startswith('image'):
            raise NotAnImage(r.headers['Content-Type'])
        bytes = BytesIO(r.content)
        img = Image.open(bytes)
        ext = EXTS[img.format]
        address = request.hashfs.put(bytes, ext)
        request.db_session.add(FetchedImage(id=address.id, orig_url=img_src))
    img_tag['data-mirrored'] = 'mirrored'
    img_tag['data-orig-src'] = img_src
    img_tag['data-width'] = img.width
    img_tag['data-height'] = img.height
    img_tag['src'] = request.route_path('image', path=address.relpath)
    return did_fetch
