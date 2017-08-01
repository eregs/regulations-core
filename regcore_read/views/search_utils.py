from webargs import fields

search_args = {
    'q': fields.Str(required=True),
    'version': fields.Str(missing=None),
    'regulation': fields.Str(missing=None),
    'is_root': fields.Bool(missing=None),
    'is_subpart': fields.Bool(missing=None),
    'page': fields.Int(missing=0)
}
