from marshmallow import Schema, fields


class Writeup(Schema):
    id = fields.Integer()
    author_slug = fields.String()
    writeup_slug = fields.String()
    title = fields.String()
    status = fields.String()
    published = fields.Boolean()
    offensive_content = fields.Boolean()
    triggery_content = fields.Boolean()

    posts = fields.Nested(
        'WriteupPost',
        only=['author', 'index', 'ordinal', 'title', 'url'],
        many=True)


class WriteupPost(Schema):
    id = fields.Integer()
    writeup_id = fields.Integer()
    author = fields.String()
    index = fields.Integer()
    ordinal = fields.String()
    title = fields.String()
    url = fields.Url()

    versions = fields.Nested(
        'WriteupPostVersion',
        only=['version', 'active', 'html', 'created_at', 'edit_summary'],
        many=True)


class WriteupPostVersion(Schema):
    id = fields.Integer()
    writeuppost_id = fields.Integer()
    threadpost_id = fields.Integer()
    html = fields.String()
    created_at = fields.DateTime()
    version = fields.Integer()
    active = fields.Boolean()
    edit_summary = fields.String()
