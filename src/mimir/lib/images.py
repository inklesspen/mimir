from io import BytesIO
import os.path

from PIL import Image
import requests

from ..models import FetchedImage

EXTS = {
    "JPEG": ".jpeg",
    "PNG": ".png",
    "GIF": ".gif",
}


class MirrorError(Exception):
    pass


class NotAnImage(MirrorError):
    pass


class CantConnect(MirrorError):
    pass


def mirror_image(request, img_tag, referer, cred):
    did_fetch = False
    if "data-mirrored" in img_tag.attrs:
        img_src = img_tag["data-orig-src"]
    else:
        img_src = img_tag["src"]
    use_cred = "forums.somethingawful.com" in img_src
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
            r_kwargs = {"headers": {"referer": referer}, "timeout": 5}
            if use_cred:
                r_kwargs["cookies"] = cred.cookies
            r = requests.get(img_src, **r_kwargs)
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.TooManyRedirects,
        ) as err:
            raise CantConnect(err)
        if not r.headers["Content-Type"].startswith("image"):
            raise NotAnImage(r.headers["Content-Type"])
        bytes = BytesIO(r.content)
        try:
            img = Image.open(bytes)
        except OSError as err:
            raise NotAnImage(err)
        ext = EXTS[img.format]
        address = request.hashfs.put(bytes, ext)
        request.db_session.add(FetchedImage(id=address.id, orig_url=img_src))
    img_tag["data-mirrored"] = "mirrored"
    img_tag["data-orig-src"] = img_src
    img_tag["data-width"] = img.width
    img_tag["data-height"] = img.height
    img_tag["src"] = make_image_path(address)
    return did_fetch


def make_image_path(address):
    ext = os.path.splitext(address.relpath)[1]
    return "".join([address.id, ext])
