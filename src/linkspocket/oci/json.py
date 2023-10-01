import json 
import typing as T
from .core import descriptor, manifest

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
            if obj.annotations:
                m["annotations"] = obj.annotations.copy()
            return m
        super().default(obj)
