/*
SQLyog Ultimate v12.14 (64 bit)
MySQL - 10.2.7-MariaDB : Database - reports_data
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*Table structure for table `brokers` */

CREATE TABLE `brokers` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID of broker for the report subsystem',
  `code` varchar(32) NOT NULL COMMENT 'Unique name (codename) of broker, the same as in INI files',
  `created_on` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `broker_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COMMENT='Brokers, aka  ''platforms''';

/*Data for the table `brokers` */

insert  into `brokers`(`id`,`code`,`created_on`) values (1,'prom.ua','2017-08-15 11:38:34');
insert  into `brokers`(`id`,`code`,`created_on`) values (2,'netcast.com.ua','2017-08-15 11:38:55');
insert  into `brokers`(`id`,`code`,`created_on`) values (3,'netcast.com.ua.test','2017-08-15 18:01:01');
insert  into `brokers`(`id`,`code`,`created_on`) values (4,'it.ua','2017-08-15 18:38:49');
insert  into `brokers`(`id`,`code`,`created_on`) values (5,'newtend.com','2017-08-16 20:35:23');
insert  into `brokers`(`id`,`code`,`created_on`) values (6,'e-tender.biz','2017-08-16 20:35:23');
insert  into `brokers`(`id`,`code`,`created_on`) values (7,'public-bid.com.ua','2017-08-16 20:44:38');
insert  into `brokers`(`id`,`code`,`created_on`) values (8,'uub.com.ua','2017-08-16 21:02:55');
insert  into `brokers`(`id`,`code`,`created_on`) values (9,'zakupki.com.ua','2017-08-17 15:42:19');

/*Table structure for table `procurement_method_types` */

CREATE TABLE `procurement_method_types` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

/*Data for the table `procurement_method_types` */

insert  into `procurement_method_types`(`id`,`code`) values (2,'aboveThresholdEU');
insert  into `procurement_method_types`(`id`,`code`) values (1,'aboveThresholdUA');
insert  into `procurement_method_types`(`id`,`code`) values (3,'aboveThresholdUA.defense');
insert  into `procurement_method_types`(`id`,`code`) values (6,'belowThreshold');
insert  into `procurement_method_types`(`id`,`code`) values (5,'competitiveDialogueEU.stage2');
insert  into `procurement_method_types`(`id`,`code`) values (4,'competitiveDialogueUA.stage2');

/*Table structure for table `procurement_methods` */

CREATE TABLE `procurement_methods` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

/*Data for the table `procurement_methods` */

insert  into `procurement_methods`(`id`,`code`) values (3,'limited');
insert  into `procurement_methods`(`id`,`code`) values (1,'open');
insert  into `procurement_methods`(`id`,`code`) values (2,'selective');

/*Table structure for table `tender_statuses` */

CREATE TABLE `tender_statuses` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;

/*Data for the table `tender_statuses` */

insert  into `tender_statuses`(`id`,`code`) values (3,'active.auction');
insert  into `tender_statuses`(`id`,`code`) values (5,'active.awarded');
insert  into `tender_statuses`(`id`,`code`) values (1,'active.enquiries');
insert  into `tender_statuses`(`id`,`code`) values (9,'active.pre-qualification');
insert  into `tender_statuses`(`id`,`code`) values (4,'active.qualification');
insert  into `tender_statuses`(`id`,`code`) values (2,'active.tendering');
insert  into `tender_statuses`(`id`,`code`) values (8,'cancelled');
insert  into `tender_statuses`(`id`,`code`) values (7,'complete');
insert  into `tender_statuses`(`id`,`code`) values (6,'unsuccessful');

/*Table structure for table `tenders` */

CREATE TABLE `tenders` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Integer ID for reports database',
  `original_id` char(32) NOT NULL COMMENT 'ID (hash, ocid) of tender in main database',
  `status_id` smallint(6) unsigned NOT NULL,
  `broker_id` int(10) unsigned NOT NULL,
  `date_modified` datetime(6) NOT NULL,
  `created_on` timestamp(3) NOT NULL DEFAULT current_timestamp(3),
  `updated_on` timestamp(3) NOT NULL DEFAULT current_timestamp(3) ON UPDATE current_timestamp(3),
  `enquiry_start_date` datetime(6) NOT NULL,
  `enquiry_end_date` datetime NOT NULL,
  `procurement_method_type_id` smallint(5) unsigned DEFAULT NULL,
  `procurement_method_id` smallint(5) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `original_id` (`original_id`),
  KEY `FK_tender_broker` (`broker_id`),
  KEY `FK_tender_status` (`status_id`),
  KEY `FK_tender_procmettype` (`procurement_method_type_id`),
  KEY `FK_tender_procmet` (`procurement_method_id`),
  CONSTRAINT `FK_tender_broker` FOREIGN KEY (`broker_id`) REFERENCES `brokers` (`id`),
  CONSTRAINT `FK_tender_procmet` FOREIGN KEY (`procurement_method_id`) REFERENCES `procurement_methods` (`id`),
  CONSTRAINT `FK_tender_procmettype` FOREIGN KEY (`procurement_method_type_id`) REFERENCES `procurement_method_types` (`id`),
  CONSTRAINT `FK_tender_status` FOREIGN KEY (`status_id`) REFERENCES `tender_statuses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Tenders basic information';

/*Data for the table `tenders` */

/*Table structure for table `bid_statuses` */

CREATE TABLE `bid_statuses` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

/*Data for the table `bid_statuses` */

insert  into `bid_statuses`(`id`,`code`) values (1,'active');
insert  into `bid_statuses`(`id`,`code`) values (3,'deleted');
insert  into `bid_statuses`(`id`,`code`) values (2,'draft');
insert  into `bid_statuses`(`id`,`code`) values (6,'invalid');
insert  into `bid_statuses`(`id`,`code`) values (5,'pending');
insert  into `bid_statuses`(`id`,`code`) values (4,'unsuccessful');

/*Table structure for table `bids` */

CREATE TABLE `bids` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Integer ID for reports database',
  `original_id` varchar(32) NOT NULL COMMENT 'ID (hash) of bid in original database',
  `tender_id` bigint(20) unsigned NOT NULL,
  `bid_date` datetime(6) DEFAULT NULL,
  `status_id` smallint(5) unsigned NOT NULL,
  `created_on` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `FK_bid_tender` (`tender_id`),
  KEY `FK_bid_status` (`status_id`),
  CONSTRAINT `FK_bid_status` FOREIGN KEY (`status_id`) REFERENCES `bid_statuses` (`id`),
  CONSTRAINT `FK_bid_tender` FOREIGN KEY (`tender_id`) REFERENCES `tenders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='bids basic information';

/*Data for the table `bids` */

/*Table structure for table `report_types` */

CREATE TABLE `report_types` (
  `id` smallint(5) unsigned NOT NULL,
  `name` varchar(120) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `report_types` */

insert  into `report_types`(`id`,`name`) values (1,'Attracted Suppliers');
insert  into `report_types`(`id`,`name`) values (2,'Correct Suppliers');
insert  into `report_types`(`id`,`name`) values (3,'Supplier Frequency');

/*Table structure for table `tenderers` */

CREATE TABLE `tenderers` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Integer ID for reports database',
  `identifier` varchar(50) NOT NULL COMMENT 'Organization identifier. Contains UA-EDR for Ukrainian organizations.',
  `scheme` varchar(50) NOT NULL,
  `created_on` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `identifier` (`identifier`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Suppliers, or tender participants. Field called ''tenderers'' in main database';

/*Data for the table `tenderers` */

/*Table structure for table `tenderers_bids` */

CREATE TABLE `tenderers_bids` (
  `tenderer_id` int(10) unsigned NOT NULL,
  `bid_id` bigint(20) unsigned NOT NULL,
  `created_on` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`tenderer_id`,`bid_id`),
  KEY `FK_tendbid_bid` (`bid_id`),
  CONSTRAINT `FK_tendbid_bid` FOREIGN KEY (`bid_id`) REFERENCES `bids` (`id`),
  CONSTRAINT `FK_tendbid_tenderer` FOREIGN KEY (`tenderer_id`) REFERENCES `tenderers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Many to many link between suppliers (tenderers) and bids';

/*Data for the table `tenderers_bids` */

/*Table structure for table `user_action_types` */

