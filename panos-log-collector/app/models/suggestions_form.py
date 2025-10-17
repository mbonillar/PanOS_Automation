from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    ValidationError,
    TextAreaField,
)
from wtforms.validators import InputRequired, Optional

class SuggestionsForm(FlaskForm):
    message = TextAreaField(
        'Your feedback here...',
        validators=[
            InputRequired(),
        ],
    )