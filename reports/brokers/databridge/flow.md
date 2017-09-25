# Flow of data

1. We acquire tenders data from API, queue ids->filtered_tender_ids_queue
2. We acquire data for every tender in base_integration: filtered_tender_ids_queue->tenders

Normal procedure:

3. We save tenders and their data in the database.

Flow of acquiring edr data:

3. We parse tender, and, if we find edr_documents worth downloading,
we put their tuples->processing_docs_queue.
4. processing_docs_queue->(tender_id, bid_id, edr_status, edr_date)?

Okay, new solution: copy idea from edr bot and just pass around the
whole namedtuple, adding new fields when they appear
