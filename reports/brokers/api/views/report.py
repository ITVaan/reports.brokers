import os

from yaml import load
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import FileResponse
from pyramid.view import view_config, view_defaults

from reports.brokers.api.views.reports_generator import GeneratorOfReports


@view_defaults(route_name='report', renderer='json')
class ReportView:
    def __init__(self, request):
        self.request = request
        self.ROOT_DIR = os.path.dirname(__file__)

        init_file_path = os.path.join(self.ROOT_DIR, '..', '..', '..', '..', 'etc', 'reports_brokers.yaml')

        with open(init_file_path) as conf:
            _config = load(conf.read())

        self.conf = _config

        self.REPORTS_PATH = _config['main']['result_dir']

    @view_config(request_method='GET')
    def generate(self):
        data = dict(self.request.GET)

        reports_generator = GeneratorOfReports(
            start_report_period=data['start_report_period'],
            end_report_period=data['end_report_period'],
            report_number=data['report_number'],
            user_name=data['user_name'],
            password=data['password'],
            config=self.conf
        )
        file_name = reports_generator.filename('.xlsx')

        file_path = os.path.join(self.ROOT_DIR, '..', self.REPORTS_PATH, file_name)

        response = FileResponse(
            path=file_path,
            request=self.request,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response.headers['Content-Disposition'] = ("attachment; filename={}".format(file_name))

        return response

if __name__ == '__main__':
    config = Configurator()
    config.add_route('report', '/report')
    config.add_view(ReportView, route_name='report')
    config.scan('.')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()



