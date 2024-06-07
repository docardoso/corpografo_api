from marshmallow import Schema, fields

class PlainCorpusSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)

class PlainDocumentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    content = fields.String(required=True)

class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)

class PlainUserSchema(LoginSchema):
    id = fields.Int(dump_only=True)
    real_name = fields.String(required=True)
    email = fields.String(required=True)
    access_level = fields.Int(required=True)

class CorpusSchema(PlainCorpusSchema):
    documents = fields.List(fields.Nested(PlainDocumentSchema()), dump_only=True)
    user_id = fields.Int(required=True, dump_only=True)
    user = fields.Nested(PlainUserSchema(), dump_only=True)

class DocumentSchema(PlainDocumentSchema):
    corpus_id = fields.Int(required=True)
    corpus = fields.Nested(PlainCorpusSchema(), dump_only=True)

class UserSchema(PlainUserSchema):
    corpora = fields.List(fields.Nested(PlainCorpusSchema()), dump_only=True)
