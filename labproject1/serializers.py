from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    name = fields.String(required=True)

class CategorySchema(Schema):
    name = fields.String(required=True)

class RecordSchema(Schema):
    category_id = fields.Integer(required=True, validate=validate.Range(min=0))
    user_id = fields.Integer(required=True, validate=validate.Range(min=0))
    sum = fields.Float(required=True, validate=validate.Range(min=0.0))

class UserCategorySchema(Schema):
    name = fields.String(required=True)
    user_id = fields.Integer(required=True, validate=validate.Range(min=0))
    is_public = fields.Boolean(required=True)
