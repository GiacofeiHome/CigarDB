# project/server/cigar/forms.py


from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class AddCigar(Form):
    hash = StringField('Unique Hash', [DataRequired(), Length(min=64, max=64)])

