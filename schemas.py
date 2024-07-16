from marshmallow import Schema, fields

class PlainAuthorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    url = fields.String()
    email = fields.String()
    organization_id = fields.Int(allow_none=True)

class PlainCorpusSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)

class LightweightDocumentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)

class PlainDocumentSchema(LightweightDocumentSchema):
    content = fields.String(required=True)
    input_file = fields.String()
    citation = fields.String(allow_none=True)
    language_id = fields.Int(allow_none=True)
    source_id = fields.Int(allow_none=True)
    publisher_id = fields.Int(allow_none=True)

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
    authors = fields.List(fields.Nested(PlainAuthorSchema()), dump_only=True)

class UserSchema(PlainUserSchema):
    corpora = fields.List(fields.Nested(PlainCorpusSchema()), dump_only=True)
    documents = fields.List(fields.Nested(PlainDocumentSchema()), dump_only=True)

class PlainLanguageSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)

class LanguageSchema(PlainLanguageSchema):
    documents = fields.List(fields.Nested(LightweightDocumentSchema()), dump_only=True)

class PlainOrganizationSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    url = fields.String()
    email = fields.String()


class OrganizationSchema(PlainOrganizationSchema):
    documents = fields.List(fields.Nested(LightweightDocumentSchema()), dump_only=True)

class AuthorSchema(PlainAuthorSchema):
    documents = fields.List(fields.Nested(LightweightDocumentSchema()), dump_only=True)