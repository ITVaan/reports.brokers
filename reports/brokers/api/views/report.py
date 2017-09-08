import os


from pyramid.response import FileResponse
from pyramid.view import view_config, view_defaults

from reports.brokers.api.views.reports_generator import GeneratorOfReports
from logging import getLogger
LOGGER = getLogger("{}.init".format(__name__))


@view_defaults(route_name='report')
class ReportView(object):
    def __init__(self, request):
        self.request = request
        self.ROOT_DIR = os.path.dirname(__file__)
        self.REPORTS_PATH = request.registry.settings['result_dir']

    @view_config(request_method='GET')
    def generate(self):
        data = dict(self.request.GET)

        reports_generator = GeneratorOfReports(
            start_report_period=data['start_report_period'],
            end_report_period=data['end_report_period'],
            report_number=data['report_number'],
            user_name=data['user_name'],
            password=data['password'],
            config=self.request.registry.settings
        )
        file_name = reports_generator.filename('.xlsx')
        file_path = os.path.join(self.REPORTS_PATH, file_name)

        response = FileResponse(
            path=file_path, request=self.request,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response.headers['Content-Disposition'] = ("attachment; filename={}".format(file_name))
        LOGGER.info("response.headers {}".format(response.headers))
        return response
