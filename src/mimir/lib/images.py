from io import BytesIO
import os.path

from PIL import Image
import requests

from ..models import FetchedImage

EXTS = {
    "JPEG": ".jpeg",
    "PNG": ".png",
    "GIF": ".gif",
    "WEBP": ".webp",
}


class MirrorError(Exception):
    pass


class NotAnImage(MirrorError):
    pass


class CantConnect(MirrorError):
    pass


def open_and_resize_image(img_bytes: BytesIO):
    original_threshold = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = original_threshold * 4
    try:
        img = Image.open(img_bytes)
        img.thumbnail((3000, 3000), resample=Image.LANCZOS)
        out_bytes = BytesIO()
        img.save(out_bytes, img.format)
        return out_bytes, img
    finally:
        Image.MAX_IMAGE_PIXELS = original_threshold


def open_image(r: requests.Response):
    img_bytes = BytesIO(r.content)
    try:
        img = Image.open(img_bytes)
    except OSError as err:
        raise NotAnImage(err)
    except Image.DecompressionBombError:
        return open_and_resize_image(img_bytes)
    return img_bytes, img


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
            requests.exceptions.ReadTimeout,
        ) as err:
            raise CantConnect(err)
        # Content-Type may not be in headers!!! but if not, let's just try opening it
        # since it was in an <img> tag anyway
        if "Content-Type" in r.headers and not r.headers["Content-Type"].startswith(
            "image"
        ):
            raise NotAnImage(r.headers["Content-Type"])
        img_bytes, img = open_image(r)
        ext = EXTS[img.format]
        address = request.hashfs.put(img_bytes, ext)
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
