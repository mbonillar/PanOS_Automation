
from flask import render_template, request
from app.scripts.rest_log_query import QueryLogs
from app.models.log import LogForm
from app.log import bp
import sys
import json


@bp.route('/', methods=('GET', 'POST'))
def index():
    # Test code without querying Panorama
    # with open('log_output.json') as log_file:
    #     logs_text = log_file.read()
    # log_results = json.loads(logs_text)
    # print(log_results)

    form = LogForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if request.form['output_type'] == 'simple':
                template_type = 'log/results.html'
            else:
                template_type = 'log/detailed_results.html'

            return render_template(
                template_type,
                source_ip=form.source_ip.data,
                dest_ip=form.dest_ip.data,
                dest_port=form.dest_port.data,
                log_results=QueryLogs.run_query(
                    form.source_ip.data, form.dest_ip.data, form.dest_port.data, request.form['output_type'],
                ),
                # log_results=log_results,
            )
    return render_template('log/index.html', form=form)
