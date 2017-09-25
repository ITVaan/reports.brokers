from datetime import datetime
from logging import getLogger

import os

from pyramid.response import FileResponse
from pyramid.view import view_config, view_defaults
from reports.brokers.api.views.reports_generator import GeneratorOfReports

LOGGER = getLogger("{}.init".format(__name__))


@view_defaults(route_name='report')
class ReportView(object):
    def __init__(self, request):
        self.request = request
        self.ROOT_DIR = os.path.dirname(__file__)
        self.REPORTS_PATH = request.registry.settings['result_dir']

    @view_config(request_method='GET', permission='view')
    def generate(self):
        # import pdb;pdb.set_trace()
        data = dict(self.request.GET)
        start_period = datetime.strptime(str(data['start_report_period']), '%d.%m.%Y')
        end_period = datetime.strptime(str(data['end_report_period']), '%d.%m.%Y')
        report_number = data['report_number']
        for file in os.listdir(self.REPORTS_PATH):
            if os.path.splitext(file)[1] == '.xlsx':
                # import pdb;pdb.set_trace()
                file_start_date = datetime.strptime(str(file.split('_start_date_')[1].split('_end_date_')[0]),
                                                    '%Y-%m-%d-%H-%M-%S')
                file_end_date = datetime.strptime(str(file.split('_end_date_')[1].split('_report_number_')[0]),
                                                  '%Y-%m-%d-%H-%M-%S')
                file_reports_number = str(file.split('_report_number_')[1][0])
                if start_period == file_start_date and end_period == file_end_date and report_number == file_reports_number:
                    file_name = file
                    break
        else:
            reports_generator = GeneratorOfReports(start_report_period=data['start_report_period'],
                                                   end_report_period=data['end_report_period'],
                                                   report_number=data['report_number'],
                                                   user_name=data['user_name'],
                                                   password=data['password'],
                                                   config=self.request.registry.settings)
            file_name = reports_generator.filename('.xlsx')

        file_path = os.path.join(self.REPORTS_PATH, file_name)

        response = FileResponse(path=file_path, request=self.request,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response.headers['Content-Disposition'] = ("attachment; filename={}".format(file_name))
        LOGGER.info("response.headers {}".format(response.headers))
        return response
