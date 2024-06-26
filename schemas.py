from marshmallow import Schema, fields

class PlainCorpusSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)

class PlainDocumentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    content = fields.String(required=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)

class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    access_level = fields.Int(required=True)
    email = fields.Email(required=True)

class CorpusSchema(PlainCorpusSchema):
    documents = fields.List(fields.Nested(PlainDocumentSchema()), dump_only=True)
    users = fields.List(fields.Nested(PlainUserSchema()), dump_only=True)

class DocumentSchema(PlainDocumentSchema):
    corpora = fields.List(fields.Nested(PlainCorpusSchema()), dump_only=True)
    users = fields.List(fields.Nested(PlainUserSchema()), dump_only=True)

class UserSchema(PlainUserSchema):
    corpora = fields.List(fields.Nested(PlainCorpusSchema()), dump_only=True)
    documents = fields.List(fields.Nested(PlainDocumentSchema()), dump_only=True)
