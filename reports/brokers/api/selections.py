report1 = '''
SELECT 
	br.`code` AS broker, COUNT(ts.id) AS tenderers_count
FROM 
	tenders t
    LEFT JOIN `brokers` br ON br.`id` = t.`broker_id`
	LEFT JOIN bids b ON b.`tender_id` = t.id
	LEFT JOIN `tenderers_bids` tb ON tb.`bid_id` = b.id
	LEFT JOIN tenderers ts ON ts.`id` = tb.`tenderer_id`	
	INNER JOIN
	(
		SELECT 
			ts.`id` AS tenderer_id, MIN(t.`enquiry_start_date`) AS min_tender_date
		FROM tenders t
		   LEFT JOIN bids b ON b.`tender_id` = t.id
		   LEFT JOIN `tenderers_bids` tb ON tb.`bid_id` = b.id
		   LEFT JOIN tenderers ts ON ts.`id` = tb.`tenderer_id`
		WHERE 
			ts.`id` IS NOT NULL
			AND ts.`identifier`  IS NOT NULL
			AND ts.`identifier` <> ''
		GROUP BY ts.`id`
	) AS tmp
	ON ts.`id` = tmp.tenderer_id AND t.`enquiry_start_date` = tmp.min_tender_date
	WHERE t.`enquiry_end_date` BETWEEN %(start_date)s AND %(end_date)s
	GROUP BY br.id
	ORDER BY 2 DESC
'''

report2 = '''
'''
report3 = '''
'''

auth = '''
SELECT id
FROM users
WHERE user_name=%(user_name)s AND password=password AND blocked=0
'''

logging = '''
INSERT INTO user_actions(user_id, report_type_id, start_report_period, end_report_period)
VALUES (%(user_id)s, %(report_type_id)s, %(start_report_period)s, %(end_report_period)s)
'''