from marshmallow import (
    fields,
    post_load,
    pre_load,
    Schema,
    validates_schema,
    ValidationError,
)

from .classes import Writeup, WriteupPost


# from https://github.com/marshmallow-code/marshmallow/issues/1391
class TrimmedString(fields.String):
    def _deserialize(self, value, *args, **kwargs):
        if hasattr(value, "strip"):
            value = value.strip()
        return super()._deserialize(value, *args, **kwargs)


class AssignWPV(Schema):
    writeup_id = fields.Integer()
    writeup_post_id = fields.Integer()
    writeup_title = TrimmedString()
    writeup_author = TrimmedString()
    post_title = TrimmedString()
    post_html = fields.String()

    @pre_load
    def handle_new_ids(self, in_data, **kwargs):
        # Probably a better way to do this, but this'll work for now
        if "writeup_id" in in_data and in_data["writeup_id"] == "w":
            del in_data["writeup_id"]
        if "writeup_post_id" in in_data and in_data["writeup_post_id"] == "wp":
            del in_data["writeup_post_id"]
        return in_data

    @post_load
    def attach_models(self, data, **kwargs):
        db_session = self.context["request"].db_session
        if "writeup_id" in data:
            data["writeup"] = (
                db_session.query(Writeup)
                .filter_by(status="ongoing", id=data["writeup_id"])
                .one()
            )
            del data["writeup_id"]

        if "writeup_post_id" in data:
            if "writeup" not in data:
                raise ValidationError("Cannot have a writeup_post_id without a writeup")

            data["writeup_post"] = (
                db_session.query(WriteupPost)
                .with_parent(data["writeup"])
                .filter_by(id=data["writeup_post_id"])
                .one()
            )
            del data["writeup_post_id"]

        return data

    @validates_schema
    def mutually_exclusive(self, data, **kwargs):
        # called after pre_load but before post_load
        if "writeup_id" in data and (
            "writeup_title" in data or "writeup_author" in data
        ):
            raise ValidationError(
                "Cannot specify writeup details when writeup_id present"
            )
        if "writeup_post_id" in data and "post_title" in data:
            raise ValidationError(
                "Cannot specify writeup post details when writeup_post_id present"
            )


class EditWriteup(Schema):
    author_slug = TrimmedString()
    writeup_slug = TrimmedString()
    title = TrimmedString()
    author = TrimmedString()
    status = fields.String()
    published = fields.Boolean(missing=False)
    offensive_content = fields.Boolean(missing=False)
    triggery_content = fields.Boolean(missing=False)


class EditWriteupPost(Schema):
    title = TrimmedString()
    author = TrimmedString()
    ordinal = fields.Integer()
    published = fields.Boolean(missing=False)
