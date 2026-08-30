"""Upload CMS images to Vercel Blob when BLOB_READ_WRITE_TOKEN is set.

The function filesystem is ephemeral, so local media/ cannot be the production
store. The ImageField may hold either a relative path (local) or a full Blob URL.
"""

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class VercelBlobStorage(Storage):
    def _open(self, name, mode="rb"):
        from django.core.files.base import ContentFile

        with urlopen(self.url(name), timeout=30) as response:
            return ContentFile(response.read(), name=name)

    def _save(self, name, content):
        import vercel_blob

        payload = content.read()
        result = vercel_blob.put(
            name.replace("\\", "/"),
            payload,
            {
                "addRandomSuffix": False,
                "allowOverwrite": True,
            },
            timeout=60,
        )
        if isinstance(result, dict):
            return result.get("url") or result.get("pathname") or name
        return getattr(result, "url", None) or name

    def url(self, name):
        if not name:
            return ""
        if name.startswith("http://") or name.startswith("https://"):
            return name
        return settings.MEDIA_URL.rstrip("/") + "/" + name.lstrip("/")

    def exists(self, name):
        if not name:
            return False
        try:
            request = Request(self.url(name), method="HEAD")
            with urlopen(request, timeout=8) as response:
                return 200 <= response.status < 400
        except (HTTPError, URLError, TimeoutError, OSError):
            return False

    def delete(self, name):
        if not name:
            return
        import vercel_blob

        url = self.url(name)
        vercel_blob.delete(url)

    def size(self, name):
        return 0

    def listdir(self, path):
        return [], []
