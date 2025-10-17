from app.suggestions import bp
from app.models.suggestions_form import SuggestionsForm
from flask import render_template, request, redirect, url_for, current_app
from flask_mail import Message
from app.extensions import mail

@bp.route('/')
def index():
    form = SuggestionsForm()
    if form.validate_on_submit():
        return render_template('suggestions/submit.html')
    return render_template('suggestions/index.html', form=form)

@bp.route('/thanks')
def thanks():
    return render_template('suggestions/thank_you.html')

@bp.route('/submit', methods=['GET', 'POST'])
def submit():

    message = request.form['suggestion']
    print(message)
    msg = Message(
        'PANOS Log Collector Flask App - Suggestion from a User',
        sender='FWOps@kohls.com',
        recipients=['miguel.bonilla@kohls.com',],
    )
    msg.body = f'Suggestion: {message}'
    with current_app.app_context():
        mail.send(msg)
    return redirect(url_for('suggestions.thanks'))