CREATE TABLE `user_action_types` (
  `id` smallint(5) unsigned NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `user_action_types` */

insert  into `user_action_types`(`id`,`name`) values (1,'login');
insert  into `user_action_types`(`id`,`name`) values (2,'view_report');

/*Table structure for table `users` */

CREATE TABLE `users` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_name` varchar(15) NOT NULL,
  `password` varchar(120) NOT NULL,
  `blocked` tinyint unsigned zerofill NOT NULL,
  `full_name` varchar(50) DEFAULT NULL,
  `created_on` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_on` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_name` (`user_name`),
  KEY `blocked` (`blocked`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `users` */

/*Table structure for table `user_actions` */

CREATE TABLE `user_actions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL,
  `action_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `action_type` smallint(5) unsigned NOT NULL,
  `report_type_id` smallint(5) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK1_useraction_user` (`user_id`),
  KEY `FK2_useraction_reporttype` (`report_type_id`),
  CONSTRAINT `FK1_useraction_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `FK2_useraction_reporttype` FOREIGN KEY (`report_type_id`) REFERENCES `report_types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `user_actions` */

/* Function  structure for function  `fn_parse_utc_datetime` */

DELIMITER $$

/*!50003 CREATE DEFINER=`root`@`localhost` FUNCTION `fn_parse_utc_datetime`(

	`datetime_string` VARCHAR(50)

) RETURNS datetime(6)
BEGIN

	set @timeZone = '+00:00';

	set @res = null;



	IF SUBSTRING(datetime_string, 27, 1) = '+' or SUBSTRING(datetime_string, 27, 1) = '-' THEN 

		set @timeZone = SUBSTRING(datetime_string, 27, 6);

	end if;



	set @res = CONVERT_TZ(STR_TO_DATE(datetime_string, '%Y-%m-%dT%H:%i:%s.%f'), @timeZone, '+00:00');	

	if @res is null then #may be date without microseconds

		IF SUBSTRING(datetime_string, 20, 1) = '+' or SUBSTRING(datetime_string, 20, 1) = '-' THEN 

			set @timeZone = SUBSTRING(datetime_string, 20, 6);

		end if;	

		set @res = CONVERT_TZ(STR_TO_DATE(datetime_string, '%Y-%m-%dT%H:%i:%s'), @timeZone, '+00:00');	

	end if;



	return @res;

END */$$
DELIMITER ;

/* Procedure structure for procedure `sp_check_tender` */

DELIMITER $$

/*!50003 CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_check_tender`(

	IN `tender_hash` CHAR(32),

	OUT `tender_status` SMALLINT



)
BEGIN

	set tender_status := (select status_id from tenders where original_id = tender_hash);

END */$$
DELIMITER ;

/* Procedure structure for procedure `sp_test_json` */

DELIMITER $$

/*!50003 CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_test_json`()
BEGIN

	set @json = '{"data":{"procurementMethod":"open","numberOfBids":3,"awardPeriod":{"startDate":"2017-08-01T14:36:30.446339+03:00","endDate":"2017-08-04T09:54:45.638521+03:00"},"complaintPeriod":{"startDate":"2017-07-13T13:24:19.108055+03:00","endDate":"2017-07-27T00:00:00+03:00"},"auctionUrl":"https://auction.openprocurement.org/tenders/c9d2f876980a4c719e621d43e8cc1928","enquiryPeriod":{"startDate":"2017-07-13T13:24:19.108055+03:00","clarificationsUntil":"2017-07-26T14:00:00+03:00","endDate":"2017-07-21T14:00:00+03:00","invalidationDate":"2017-07-13T13:33:00.698500+03:00"},"submissionMethod":"electronicAuction","procuringEntity":{"kind":"general","name":"","address":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"contactPoint":{"url":"http://www.emd.kh.ua","name_en":"Zhalinska Oksana Volodymyrivna","email":"kkt_cemd@ukr.net","name":"","telephone":"380577029453"},"identifier":{"scheme":"UA-EDR","legalName_en":"Municipal Health Care Institution Centre of Emergency Medical Aid and Catastrophe Medicine","id":"38494108","legalName":""},"name_en":"Municipal Health Care Institution Centre of Emergency Medical Aid and Catastrophe Medicine"},"owner":"e-tender.biz","id":"c9d2f876980a4c719e621d43e8cc1928","description":"","documents":[{"hash":"md5:083552e97391329242f4bef7996a2f6e","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/3f7796e6fc1244a29602260bcf074327?KeyID=52462340&Signature=VeykeJcaqy%252BDGaEkdi7A%252Bv7%252Bgl6pMvQkdyeE6IXkIcb3dfwlMfBDM7NyBlRGqmuUS6FwvkADq0FI07Lv5v5CAg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:27:00.460191+03:00","documentType":"biddingDocuments","dateModified":"2017-07-13T13:27:00.460213+03:00","id":"4cca7264e9d640d094a25771450928ee"},{"hash":"md5:7fa3613ba8b66cac7f997818e0d305f8","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/65efcdf01dce40d6bc6a103d702a38cb?KeyID=52462340&Signature=EtNJrjEw5xEjR8zVAeofSkRArhEdE2Su%252B9x6FfDDVtPKtwvfEqowEWt0wDM6OxFvlkdGYDIAXGlBN4EHz4EXDQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:27:40.794495+03:00","documentType":"eligibilityCriteria","dateModified":"2017-07-13T13:27:40.794516+03:00","id":"cf3431a9d85d4f3c8f8e4bd430a84ec0"},{"hash":"md5:b3f544fe7f585c93ad1585e8ebf251d8","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/cac4a2424bfd4c4ab842bb64dc80a0cd?KeyID=52462340&Signature=BwAZ1Tg5dPow%2FVMNx%2FjBgg4UYu1zpHVFnD%252BAQ3k1zBc9LqjK0NtqbBrXZgpkgoiB6deqPlsl%2F8SoOl9PdldVAA%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:28:25.936571+03:00","documentType":"contractProforma","dateModified":"2017-07-13T13:28:25.936624+03:00","id":"c9e9d17ff3014a489ff2216843114685"},{"hash":"md5:a2e16b232fb1fe8a46aae14a5be85f9e","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/72f0a46da1c143318ec8a28edb6aa6f4?KeyID=52462340&Signature=GOJC7YxPzafWjc%2FD5lKV7Bhyuqp4lnX90QaEGqdu2n9hA8oHJBQUTJ6cJdl6LgY9j2lUD98HRFPcqIt%2FOA03DQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:29:09.618430+03:00","documentType":"technicalSpecifications","dateModified":"2017-07-13T13:29:09.618451+03:00","id":"7820348fd8a74369891544b018982c69"},{"hash":"md5:1ca1649e4ddad98834f71f60c29d585a","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/c5576ee2dd564ebc8fd3a245a26f4d12?KeyID=52462340&Signature=h9g2tQZfzX%2F%252BYdi4g%252BQvYxzCYyE%2Fe%2FbQUt00r7Fjv6FHWZGSdH7qYYqbf0UcPmWd1kAduclRw%252Be95v4HjXX%252BDg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:29:09.943103+03:00","dateModified":"2017-07-13T13:29:09.943140+03:00","id":"9f1c4791d556442e8fe58785f91e9d12"},{"hash":"md5:090bee0cc090d62799cb6819496aef7f","author":"tender_owner","format":"application/pkcs7-signature","url":"https://public.docs.openprocurement.org/get/b7ae329ff3444a99897818adb63a4701?KeyID=52462340&Signature=KlxlYwMWFWk225BheGLrTViL%2F2X7LoIbrH7sKB%2F118l9scw7VwO0MpAfYENbVMG1MaW4zkDZ%252B0kmWY21mPiJAQ%253D%253D","title":"sign.p7s","documentOf":"tender","datePublished":"2017-07-13T13:33:00.697703+03:00","dateModified":"2017-07-13T13:33:00.697724+03:00","id":"2960c71e5d0e4199be6cd14678a5321a"},{"hash":"md5:53212f5af9c366beca2b6a77d4da4447","author":"auction","format":"text/plain","url":"https://public.docs.openprocurement.org/get/9fdd49b1bed04c718e96978dc40fc525?KeyID=52462340&Signature=%2F9Jm4pKaBwCXalcbVRs%252BjwleiIwmWN4OMqtZv%252BO9KbIH5JsXd%2FbWZlk5Y8ZcumEIGTRavDXYnwrrkbxnKtXgDw%253D%253D","title":"audit_c9d2f876980a4c719e621d43e8cc1928.yaml","documentOf":"tender","datePublished":"2017-08-01T14:36:29.366486+03:00","dateModified":"2017-08-01T14:36:29.366522+03:00","id":"7b0692728f7d4af3bae2e0f7a550874d"},{"hash":"md5:7c03b4681100d2231dc2def8653e29af","author":"auction","format":"text/plain","url":"https://public.docs.openprocurement.org/get/0f89825697a1431f885bcf0610819126?KeyID=52462340&Signature=4f6Vn4Ui0dW1D0ldGyn8YVnCxH2V%252BfneBgsApDgXFG1DodZz6YJIeFV7BNiHqByx2GxYkb29l8W9uFFUsGmDBw%253D%253D","title":"audit_c9d2f876980a4c719e621d43e8cc1928.yaml","documentOf":"tender","datePublished":"2017-08-01T14:36:29.366486+03:00","dateModified":"2017-08-01T14:36:30.760365+03:00","id":"7b0692728f7d4af3bae2e0f7a550874d"}],"title":"","tenderID":"UA-2017-07-13-001132-b","guarantee":{"currency":"UAH","amount":0.0},"dateModified":"2017-08-15T00:04:40.444240+03:00","status":"unsuccessful","tenderPeriod":{"startDate":"2017-07-13T13:24:19.108055+03:00","endDate":"2017-07-31T14:00:00+03:00"},"auctionPeriod":{"startDate":"2017-08-01T14:09:29+03:00","endDate":"2017-08-01T14:36:30.386402+03:00"},"procurementMethodType":"aboveThresholdUA","awards":[{"status":"unsuccessful","documents":[{"hash":"md5:5fb8d95b0de1aac748c5262359e34567","author":"bots","format":"application/yaml","url":"https://public.docs.openprocurement.org/get/9b65659ca3fb4075814cb03d63877ad4?KeyID=52462340&Signature=%252BaYv63d6%252Bylk%252BspaHebuiZxfxevClmPaWWTFVPabmW5XFtySFnDM%2FWEXVSc43hErfOe3u3Q9LOTVbJ%2F6Gg8XCw%253D%253D","title":"edr_identification.yaml","documentOf":"tender","datePublished":"2017-08-01T14:36:52.249918+03:00","documentType":"registerExtract","dateModified":"2017-08-01T14:36:52.249955+03:00","id":"606f50a8ea574154aea33b6b1f165232"},{"hash":"md5:124b09a1104037b4f58a79ff577facb6","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/1d31dbe1bbed4b448da1ee87372b827a?KeyID=52462340&Signature=kMwBgGsvlYQ043%252BWJMzwx29ZGmDmCtDEPbsz%2FdvSJpiZ0nhPJ3jU1Y19KEciEBEt9jBJiCi1vB9JFDWy36uUCw%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-02T10:27:50.864191+03:00","documentType":"awardNotice","dateModified":"2017-08-02T10:27:50.864212+03:00","id":"11daa1a20aaf4b84aaaa89b0fc82bc73"},{"hash":"md5:a188147e925be4aaebdf8ff1bcf510b6","author":"tender_owner","format":"application/pkcs7-signature","url":"https://public.docs.openprocurement.org/get/c811e2e0413042a989d872ada94fd103?KeyID=52462340&Signature=kRY9eHlcHuY8qr6hVoaZ0%2FsUToo9x1dg2j0JR02RY%2F%2Fxssgo3qIdlp9DhyAaGgFQrrwsa5Yt86GvwbdQKFsBDg%253D%253D","title":"sign.p7s","documentOf":"tender","datePublished":"2017-08-02T10:30:50.609072+03:00","dateModified":"2017-08-02T10:30:50.609094+03:00","id":"e4cbc1ef598b40179b8447a76acc9076"}],"description":"","title":"","suppliers":[{"contactPoint":{"email":"popova.julia@pharmplanet.com.ua","name":"","telephone":"+380443915069"},"identifier":{"scheme":"UA-EDR","id":"36852896","legalName":""},"name":"","address":{"postalCode":"08171","countryName":"","streetAddress":"","region":"","locality":""}}],"complaintPeriod":{"startDate":"2017-08-01T14:36:30.447710+03:00","endDate":"2017-08-13T00:00:00+03:00"},"bid_id":"6ce5b18702d14bc6b458edd8fafaa7bf","value":{"currency":"UAH","amount":1342561.1,"valueAddedTaxIncluded":true},"qualified":false,"date":"2017-08-02T10:38:27.581750+03:00","eligible":false,"id":"a65b3a7561f04ecbb92018cc69c4f274"},{"status":"unsuccessful","documents":[{"hash":"md5:732a3b08eb0ce9411bf66cfd2f3327e0","author":"bots","format":"application/yaml","url":"https://public.docs.openprocurement.org/get/c245785936254a7d8c252e019df11b9a?KeyID=52462340&Signature=IOlWY9h78ltZxjpv6QSNDEqKrOJHd6x%2FDIo7Vuv073%252B6zjVO%2F8HeMMu2ilWYTOwl%2F578K2sjE5W8m2ee8XYYCw%253D%253D","title":"edr_identification.yaml","documentOf":"tender","datePublished":"2017-08-02T10:38:42.411357+03:00","documentType":"registerExtract","dateModified":"2017-08-02T10:38:42.411377+03:00","id":"566b0fe5b3e94f04a0a56c25ed5e0f79"},{"hash":"md5:06b2eb60d0c0bb3086849bfd28302eed","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/31673c132d1d4c549433c699112ed2b2?KeyID=52462340&Signature=y5v2%2FRFgfqs5bA5nSu0YZVWiuBb1rmhsEIZ45aZMZX5%252BQiN6IocwLj6hfKnhBMsANNCTawO27j9elndJwt1SDQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-03T10:31:04.959046+03:00","documentType":"awardNotice","dateModified":"2017-08-03T10:31:04.959068+03:00","id":"11d525f14f5d435ab945d1e85e0cb2ba"},{"hash":"md5:edcacfe64c2eda3f63cdeb796e8370be","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/0e586aac1d144da78898ad686285f9dc?KeyID=52462340&Signature=ACF5TqW%2FwY%2FOEIqyTvQtXtuzWwtFnk%2FLL1k1vPmzgNf%2FLRblJMiKsHybntZB%2FMTU375fTK%252BbtwGbbF3Wj6mRAQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-03T10:34:17.069340+03:00","documentType":"awardNotice","dateModified":"2017-08-03T10:34:17.069375+03:00","id":"0797838681aa4e499d0e740c9f372ace"},{"hash":"md5:a969ddf266277efd628ca3729a1cbb92","author":"tender_owner","format":"application/pkcs7-signature","url":"https://public.docs.openprocurement.org/get/10497c8bc00a434e9a467a6d808d567e?KeyID=52462340&Signature=UF9Va5Zld02suSRQ%252BrvtiNrl80r%2Fyhm8Ui%2FeTfWQEt37D6GvCF4q2mfFiWSZj%2FXWMVcJx0yvan%2FsnwyMPGJHCA%253D%253D","title":"sign.p7s","documentOf":"tender","datePublished":"2017-08-03T10:37:33.614003+03:00","dateModified":"2017-08-03T10:37:33.614024+03:00","id":"e77ad02958824ce9987107d33ed5aa60"}],"description":"","title":"","suppliers":[{"contactPoint":{"email":"eburyak@badm-b.biz","name":"","telephone":"+380567470245"},"identifier":{"scheme":"UA-EDR","id":"39273420","legalName":""},"name":"","address":{"postalCode":"49005","countryName":"","streetAddress":"","region":"","locality":""}}],"complaintPeriod":{"startDate":"2017-08-02T10:38:27.570342+03:00","endDate":"2017-08-14T00:00:00+03:00"},"bid_id":"cc4fcb7f07af4916b57ae7088faf183b","value":{"currency":"UAH","amount":1361804.84,"valueAddedTaxIncluded":true},"qualified":false,"date":"2017-08-03T10:39:00.693874+03:00","eligible":false,"id":"269ad74d1a0440e0829e59cb4916bb7b"},{"status":"unsuccessful","documents":[{"hash":"md5:62190919da068017491597182ae0994f","author":"bots","format":"application/yaml","url":"https://public.docs.openprocurement.org/get/6124ef107cb7404c913df1c00b15968d?KeyID=52462340&Signature=xjEl15nbY7Rci3un5UIOCDJtgGLsweG3xgmrX5yVuuba9varmAgfDiTsX8OP8GN7tqbG2BaEdXzqrtycHb8TAg%253D%253D","title":"edr_identification.yaml","documentOf":"tender","datePublished":"2017-08-03T10:39:10.451241+03:00","documentType":"registerExtract","dateModified":"2017-08-03T10:39:10.451262+03:00","id":"e3bfd381fc8e47928edf1fc5b3fdf226"},{"hash":"md5:3735674223a5b8c2a42836e41ee97e7f","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/1c27ddd9ec9b42eab6d0309708bb6ebf?KeyID=52462340&Signature=JIQKIwyRihevLmV9uAAfv%252BCmwEolpGHpEnermxFySiXrGvjEvUOU6IEk2RIUzsxYfAgNHqWHv60N%2FWP8tS5UBA%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-04T09:50:46.234182+03:00","documentType":"awardNotice","dateModified":"2017-08-04T09:50:46.234203+03:00","id":"7292d594d4f04a1091293014fdf60f95"},{"hash":"md5:4427ffa39cb046ad561605a97e153dd7","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/02299f4432bf4871b39f8fca5d3d0c35?KeyID=52462340&Signature=ZhuaF8yDhAdCww46GDr8drEWubdGq%252BJHky2B7%252Bt%2FBWtBnEVvUswNC6N1XOMHRh7PcBPl9xiDXfWpMMHNxyDWBg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-04T09:52:12.590293+03:00","documentType":"awardNotice","dateModified":"2017-08-04T09:52:12.590321+03:00","id":"fc6971ab2c9947cdb8fbc1f14809700f"},{"hash":"md5:49136caa10c46c6250523d409c160f9c","author":"tender_owner","format":"application/pkcs7-signature","url":"https://public.docs.openprocurement.org/get/5da946d3ff7d4843bf9a158e1d5b9b15?KeyID=52462340&Signature=A2dRdfzCQt4bE96BYwkhGM2NBhYdAjW15ASIJUI8SXRFGQflO4qhVJpXPjoDhIhmJP%2FJX0mpfmt6202POjM2Cw%253D%253D","title":"sign.p7s","documentOf":"tender","datePublished":"2017-08-04T09:53:23.369352+03:00","dateModified":"2017-08-04T09:53:23.369389+03:00","id":"1ba0cf57d61947ee9ca3a1f8364bfbe4"}],"description":"","title":"","suppliers":[{"contactPoint":{"email":"lala.19@ukr.net","name":"","telephone":"+380672458377"},"identifier":{"scheme":"UA-EDR","id":"25184975","uri":"http://framco.com.ua","legalName":""},"name":"","address":{"postalCode":"61204","countryName":"","streetAddress":"","region":"","locality":""}}],"complaintPeriod":{"startDate":"2017-08-03T10:39:00.682268+03:00","endDate":"2017-08-15T00:00:00+03:00"},"bid_id":"205955af6f964a638e28ec7fa7588e83","value":{"currency":"UAH","amount":1361928.1,"valueAddedTaxIncluded":true},"qualified":false,"date":"2017-08-04T09:54:45.651520+03:00","eligible":false,"id":"ac0cec9426484c7392b47e964cd0874b"}],"date":"2017-08-15T00:04:40.444240+03:00","minimalStep":{"currency":"UAH","amount":681.0,"valueAddedTaxIncluded":true},"items":[{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"edfb854fe545475f8e16814d36b95fed","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"925abfc889e34645ab978784a631e188","unit":{"code":"PK","name":""},"quantity":400},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"9697cc26dc094e56b2b0f1337a99004a","unit":{"code":"VI","name":""},"quantity":400},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"21dd7fd215de4dd3ab6ec4d68d91b452","unit":{"code":"PK","name":""},"quantity":1000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"733963d9da3844f28951c7931ec019cb","unit":{"code":"PK","name":""},"quantity":500},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"a89ea5baeb7a4475804dfa53c113c10f","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"6bd363b0d332487ba97b0a089dc8e81e","unit":{"code":"PK","name":""},"quantity":1500},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"87f0331c4e974f28af90f7bf42822fc9","unit":{"code":"PK","name":""},"quantity":200},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"d3dfd8720cfd4eccaf08a63b9ff502db","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"cfaa6b1b8ca34c07a7607dd508b99343","unit":{"code":"PK","name":""},"quantity":1500},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"83e0f8f848834d3498942595e6f99cb2","unit":{"code":"PK","name":""},"quantity":30},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"6516e3b7ddfe45d79a7d8e468380e2f3","unit":{"code":"PK","name":""},"quantity":1000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"9caa9b60f4294e5f82519cbdd2d53037","unit":{"code":"PK","name":""},"quantity":750},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"db629c64657e467f8975fc6c491f6a09","unit":{"code":"VI","name":""},"quantity":400},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"d04585588962424ca3e11fde185bacd8","unit":{"code":"PK","name":""},"quantity":1000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"c2ba767e664e4db19c560cf7e41d3353","unit":{"code":"PK","name":""},"quantity":250},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"5e97147d51ea4a07af548c42a16e1e1a","unit":{"code":"VI","name":""},"quantity":800},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"cd0e232ed4474b8192f9db060898ef66","unit":{"code":"VI","name":""},"quantity":500},{"description":"A","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"5216668a8874446f8562c636ca7232fb","unit":{"code":"PK","name":""},"quantity":500},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"c769fb88d4c64d928dd5230b65ecd045","unit":{"code":"PK","name":""},"quantity":3000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"4026b824a3624d6c9cd0791c7a9428d1","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"57528847fdcd4018944f8de1676ed0c4","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"117ce1dd13c74a058854b6d979e7754f","unit":{"code":"PK","name":""},"quantity":50},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"9fcd61a2b5f44e188ca97561c1b25c97","unit":{"code":"PK","name":""},"quantity":300},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"e23c4dac0a5f46be872470a7ab1a8d58","unit":{"code":"VI","name":""},"quantity":2000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"2075b72d653b488e8b684a413d82fe5d","unit":{"code":"PK","name":""},"quantity":300},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"4257b7acdd71499183c87cd1952aa56c","unit":{"code":"PK","name":""},"quantity":600},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"7de597a967f240bfa943096ca9eeb644","unit":{"code":"PK","name":""},"quantity":450},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"cbd53a5b18d1458985e788909800e29a","unit":{"code":"PK","name":""},"quantity":5000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"a697560962254dddbfc896416676d3d2","unit":{"code":"PK","name":""},"quantity":200},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"92af9cf6ac124740a6f334896da273b7","unit":{"code":"PK","name":""},"quantity":5000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"1a0a6b0051614e9a807f10699e6bcb42","unit":{"code":"PK","name":""},"quantity":350}],"bids":[{"status":"active","documents":[{"hash":"md5:c2fdedb41b6e46bfc38fe48fe41ff415","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/15163eeb93e84631acb2402b65535eac?KeyID=52462340&Signature=TUOpQnzEuvnb7jD2eZcAo3Ny2sYSj3CK49Cv61ib6bSuYHKDwn%2F5Q83hpzmPwYsk5o%252BAX9WffFoo7olQIrAWCg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-27T15:00:49.898346+03:00","dateModified":"2017-07-27T15:00:49.898381+03:00","id":"03a0bd1a7fbe4910866ab6bc4f1932a8"},{"hash":"md5:3cdd6c6374699c72fcd42933242d53d7","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/5a9a6d956b894f78a766c79a12ec0883?KeyID=52462340&Signature=jMiEDOTSIKzALrz2uUAI0BlPVL9qcsroDJGkJUtQ5eXnTgD5gKAkNI1F65AeQoOJtfTZbQLAp0c3YiKBAbCCCA%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-27T15:00:49.899173+03:00","dateModified":"2017-07-27T15:00:49.899208+03:00","id":"1458722127474353ba2849375fb0a983"}],"selfEligible":true,"value":{"currency":"UAH","amount":1342561.1,"valueAddedTaxIncluded":true},"subcontractingDetails":"","selfQualified":true,"tenderers":[{"contactPoint":{"email":"popova.julia@pharmplanet.com.ua","name":"","telephone":"+380443915069"},"identifier":{"scheme":"UA-EDR","id":"36852896","legalName":""},"name":"","address":{"postalCode":"08171","countryName":"","streetAddress":"","region":"","locality":""}}],"date":"2017-07-27T15:00:49.897341+03:00","id":"6ce5b18702d14bc6b458edd8fafaa7bf","participationUrl":"https://auction.openprocurement.org/tenders/c9d2f876980a4c719e621d43e8cc1928/login?bidder_id=6ce5b18702d14bc6b458edd8fafaa7bf&hash=38f72345ff0460f575ff5d7284334e677c1db3ba"},{"status":"active","documents":[{"hash":"md5:f6c0da89629ab8dfe79e0cd73eb052a2","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/7203a5a5717d4ded8eada41252c3e723?KeyID=52462340&Signature=Zi8mrXSylUavHTkIgLa4n2mGzLrJ4NaYYamtUuAV9orAvtrcd2KNhOMjpL6NpG7P%252B4ninN4H%252BOt0pyVsJA0jDQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-28T09:51:57.025118+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-28T09:51:57.025138+03:00","id":"df17cd20c27f4a5d86a2a25504dee96c"},{"hash":"md5:00b11b05025352e198587961189a7d46","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/01837cf240104a2a8f73cf8d15b765b0?KeyID=52462340&Signature=lXR9xschtvEbqPkRjoYkEn1Fbg4mNHORO04aEy3dHPb8WpaPBujqA7RchIGNgX0IHJmGz8GdxFejgrBwp%252BoqDg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-28T09:51:57.025588+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-28T09:51:57.025607+03:00","id":"143e13c3ff934302bcfc449f04c23605"},{"hash":"md5:212a1f453937714382a11d9827bf0437","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/84792583e06a4c309c97a0f13e605ddc?KeyID=52462340&Signature=8XMilvb%2FzMe54tC2BudpWvJmet4NI2NoO8DudoF0kyNFFP4Ya1pbLpjYto5rsptKi8z5QeDQeuGF70fwk6JbCw%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-28T09:51:57.026067+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-28T09:51:57.026086+03:00","id":"198ab45defff418a85f3720069739f51"}],"selfEligible":true,"value":{"currency":"UAH","amount":1361928.1,"valueAddedTaxIncluded":true},"subcontractingDetails":"","selfQualified":true,"tenderers":[{"contactPoint":{"email":"lala.19@ukr.net","name":"","telephone":"+380672458377"},"identifier":{"scheme":"UA-EDR","id":"25184975","uri":"http://framco.com.ua","legalName":""},"name":"","address":{"postalCode":"61204","countryName":"","streetAddress":"","region":"","locality":""}}],"date":"2017-07-28T09:51:57.024521+03:00","id":"205955af6f964a638e28ec7fa7588e83","participationUrl":"https://auction.openprocurement.org/tenders/c9d2f876980a4c719e621d43e8cc1928/login?bidder_id=205955af6f964a638e28ec7fa7588e83&hash=218353122cd36a826049a96a3911bdcce3971e32"},{"status":"active","documents":[{"hash":"md5:6e8b0b26fc298ee5151849d0be316461","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/2c69eb0a299a4755bd3b98b37c209475?KeyID=52462340&Signature=fs91rVzgmtHF9GDl05%2Fg%252BIkwBjVIEbL1OT%252BqREG4%252BfVWse029%252BVnvC7qpR34qKpgxevlao2YwfcUJ8zc9zfNAg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-31T11:17:40.613937+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-31T11:17:40.613957+03:00","id":"4fc1ace6c2c2452abb12b16f23b4e7da"},{"hash":"md5:5f5367ccbfe6281f693b2fc23505332b","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/0780c7c3cd324948b133caaa6e01a949?KeyID=52462340&Signature=i%2FZf3AsWNbCZfhH%2FMPcgaVqY9pOrSE3cHuBE00ubRcX9sIion3gX0%2Fypa1J8mgVi8yp6vBYiZ1HH0db4lr8HAg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-31T11:17:40.614413+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-31T11:17:40.614433+03:00","id":"63396b82d3824f8aab3e948228888d3a"},{"hash":"md5:dc5d953b12862704ab4e9b6aa9adffd0","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/3072c1e2502543b991a1b546688fd116?KeyID=52462340&Signature=oyzS3O4tbC4QatImq%2F%252BMK25DO1oLj%2FivUc45cDL8Mcj%252BrsTxwy5OPaRN6RU23OODglJBqGWZkSenzkxrTXuIDQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-31T11:17:40.614899+03:00","documentType":"technicalSpecifications","dateModified":"2017-07-31T11:17:40.614918+03:00","id":"70751f6780ad433abcacfaadc4bba0c2"}],"selfEligible":true,"value":{"currency":"UAH","amount":1361804.84,"valueAddedTaxIncluded":true},"subcontractingDetails":"","selfQualified":true,"tenderers":[{"contactPoint":{"email":"eburyak@badm-b.biz","name":"","telephone":"+380567470245"},"identifier":{"scheme":"UA-EDR","id":"39273420","legalName":""},"name":"","address":{"postalCode":"49005","countryName":"","streetAddress":"","region":"","locality":""}}],"date":"2017-07-31T11:17:40.613307+03:00","id":"cc4fcb7f07af4916b57ae7088faf183b","participationUrl":"https://auction.openprocurement.org/tenders/c9d2f876980a4c719e621d43e8cc1928/login?bidder_id=cc4fcb7f07af4916b57ae7088faf183b&hash=f2062ebb6412fadd9a9172678585816d7204c318"}],"value":{"currency":"UAH","amount":1362000.0,"valueAddedTaxIncluded":true},"awardCriteria":"lowestCost"}}';

	    

	set @len =  JSON_LENGTH(@json, "$.data.bids");

	set @i = 0;

	

	WHILE @i < @len DO

		set @b = json_query(@json, concat("$.data.bids[",@i,"]"));

		select json_value(@b, "$.date"), json_value(@b, "$.id"), json_value(@b, "$.status");



		set @tenderersLen =  JSON_LENGTH(@b, "$.tenderers");

		set @j = 0;

		WHILE @j < @tenderersLen DO

			set @t = json_query(@b, concat("$.tenderers[",@j,"]"));

			select json_value(@t, "$.identifier.id"), json_value(@t, "$.identifier.scheme");

			

			SET @j = @j + 1;

		END WHILE;



   	SET @i = @i + 1;

	END WHILE;	

END */$$
DELIMITER ;

/* Procedure structure for procedure `sp_update_tender` */

DELIMITER $$

/*!50003 CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_update_tender`(

	IN `tender_json` LONGTEXT,

	IN `modified_date_string` VARCHAR(50),

	OUT `error_code` INT,

	OUT `error_description` LONGTEXT







)
BEGIN	

	declare tenderId bigint;

	declare tenderHashId varchar(50);

	declare dateString varchar(50);

	declare enquiryPeriodStartDate datetime(6);

	declare enquiryPeriodEndDate datetime(6);

	declare tenderDateModified datetime(6);



	declare statusId smallint;

	declare procurementMethodId smallint;

	declare procurementMethodTypeId smallint;

	declare brokerId smallint;

	declare brokerCode varchar(50);



	declare bidsLen smallint;

	declare tenderersLen smallint;

	# declare test_json longtext;

	declare bidHash varchar(50);

	declare bidId bigint;

	declare bidStatusCode varchar(50);

	declare bidStatusId smallint;

	

	declare bidDate datetime(6);

	

	declare tendererId int;

	declare tendererIdentifierId  varchar(50);

	declare tendererIdScheme varchar(50);

		

	declare b LONGTEXT;

	declare t LONGTEXT;

	declare i smallint;

	declare j smallint;

	

	

	set error_code = 0;

	set error_description = '';

	set tenderId = -1; #tender id

	set tenderHashId = '';  #tender hash (id from source db)



proc_code_label:BEGIN



	set dateString = JSON_VALUE(tender_json,'$.data.enquiryPeriod.startDate'); 	# 2017-05-18T17:39:20.351569+03:00

	set enquiryPeriodStartDate = fn_parse_utc_datetime(dateString);



	if enquiryPeriodStartDate is null then 

		set error_code = -11;

		set error_description = CONCAT('Bad enquiryPeriod.startDate: ', IFNULL(dateString,'NULL!'));	

	end if;



	if error_code = 0 then	

		set dateString = JSON_VALUE(tender_json,'$.data.enquiryPeriod.endDate'); 	# 2017-05-18T17:39:20+03:00 - no microseconds!

		set enquiryPeriodEndDate = fn_parse_utc_datetime(dateString);

		

		if enquiryPeriodEndDate is null then 

			set error_code = -12;

			set error_description = CONCAT('Bad enquiryPeriod.endDate: ', IFNULL(dateString,'NULL!'));	

		end if;	

	end if;

		

	if error_code = 0 then	

		set dateString = modified_date_string; # with microseconds

		set tenderDateModified = fn_parse_utc_datetime(dateString);



		if tenderDateModified is null then 

			set error_code = -13;

			set error_description = CONCAT('Bad dateModified: ', IFNULL(dateString,'NULL!'));	

		end if;

	end if;



	if error_code = 0 then	

		set tenderHashId = JSON_VALUE(tender_json,'$.data.id');

		if tenderHashId is null then

			set error_code = -14;

			set error_description = CONCAT('Bad or no tender hash ID: ', IFNULL(tenderHashId, 'NULL!'));

		end if;

	end if;



	if error_code = 0 then	

		set statusId := (select id FROM tender_statuses WHERE code = JSON_VALUE(tender_json,'$.data.status'));

		

		if statusId is null then

			set error_code = -3;

			set error_description = CONCAT('Bad status code: ', IFNULL(JSON_VALUE(tender_json,'$.data.status'),'NULL!'));

		end if;

	end if;

	

	if error_code = 0 then	

		set procurementMethodId := (select id FROM procurement_methods WHERE code = JSON_VALUE(tender_json,'$.data.procurementMethod'));

		

		if procurementMethodId is null then

			set error_code = -4;

			set error_description = CONCAT('Bad procurementMethod: ', IFNULL(JSON_VALUE(tender_json,'$.data.procurementMethod'),'NULL!'));

		end if;

	end if;

	

	if error_code = 0 then	

		set procurementMethodTypeId := (select id FROM procurement_method_types WHERE code = JSON_VALUE(tender_json,'$.data.procurementMethodType'));

		

		if procurementMethodTypeId is null then

			set error_code = -5;

			set error_description = CONCAT('Bad procurementMethodType: ', IFNULL(JSON_VALUE(tender_json,'$.data.procurementMethodType'),'NULL!'));

		end if;

	end if;		



	if error_code = 0 then	

		set brokerId := (select id FROM brokers WHERE code = JSON_VALUE(tender_json,'$.data.owner'));



		if brokerId is null then # rare case - new broker added			

			set brokerCode = JSON_VALUE(tender_json,'$.data.owner');

			

			if brokerCode is null or brokerCode = '' then

				set error_code = -1;

				set error_description = CONCAT('Bad broker code: ', IFNULL(brokerCode, 'NULL!'));

			else 

				insert into brokers (code) values (brokerCode); # not in tran, possibly can be inserted already by another query

			

				set brokerId := (select id FROM brokers WHERE code = brokerCode);

						

				if brokerId is null then

					set error_code = -2;

				end if;

			end if;

		end if;		

	end if;		

	

	if error_code = 0 then

		

		START TRANSACTION;

		

		set tenderId := (select id FROM tenders WHERE original_id = tenderHashId);

		if tenderId is not null and tenderId <> 0 then

			update tenders set 

				status_id = statusId,

				broker_id = brokerId,

				date_modified = tenderDateModified,

				enquiry_start_date = enquiryPeriodStartDate,

				enquiry_end_date =  enquiryPeriodEndDate,

				procurement_method_id = procurementMethodId,

				procurement_method_type_id = procurementMethodTypeId,

				updated_on = NOW(3)

			where id = tenderId;			

		else

			insert into tenders 

				(original_id, status_id, broker_id, date_modified, enquiry_start_date, enquiry_end_date, procurement_method_id, procurement_method_type_id)

			values (

				tenderHashId, statusId, brokerId,

				tenderDateModified, enquiryPeriodStartDate, enquiryPeriodEndDate,

				procurementMethodId, procurementMethodTypeId

			);



			# todo: last insert id?

			set tenderId := (select id FROM tenders WHERE original_id = tenderHashId);

		end if;



		# todo: probably needed only in update branch

		delete from tenderers_bids where bid_id in (select id from bids where tender_id = tenderId);

		delete from bids where tender_id = tenderId;

		

		set bidsLen =  JSON_LENGTH(tender_json, "$.data.bids");

		set i = 0;		

		

		#set test_json = '{"data":{"procurementMethod":"open","numberOfBids":3,"awardPeriod":{"startDate":"2017-08-01T14:36:30.446339+03:00","endDate":"2017-08-04T09:54:45.638521+03:00"},"complaintPeriod":{"startDate":"2017-07-13T13:24:19.108055+03:00","endDate":"2017-07-27T00:00:00+03:00"},"auctionUrl":"https://auction.openprocurement.org/tenders/c9d2f876980a4c719e621d43e8cc1928","enquiryPeriod":{"startDate":"2017-07-13T13:24:19.108055+03:00","clarificationsUntil":"2017-07-26T14:00:00+03:00","endDate":"2017-07-21T14:00:00+03:00","invalidationDate":"2017-07-13T13:33:00.698500+03:00"},"submissionMethod":"electronicAuction","procuringEntity":{"kind":"general","name":"","address":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"contactPoint":{"url":"http://www.emd.kh.ua","name_en":"Zhalinska Oksana Volodymyrivna","email":"kkt_cemd@ukr.net","name":"","telephone":"380577029453"},"identifier":{"scheme":"UA-EDR","legalName_en":"Municipal Health Care Institution Centre of Emergency Medical Aid and Catastrophe Medicine","id":"38494108","legalName":""},"name_en":"Municipal Health Care Institution Centre of Emergency Medical Aid and Catastrophe Medicine"},"owner":"e-tender.biz","id":"c9d2f876980a4c719e621d43e8cc1928","description":"","documents":[{"hash":"md5:083552e97391329242f4bef7996a2f6e","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/3f7796e6fc1244a29602260bcf074327?KeyID=52462340&Signature=VeykeJcaqy%252BDGaEkdi7A%252Bv7%252Bgl6pMvQkdyeE6IXkIcb3dfwlMfBDM7NyBlRGqmuUS6FwvkADq0FI07Lv5v5CAg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:27:00.460191+03:00","documentType":"biddingDocuments","dateModified":"2017-07-13T13:27:00.460213+03:00","id":"4cca7264e9d640d094a25771450928ee"},{"hash":"md5:7fa3613ba8b66cac7f997818e0d305f8","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/65efcdf01dce40d6bc6a103d702a38cb?KeyID=52462340&Signature=EtNJrjEw5xEjR8zVAeofSkRArhEdE2Su%252B9x6FfDDVtPKtwvfEqowEWt0wDM6OxFvlkdGYDIAXGlBN4EHz4EXDQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:27:40.794495+03:00","documentType":"eligibilityCriteria","dateModified":"2017-07-13T13:27:40.794516+03:00","id":"cf3431a9d85d4f3c8f8e4bd430a84ec0"},{"hash":"md5:b3f544fe7f585c93ad1585e8ebf251d8","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/cac4a2424bfd4c4ab842bb64dc80a0cd?KeyID=52462340&Signature=BwAZ1Tg5dPow%2FVMNx%2FjBgg4UYu1zpHVFnD%252BAQ3k1zBc9LqjK0NtqbBrXZgpkgoiB6deqPlsl%2F8SoOl9PdldVAA%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:28:25.936571+03:00","documentType":"contractProforma","dateModified":"2017-07-13T13:28:25.936624+03:00","id":"c9e9d17ff3014a489ff2216843114685"},{"hash":"md5:a2e16b232fb1fe8a46aae14a5be85f9e","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/72f0a46da1c143318ec8a28edb6aa6f4?KeyID=52462340&Signature=GOJC7YxPzafWjc%2FD5lKV7Bhyuqp4lnX90QaEGqdu2n9hA8oHJBQUTJ6cJdl6LgY9j2lUD98HRFPcqIt%2FOA03DQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:29:09.618430+03:00","documentType":"technicalSpecifications","dateModified":"2017-07-13T13:29:09.618451+03:00","id":"7820348fd8a74369891544b018982c69"},{"hash":"md5:1ca1649e4ddad98834f71f60c29d585a","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/c5576ee2dd564ebc8fd3a245a26f4d12?KeyID=52462340&Signature=h9g2tQZfzX%2F%252BYdi4g%252BQvYxzCYyE%2Fe%2FbQUt00r7Fjv6FHWZGSdH7qYYqbf0UcPmWd1kAduclRw%252Be95v4HjXX%252BDg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-13T13:29:09.943103+03:00","dateModified":"2017-07-13T13:29:09.943140+03:00","id":"9f1c4791d556442e8fe58785f91e9d12"},{"hash":"md5:090bee0cc090d62799cb6819496aef7f","author":"tender_owner","format":"application/pkcs7-signature","url":"https://public.docs.openprocurement.org/get/b7ae329ff3444a99897818adb63a4701?KeyID=52462340&Signature=KlxlYwMWFWk225BheGLrTViL%2F2X7LoIbrH7sKB%2F118l9scw7VwO0MpAfYENbVMG1MaW4zkDZ%252B0kmWY21mPiJAQ%253D%253D","title":"sign.p7s","documentOf":"tender","datePublished":"2017-07-13T13:33:00.697703+03:00","dateModified":"2017-07-13T13:33:00.697724+03:00","id":"2960c71e5d0e4199be6cd14678a5321a"},{"hash":"md5:53212f5af9c366beca2b6a77d4da4447","author":"auction","format":"text/plain","url":"https://public.docs.openprocurement.org/get/9fdd49b1bed04c718e96978dc40fc525?KeyID=52462340&Signature=%2F9Jm4pKaBwCXalcbVRs%252BjwleiIwmWN4OMqtZv%252BO9KbIH5JsXd%2FbWZlk5Y8ZcumEIGTRavDXYnwrrkbxnKtXgDw%253D%253D","title":"audit_c9d2f876980a4c719e621d43e8cc1928.yaml","documentOf":"tender","datePublished":"2017-08-01T14:36:29.366486+03:00","dateModified":"2017-08-01T14:36:29.366522+03:00","id":"7b0692728f7d4af3bae2e0f7a550874d"},{"hash":"md5:7c03b4681100d2231dc2def8653e29af","author":"auction","format":"text/plain","url":"https://public.docs.openprocurement.org/get/0f89825697a1431f885bcf0610819126?KeyID=52462340&Signature=4f6Vn4Ui0dW1D0ldGyn8YVnCxH2V%252BfneBgsApDgXFG1DodZz6YJIeFV7BNiHqByx2GxYkb29l8W9uFFUsGmDBw%253D%253D","title":"audit_c9d2f876980a4c719e621d43e8cc1928.yaml","documentOf":"tender","datePublished":"2017-08-01T14:36:29.366486+03:00","dateModified":"2017-08-01T14:36:30.760365+03:00","id":"7b0692728f7d4af3bae2e0f7a550874d"}],"title":"","tenderID":"UA-2017-07-13-001132-b","guarantee":{"currency":"UAH","amount":0.0},"dateModified":"2017-08-15T00:04:40.444240+03:00","status":"unsuccessful","tenderPeriod":{"startDate":"2017-07-13T13:24:19.108055+03:00","endDate":"2017-07-31T14:00:00+03:00"},"auctionPeriod":{"startDate":"2017-08-01T14:09:29+03:00","endDate":"2017-08-01T14:36:30.386402+03:00"},"procurementMethodType":"aboveThresholdUA","awards":[{"status":"unsuccessful","documents":[{"hash":"md5:5fb8d95b0de1aac748c5262359e34567","author":"bots","format":"application/yaml","url":"https://public.docs.openprocurement.org/get/9b65659ca3fb4075814cb03d63877ad4?KeyID=52462340&Signature=%252BaYv63d6%252Bylk%252BspaHebuiZxfxevClmPaWWTFVPabmW5XFtySFnDM%2FWEXVSc43hErfOe3u3Q9LOTVbJ%2F6Gg8XCw%253D%253D","title":"edr_identification.yaml","documentOf":"tender","datePublished":"2017-08-01T14:36:52.249918+03:00","documentType":"registerExtract","dateModified":"2017-08-01T14:36:52.249955+03:00","id":"606f50a8ea574154aea33b6b1f165232"},{"hash":"md5:124b09a1104037b4f58a79ff577facb6","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/1d31dbe1bbed4b448da1ee87372b827a?KeyID=52462340&Signature=kMwBgGsvlYQ043%252BWJMzwx29ZGmDmCtDEPbsz%2FdvSJpiZ0nhPJ3jU1Y19KEciEBEt9jBJiCi1vB9JFDWy36uUCw%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-02T10:27:50.864191+03:00","documentType":"awardNotice","dateModified":"2017-08-02T10:27:50.864212+03:00","id":"11daa1a20aaf4b84aaaa89b0fc82bc73"},{"hash":"md5:a188147e925be4aaebdf8ff1bcf510b6","author":"tender_owner","format":"application/pkcs7-signature","url":"https://public.docs.openprocurement.org/get/c811e2e0413042a989d872ada94fd103?KeyID=52462340&Signature=kRY9eHlcHuY8qr6hVoaZ0%2FsUToo9x1dg2j0JR02RY%2F%2Fxssgo3qIdlp9DhyAaGgFQrrwsa5Yt86GvwbdQKFsBDg%253D%253D","title":"sign.p7s","documentOf":"tender","datePublished":"2017-08-02T10:30:50.609072+03:00","dateModified":"2017-08-02T10:30:50.609094+03:00","id":"e4cbc1ef598b40179b8447a76acc9076"}],"description":"","title":"","suppliers":[{"contactPoint":{"email":"popova.julia@pharmplanet.com.ua","name":"","telephone":"+380443915069"},"identifier":{"scheme":"UA-EDR","id":"36852896","legalName":""},"name":"","address":{"postalCode":"08171","countryName":"","streetAddress":"","region":"","locality":""}}],"complaintPeriod":{"startDate":"2017-08-01T14:36:30.447710+03:00","endDate":"2017-08-13T00:00:00+03:00"},"bid_id":"6ce5b18702d14bc6b458edd8fafaa7bf","value":{"currency":"UAH","amount":1342561.1,"valueAddedTaxIncluded":true},"qualified":false,"date":"2017-08-02T10:38:27.581750+03:00","eligible":false,"id":"a65b3a7561f04ecbb92018cc69c4f274"},{"status":"unsuccessful","documents":[{"hash":"md5:732a3b08eb0ce9411bf66cfd2f3327e0","author":"bots","format":"application/yaml","url":"https://public.docs.openprocurement.org/get/c245785936254a7d8c252e019df11b9a?KeyID=52462340&Signature=IOlWY9h78ltZxjpv6QSNDEqKrOJHd6x%2FDIo7Vuv073%252B6zjVO%2F8HeMMu2ilWYTOwl%2F578K2sjE5W8m2ee8XYYCw%253D%253D","title":"edr_identification.yaml","documentOf":"tender","datePublished":"2017-08-02T10:38:42.411357+03:00","documentType":"registerExtract","dateModified":"2017-08-02T10:38:42.411377+03:00","id":"566b0fe5b3e94f04a0a56c25ed5e0f79"},{"hash":"md5:06b2eb60d0c0bb3086849bfd28302eed","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/31673c132d1d4c549433c699112ed2b2?KeyID=52462340&Signature=y5v2%2FRFgfqs5bA5nSu0YZVWiuBb1rmhsEIZ45aZMZX5%252BQiN6IocwLj6hfKnhBMsANNCTawO27j9elndJwt1SDQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-03T10:31:04.959046+03:00","documentType":"awardNotice","dateModified":"2017-08-03T10:31:04.959068+03:00","id":"11d525f14f5d435ab945d1e85e0cb2ba"},{"hash":"md5:edcacfe64c2eda3f63cdeb796e8370be","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/0e586aac1d144da78898ad686285f9dc?KeyID=52462340&Signature=ACF5TqW%2FwY%2FOEIqyTvQtXtuzWwtFnk%2FLL1k1vPmzgNf%2FLRblJMiKsHybntZB%2FMTU375fTK%252BbtwGbbF3Wj6mRAQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-03T10:34:17.069340+03:00","documentType":"awardNotice","dateModified":"2017-08-03T10:34:17.069375+03:00","id":"0797838681aa4e499d0e740c9f372ace"},{"hash":"md5:a969ddf266277efd628ca3729a1cbb92","author":"tender_owner","format":"application/pkcs7-signature","url":"https://public.docs.openprocurement.org/get/10497c8bc00a434e9a467a6d808d567e?KeyID=52462340&Signature=UF9Va5Zld02suSRQ%252BrvtiNrl80r%2Fyhm8Ui%2FeTfWQEt37D6GvCF4q2mfFiWSZj%2FXWMVcJx0yvan%2FsnwyMPGJHCA%253D%253D","title":"sign.p7s","documentOf":"tender","datePublished":"2017-08-03T10:37:33.614003+03:00","dateModified":"2017-08-03T10:37:33.614024+03:00","id":"e77ad02958824ce9987107d33ed5aa60"}],"description":"","title":"","suppliers":[{"contactPoint":{"email":"eburyak@badm-b.biz","name":"","telephone":"+380567470245"},"identifier":{"scheme":"UA-EDR","id":"39273420","legalName":""},"name":"","address":{"postalCode":"49005","countryName":"","streetAddress":"","region":"","locality":""}}],"complaintPeriod":{"startDate":"2017-08-02T10:38:27.570342+03:00","endDate":"2017-08-14T00:00:00+03:00"},"bid_id":"cc4fcb7f07af4916b57ae7088faf183b","value":{"currency":"UAH","amount":1361804.84,"valueAddedTaxIncluded":true},"qualified":false,"date":"2017-08-03T10:39:00.693874+03:00","eligible":false,"id":"269ad74d1a0440e0829e59cb4916bb7b"},{"status":"unsuccessful","documents":[{"hash":"md5:62190919da068017491597182ae0994f","author":"bots","format":"application/yaml","url":"https://public.docs.openprocurement.org/get/6124ef107cb7404c913df1c00b15968d?KeyID=52462340&Signature=xjEl15nbY7Rci3un5UIOCDJtgGLsweG3xgmrX5yVuuba9varmAgfDiTsX8OP8GN7tqbG2BaEdXzqrtycHb8TAg%253D%253D","title":"edr_identification.yaml","documentOf":"tender","datePublished":"2017-08-03T10:39:10.451241+03:00","documentType":"registerExtract","dateModified":"2017-08-03T10:39:10.451262+03:00","id":"e3bfd381fc8e47928edf1fc5b3fdf226"},{"hash":"md5:3735674223a5b8c2a42836e41ee97e7f","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/1c27ddd9ec9b42eab6d0309708bb6ebf?KeyID=52462340&Signature=JIQKIwyRihevLmV9uAAfv%252BCmwEolpGHpEnermxFySiXrGvjEvUOU6IEk2RIUzsxYfAgNHqWHv60N%2FWP8tS5UBA%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-04T09:50:46.234182+03:00","documentType":"awardNotice","dateModified":"2017-08-04T09:50:46.234203+03:00","id":"7292d594d4f04a1091293014fdf60f95"},{"hash":"md5:4427ffa39cb046ad561605a97e153dd7","author":"tender_owner","format":"text/plain","url":"https://public.docs.openprocurement.org/get/02299f4432bf4871b39f8fca5d3d0c35?KeyID=52462340&Signature=ZhuaF8yDhAdCww46GDr8drEWubdGq%252BJHky2B7%252Bt%2FBWtBnEVvUswNC6N1XOMHRh7PcBPl9xiDXfWpMMHNxyDWBg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-08-04T09:52:12.590293+03:00","documentType":"awardNotice","dateModified":"2017-08-04T09:52:12.590321+03:00","id":"fc6971ab2c9947cdb8fbc1f14809700f"},{"hash":"md5:49136caa10c46c6250523d409c160f9c","author":"tender_owner","format":"application/pkcs7-signature","url":"https://public.docs.openprocurement.org/get/5da946d3ff7d4843bf9a158e1d5b9b15?KeyID=52462340&Signature=A2dRdfzCQt4bE96BYwkhGM2NBhYdAjW15ASIJUI8SXRFGQflO4qhVJpXPjoDhIhmJP%2FJX0mpfmt6202POjM2Cw%253D%253D","title":"sign.p7s","documentOf":"tender","datePublished":"2017-08-04T09:53:23.369352+03:00","dateModified":"2017-08-04T09:53:23.369389+03:00","id":"1ba0cf57d61947ee9ca3a1f8364bfbe4"}],"description":"","title":"","suppliers":[{"contactPoint":{"email":"lala.19@ukr.net","name":"","telephone":"+380672458377"},"identifier":{"scheme":"UA-EDR","id":"25184975","uri":"http://framco.com.ua","legalName":""},"name":"","address":{"postalCode":"61204","countryName":"","streetAddress":"","region":"","locality":""}}],"complaintPeriod":{"startDate":"2017-08-03T10:39:00.682268+03:00","endDate":"2017-08-15T00:00:00+03:00"},"bid_id":"205955af6f964a638e28ec7fa7588e83","value":{"currency":"UAH","amount":1361928.1,"valueAddedTaxIncluded":true},"qualified":false,"date":"2017-08-04T09:54:45.651520+03:00","eligible":false,"id":"ac0cec9426484c7392b47e964cd0874b"}],"date":"2017-08-15T00:04:40.444240+03:00","minimalStep":{"currency":"UAH","amount":681.0,"valueAddedTaxIncluded":true},"items":[{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"edfb854fe545475f8e16814d36b95fed","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"925abfc889e34645ab978784a631e188","unit":{"code":"PK","name":""},"quantity":400},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"9697cc26dc094e56b2b0f1337a99004a","unit":{"code":"VI","name":""},"quantity":400},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"21dd7fd215de4dd3ab6ec4d68d91b452","unit":{"code":"PK","name":""},"quantity":1000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"733963d9da3844f28951c7931ec019cb","unit":{"code":"PK","name":""},"quantity":500},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"a89ea5baeb7a4475804dfa53c113c10f","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"6bd363b0d332487ba97b0a089dc8e81e","unit":{"code":"PK","name":""},"quantity":1500},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"87f0331c4e974f28af90f7bf42822fc9","unit":{"code":"PK","name":""},"quantity":200},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"d3dfd8720cfd4eccaf08a63b9ff502db","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"cfaa6b1b8ca34c07a7607dd508b99343","unit":{"code":"PK","name":""},"quantity":1500},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"83e0f8f848834d3498942595e6f99cb2","unit":{"code":"PK","name":""},"quantity":30},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"6516e3b7ddfe45d79a7d8e468380e2f3","unit":{"code":"PK","name":""},"quantity":1000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"9caa9b60f4294e5f82519cbdd2d53037","unit":{"code":"PK","name":""},"quantity":750},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"db629c64657e467f8975fc6c491f6a09","unit":{"code":"VI","name":""},"quantity":400},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"d04585588962424ca3e11fde185bacd8","unit":{"code":"PK","name":""},"quantity":1000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"c2ba767e664e4db19c560cf7e41d3353","unit":{"code":"PK","name":""},"quantity":250},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"5e97147d51ea4a07af548c42a16e1e1a","unit":{"code":"VI","name":""},"quantity":800},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"cd0e232ed4474b8192f9db060898ef66","unit":{"code":"VI","name":""},"quantity":500},{"description":"A","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"5216668a8874446f8562c636ca7232fb","unit":{"code":"PK","name":""},"quantity":500},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"c769fb88d4c64d928dd5230b65ecd045","unit":{"code":"PK","name":""},"quantity":3000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"4026b824a3624d6c9cd0791c7a9428d1","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"57528847fdcd4018944f8de1676ed0c4","unit":{"code":"PK","name":""},"quantity":100},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"117ce1dd13c74a058854b6d979e7754f","unit":{"code":"PK","name":""},"quantity":50},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"9fcd61a2b5f44e188ca97561c1b25c97","unit":{"code":"PK","name":""},"quantity":300},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"e23c4dac0a5f46be872470a7ab1a8d58","unit":{"code":"VI","name":""},"quantity":2000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"2075b72d653b488e8b684a413d82fe5d","unit":{"code":"PK","name":""},"quantity":300},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"4257b7acdd71499183c87cd1952aa56c","unit":{"code":"PK","name":""},"quantity":600},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"7de597a967f240bfa943096ca9eeb644","unit":{"code":"PK","name":""},"quantity":450},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"cbd53a5b18d1458985e788909800e29a","unit":{"code":"PK","name":""},"quantity":5000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"a697560962254dddbfc896416676d3d2","unit":{"code":"PK","name":""},"quantity":200},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"92af9cf6ac124740a6f334896da273b7","unit":{"code":"PK","name":""},"quantity":5000},{"description":"","classification":{"scheme":"","description":"","id":"33600000-6"},"deliveryAddress":{"postalCode":"61058","countryName":"","streetAddress":"","region":"","locality":""},"deliveryDate":{"endDate":"2017-12-31T00:00:00+02:00"},"id":"1a0a6b0051614e9a807f10699e6bcb42","unit":{"code":"PK","name":""},"quantity":350}],"bids":[{"status":"active","documents":[{"hash":"md5:c2fdedb41b6e46bfc38fe48fe41ff415","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/15163eeb93e84631acb2402b65535eac?KeyID=52462340&Signature=TUOpQnzEuvnb7jD2eZcAo3Ny2sYSj3CK49Cv61ib6bSuYHKDwn%2F5Q83hpzmPwYsk5o%252BAX9WffFoo7olQIrAWCg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-27T15:00:49.898346+03:00","dateModified":"2017-07-27T15:00:49.898381+03:00","id":"03a0bd1a7fbe4910866ab6bc4f1932a8"},{"hash":"md5:3cdd6c6374699c72fcd42933242d53d7","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/5a9a6d956b894f78a766c79a12ec0883?KeyID=52462340&Signature=jMiEDOTSIKzALrz2uUAI0BlPVL9qcsroDJGkJUtQ5eXnTgD5gKAkNI1F65AeQoOJtfTZbQLAp0c3YiKBAbCCCA%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-27T15:00:49.899173+03:00","dateModified":"2017-07-27T15:00:49.899208+03:00","id":"1458722127474353ba2849375fb0a983"}],"selfEligible":true,"value":{"currency":"UAH","amount":1342561.1,"valueAddedTaxIncluded":true},"subcontractingDetails":"","selfQualified":true,"tenderers":[{"contactPoint":{"email":"popova.julia@pharmplanet.com.ua","name":"","telephone":"+380443915069"},"identifier":{"scheme":"UA-EDR","id":"36852896","legalName":""},"name":"","address":{"postalCode":"08171","countryName":"","streetAddress":"","region":"","locality":""}}],"date":"2017-07-27T15:00:49.897341+03:00","id":"6ce5b18702d14bc6b458edd8fafaa7bf","participationUrl":"https://auction.openprocurement.org/tenders/c9d2f876980a4c719e621d43e8cc1928/login?bidder_id=6ce5b18702d14bc6b458edd8fafaa7bf&hash=38f72345ff0460f575ff5d7284334e677c1db3ba"},{"status":"active","documents":[{"hash":"md5:f6c0da89629ab8dfe79e0cd73eb052a2","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/7203a5a5717d4ded8eada41252c3e723?KeyID=52462340&Signature=Zi8mrXSylUavHTkIgLa4n2mGzLrJ4NaYYamtUuAV9orAvtrcd2KNhOMjpL6NpG7P%252B4ninN4H%252BOt0pyVsJA0jDQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-28T09:51:57.025118+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-28T09:51:57.025138+03:00","id":"df17cd20c27f4a5d86a2a25504dee96c"},{"hash":"md5:00b11b05025352e198587961189a7d46","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/01837cf240104a2a8f73cf8d15b765b0?KeyID=52462340&Signature=lXR9xschtvEbqPkRjoYkEn1Fbg4mNHORO04aEy3dHPb8WpaPBujqA7RchIGNgX0IHJmGz8GdxFejgrBwp%252BoqDg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-28T09:51:57.025588+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-28T09:51:57.025607+03:00","id":"143e13c3ff934302bcfc449f04c23605"},{"hash":"md5:212a1f453937714382a11d9827bf0437","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/84792583e06a4c309c97a0f13e605ddc?KeyID=52462340&Signature=8XMilvb%2FzMe54tC2BudpWvJmet4NI2NoO8DudoF0kyNFFP4Ya1pbLpjYto5rsptKi8z5QeDQeuGF70fwk6JbCw%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-28T09:51:57.026067+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-28T09:51:57.026086+03:00","id":"198ab45defff418a85f3720069739f51"}],"selfEligible":true,"value":{"currency":"UAH","amount":1361928.1,"valueAddedTaxIncluded":true},"subcontractingDetails":"","selfQualified":true,"tenderers":[{"contactPoint":{"email":"lala.19@ukr.net","name":"","telephone":"+380672458377"},"identifier":{"scheme":"UA-EDR","id":"25184975","uri":"http://framco.com.ua","legalName":""},"name":"","address":{"postalCode":"61204","countryName":"","streetAddress":"","region":"","locality":""}}],"date":"2017-07-28T09:51:57.024521+03:00","id":"205955af6f964a638e28ec7fa7588e83","participationUrl":"https://auction.openprocurement.org/tenders/c9d2f876980a4c719e621d43e8cc1928/login?bidder_id=205955af6f964a638e28ec7fa7588e83&hash=218353122cd36a826049a96a3911bdcce3971e32"},{"status":"active","documents":[{"hash":"md5:6e8b0b26fc298ee5151849d0be316461","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/2c69eb0a299a4755bd3b98b37c209475?KeyID=52462340&Signature=fs91rVzgmtHF9GDl05%2Fg%252BIkwBjVIEbL1OT%252BqREG4%252BfVWse029%252BVnvC7qpR34qKpgxevlao2YwfcUJ8zc9zfNAg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-31T11:17:40.613937+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-31T11:17:40.613957+03:00","id":"4fc1ace6c2c2452abb12b16f23b4e7da"},{"hash":"md5:5f5367ccbfe6281f693b2fc23505332b","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/0780c7c3cd324948b133caaa6e01a949?KeyID=52462340&Signature=i%2FZf3AsWNbCZfhH%2FMPcgaVqY9pOrSE3cHuBE00ubRcX9sIion3gX0%2Fypa1J8mgVi8yp6vBYiZ1HH0db4lr8HAg%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-31T11:17:40.614413+03:00","documentType":"qualificationDocuments","dateModified":"2017-07-31T11:17:40.614433+03:00","id":"63396b82d3824f8aab3e948228888d3a"},{"hash":"md5:dc5d953b12862704ab4e9b6aa9adffd0","format":"application/pdf","url":"https://public.docs.openprocurement.org/get/3072c1e2502543b991a1b546688fd116?KeyID=52462340&Signature=oyzS3O4tbC4QatImq%2F%252BMK25DO1oLj%2FivUc45cDL8Mcj%252BrsTxwy5OPaRN6RU23OODglJBqGWZkSenzkxrTXuIDQ%253D%253D","title":"","documentOf":"tender","datePublished":"2017-07-31T11:17:40.614899+03:00","documentType":"technicalSpecifications","dateModified":"2017-07-31T11:17:40.614918+03:00","id":"70751f6780ad433abcacfaadc4bba0c2"}],"selfEligible":true,"value":{"currency":"UAH","amount":1361804.84,"valueAddedTaxIncluded":true},"subcontractingDetails":"","selfQualified":true,"tenderers":[{"contactPoint":{"email":"eburyak@badm-b.biz","name":"","telephone":"+380567470245"},"identifier":{"scheme":"UA-EDR","id":"39273420","legalName":""},"name":"","address":{"postalCode":"49005","countryName":"","streetAddress":"","region":"","locality":""}}],"date":"2017-07-31T11:17:40.613307+03:00","id":"cc4fcb7f07af4916b57ae7088faf183b","participationUrl":"https://auction.openprocurement.org/tenders/c9d2f876980a4c719e621d43e8cc1928/login?bidder_id=cc4fcb7f07af4916b57ae7088faf183b&hash=f2062ebb6412fadd9a9172678585816d7204c318"}],"value":{"currency":"UAH","amount":1362000.0,"valueAddedTaxIncluded":true},"awardCriteria":"lowestCost"}}';

		

		WHILE i < bidsLen DO			

			

			set b = json_query(tender_json, concat("$.data.bids[",i,"]"));

			

			set bidHash = json_value(b, "$.id");

			if bidHash is null then 

				set error_code = -21;

				set error_description = CONCAT('Bad bid id: ', IFNULL(bidHash, 'NULL!'), ' for tender ', tenderHashId, ' bid N ', i);

				ROLLBACK;

				LEAVE proc_code_label;

			end if;

			

			set bidStatusCode = json_value(b, "$.status");

			set bidStatusId = (select id from bid_statuses where code = bidStatusCode);

			if bidStatusId is null then 

				set error_code = -22;

				set error_description = CONCAT('Bad or unknown bid status: ', IFNULL(bidStatusCode, 'NULL!'), ' for tender ', tenderHashId, ' bid ', i);

				ROLLBACK;

				LEAVE proc_code_label;

			end if;

			

			set dateString = json_value(b, "$.date");

			set bidDate = fn_parse_utc_datetime(dateString);

	

			# deleted and unsuccessfull bids has no date (or need auth!)

#			if bidDate is null then  

#				set error_code = -23;

#				set error_description = CONCAT('Bad bid date: ', IFNULL(dateString, 'NULL!'), ' for bid ', bidHash, ' of tender ', tenderHashId);

#				ROLLBACK;

#				LEAVE proc_code_label;

#			end if;		

		

			insert into bids (tender_id, original_id, bid_date, status_id)

			values (tenderId, bidHash, bidDate, bidStatusId);

			

			# todo: last insert id?

			set bidId = (select id from bids where original_id = bidHash);

	

			set tenderersLen =  JSON_LENGTH(b, "$.tenderers");

			

			set j = 0;

			WHILE j < tenderersLen DO

				set t = json_query(b, concat("$.tenderers[",j,"]"));

								

				set tendererIdentifierId = json_value(t, "$.identifier.id");				

				if tendererIdentifierId is null then 

					set error_code = -24;

					set error_description = CONCAT('Bad tenderer identifier id: ', IFNULL(tendererIdentifierId, 'NULL!'), ' for bid ', bidId);

					ROLLBACK;

					LEAVE proc_code_label;

				end if;

				

				set tendererIdScheme = json_value(t, "$.identifier.scheme");

				if tendererIdScheme is null then 

					set error_code = -25;

					set error_description = CONCAT('Bad tenderer id scheme: ', IFNULL(tendererIdScheme, 'NULL!'), ' for bid ', bidId);

					ROLLBACK;

					LEAVE proc_code_label;

				end if;				

				

				set tendererId = (select id from tenderers where identifier = tendererIdentifierId);

				if tendererId is null then

					insert into tenderers (identifier, scheme) values (tendererIdentifierId, tendererIdScheme);

				end if;

				

				# todo: last insert id?

				set tendererId = (select id from tenderers where identifier = tendererIdentifierId);

				

				insert into tenderers_bids (tenderer_id, bid_id) values (tendererId, bidId);

				

				SET j = j + 1;

			END WHILE;

	

	   	SET i = i + 1;

		END WHILE;	

		

		COMMIT;

		

	end if;

END;

END */$$
DELIMITER ;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
