from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    ValidationError,
)
from wtforms.validators import InputRequired, Optional

from ipaddress import IPv4Address, AddressValueError


class LogForm(FlaskForm):
    source_ip = StringField(
        'Source IP',
        validators=[InputRequired(), Optional(strip_whitespace=True)],
    )
    dest_ip = StringField(
        'Destination IP',
        validators=[Optional(strip_whitespace=True)],
    )
    dest_port = StringField(
        'Destination Port',
        validators=[
            Optional(strip_whitespace=True),
        ],
    )

    def validate_source_ip(form, field):
        try:
            IPv4Address(field.data)
        except AddressValueError:
            raise ValidationError('Enter a valid IPv4 Source host address')

    def validate_dest_ip(form, field):
        try:
            IPv4Address(field.data)
        except AddressValueError:
            raise ValidationError(
                'Enter a valid IPv4 Destination host address'
            )
