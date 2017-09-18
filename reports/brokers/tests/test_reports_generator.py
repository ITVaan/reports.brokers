# coding=utf-8
from hashlib import sha256
from uuid import uuid4

from reports.brokers.api.views.reports_generator import GeneratorOfReports
from reports.brokers.tests.base_db_test import BaseDbTestCase
from reports.brokers.tests.utils import test_config


class TestReportsGenerator(BaseDbTestCase):
    def test_init(self):
        cursor = self.conn.cursor(buffered=True)
        password = sha256("1234").hexdigest()
        cursor.execute("""INSERT INTO `users` (`user_name`, `password`, `blocked`) VALUES ("Vlad", "{}", 0);""".format(
            password))
        cursor.close()
        self.conn.commit()
        rep_gen = GeneratorOfReports('01.05.2017', '01.06.2017', 1, 'Vlad', '1234', test_config)
        self.assertEqual(rep_gen.report_number, 1)
        self.assertEqual(rep_gen.password, password)
        self.assertEqual(rep_gen.config, test_config)

    def test_permission(self):
        rep_gen = GeneratorOfReports('01.05.2017', '01.06.2017', '1', 'test', 'test', test_config)
        self.assertEqual(rep_gen.report_number, '1')
        self.assertNotEqual(rep_gen.password, 'test')
        self.assertEqual(rep_gen.config, test_config)

    def test_start_reporting(self):
        date = '2017-05-02 13:00:00.000000'
        tender_id = uuid4().hex
        cursor = self.conn.cursor(buffered=True)
        cursor.execute("""INSERT INTO `users` (`user_name`, `password`, `blocked`) VALUES ("test", "{}", 0);""".format(
            self.password))
        cursor.execute("""INSERT INTO `brokers` (code) VALUES ("test");""")
        cursor.execute("""INSERT INTO `tenders` (`original_id`, `status_id`, `broker_id`, `date_modified`, 
                                              `enquiry_start_date`, `enquiry_end_date`) 
                       VALUES ('{}', '5', 1, "{}", "{}", "{}");""".format(tender_id, date, date, date))
        cursor.close()
        self.conn.commit()
        rep_gen = GeneratorOfReports('01.05.2016', '01.06.2018', '1', 'test', 'test', test_config)
        self.assertEqual(rep_gen.report_number, '1')
        self.assertEqual(rep_gen.password, self.password)
        self.assertEqual(rep_gen.config, test_config)

    def test_report_2(self):
        date = '2017-05-02 13:00:00.000000'
        tender_id = uuid4().hex
        edr_ids = [str(i) for i in range(30)]
        cursor = self.conn.cursor(buffered=True)
        cursor.execute("""INSERT INTO `users` (`user_name`, `password`, `blocked`) VALUES ("test", "{}", 0);""".format(
            self.password))
        cursor.execute("""INSERT INTO `brokers` (code) VALUES ("test");""")
        res = cursor.execute("""INSERT INTO `tenders` (`original_id`, `status_id`, `broker_id`, `date_modified`,
                                              `enquiry_start_date`, `enquiry_end_date`)
                       VALUES ('{}', '5', 1, "{}", "{}", "{}");""".format(tender_id, date, date, date))
        tender_db_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO `bids` (`original_id`, `tender_id`, `status_id`) VALUES ("{}", {}, 1)""".format(tender_id,
                                                                                                           tender_db_id))
        bid_db_id = cursor.lastrowid
        edr_status = 1
        for i in range(30):
            if edr_status == 1:
                cursor.execute(
                    """INSERT INTO `tenderers` (`identifier`, `scheme`, `edr_status`) VALUES ({}, "UA-EDR", 1)""".
                        format(edr_ids[i]))
                edr_status = 0
            else:
                cursor.execute(
                    """INSERT INTO `tenderers` (`identifier`, `scheme`, `edr_status`) VALUES ({}, "UA-EDR", 0)""".
                        format(edr_ids[i]))
                edr_status = 1
            cursor.execute(
                """INSERT INTO `tenderers_bids` (`tenderer_id`, `bid_id`) VALUES ({}, {})""".format(cursor.lastrowid,
                                                                                                    bid_db_id))
        cursor.close()
        self.conn.commit()
        rep_gen = GeneratorOfReports('01.05.2016', '01.06.2018', '2', 'test', 'test', test_config)
        self.assertEqual(rep_gen.report_number, '2')
        self.assertEqual(rep_gen.password, self.password)
        self.assertEqual(rep_gen.config, test_config)
        self.assertEqual(rep_gen.ws[2][1].value, 15)
        self.assertEqual(rep_gen.ws[2][2].value, 15)
