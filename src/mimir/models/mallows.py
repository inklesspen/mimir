from marshmallow import (
    fields,
    post_load,
    pre_load,
    Schema,
    ValidationError,
    validates_schema,
)

from .classes import Writeup, WriteupPost


class AssignWPV(Schema):
    writeup_id = fields.Integer()
    writeup_post_id = fields.Integer()
    writeup_title = fields.String()
    writeup_author = fields.String()
    post_title = fields.String()
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
