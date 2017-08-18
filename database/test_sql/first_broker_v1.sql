SELECT 
	grp1.first_broker, COUNT(grp1.identifier) AS new_tenderers_count
FROM 
	(
		SELECT 
			ts.`identifier`, 
			(
				SELECT br2.code
				FROM 
					tenders t2 
					LEFT JOIN `brokers` br2 ON br2.`id` = t2.`broker_id`
					LEFT JOIN bids b2 ON b2.`tender_id` = t2.id
					LEFT JOIN `tenderers_bids` tb2 ON tb2.`bid_id` = b2.id
				WHERE tb2.tenderer_id = ts.`id`
				ORDER BY b2.bid_date
				LIMIT 1) AS first_broker,
				COUNT(t.id) AS tenders_count
		FROM 
			tenders t
			LEFT JOIN `brokers` br ON br.`id` = t.`broker_id`
			LEFT JOIN bids b ON b.`tender_id` = t.id
			LEFT JOIN `tenderers_bids` tb ON tb.`bid_id` = b.id
			LEFT JOIN tenderers ts ON ts.`id` = tb.`tenderer_id`
		WHERE ts.`id` IS NOT NULL
		GROUP BY ts.`identifier`
		HAVING COUNT(t.id) > 1
		ORDER BY ts.`id`
	) AS grp1
GROUP BY grp1.first_broker

SELECT 
	t.`enquiry_start_date`, t.`enquiry_end_date`, br.`code`, b.`bid_date`, ts.`identifier`
FROM 
	tenders t
	LEFT JOIN `brokers` br ON br.`id` = t.`broker_id`
	LEFT JOIN bids b ON b.`tender_id` = t.id
	LEFT JOIN `tenderers_bids` tb ON tb.`bid_id` = b.id
	LEFT JOIN tenderers ts ON ts.`id` = tb.`tenderer_id`
WHERE 
	ts.`identifier` IN (
		SELECT 
			ts2.`identifier`
		FROM 
			tenders t2
			LEFT JOIN `brokers` br2 ON br2.`id` = t2.`broker_id`
			LEFT JOIN bids b2 ON b2.`tender_id` = t2.id
			LEFT JOIN `tenderers_bids` tb2 ON tb2.`bid_id` = b2.id
			LEFT JOIN tenderers ts2 ON ts2.`id` = tb2.`tenderer_id`
		WHERE ts2.`id` IS NOT NULL
		GROUP BY ts2.`identifier`
		HAVING COUNT(t2.id) > 1)	
ORDER BY ts.`id`, b.`bid_date`

