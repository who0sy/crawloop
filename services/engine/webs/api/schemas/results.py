# -*- coding: utf-8 -*-
from webargs import fields

result_by_url_schema = {
    "url": fields.Url(required=True),
    "fields": fields.DelimitedList(fields.Str(), missing=[])
}

result_by_id_schema = {
    "result_id": fields.Int(required=True)
}

get_screenshot_schema = {
    'screenshot_id': fields.Str(required=True)
}

download_har_file_schema = {
    'har_uuid': fields.Str(required=True)
}

get_favicon_schema = {
    'favicon_md5': fields.Str(required=True)
}

get_small_schema = {
    **get_screenshot_schema,
    'wide': fields.Int(missing=272),
    'high': fields.Int(missing=165)
}
