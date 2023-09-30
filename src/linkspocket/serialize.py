import json 
from .oci.core import descriptor, manifest
import typing as T


class OciEncoder(json.JSONEncoder):
    def default(self, obj: object) -> T.Any:
        if isinstance(obj, descriptor.Digest):
            return str(obj)
        if isinstance(obj, descriptor.Descriptor):
            d = {
                "digest": obj.digest,
                "size": obj.bytes,
                "mediaType": obj.content_type,
            }
            if obj.annotations:
                d["annotations"] = obj.annotations.copy()
            return d
        if isinstance(obj, manifest.Manifest):
            m = {
                "schemaVersion": 2,
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "config": obj.config,
                "layers": [d for d in obj.layers],
            }
            return m
        super().default(obj)
