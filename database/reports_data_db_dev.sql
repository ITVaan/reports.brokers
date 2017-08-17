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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

/*Table structure for table `procurement_method_types` */

CREATE TABLE `procurement_method_types` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

/*Table structure for table `statuses` */

CREATE TABLE `statuses` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;

/*Table structure for table `tenders` */

CREATE TABLE `tenders` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Числовое ИД тендера в базе отчётов',
  `original_id` char(32) NOT NULL COMMENT 'ИД (хеш) тендера из базы прозорро',
  `status_id` smallint(6) unsigned NOT NULL,
  `broker_id` int(10) unsigned NOT NULL,
  `date_modified` datetime(6) NOT NULL,
  `created_on` timestamp(3) NOT NULL DEFAULT current_timestamp(3),
  `updated_on` timestamp(3) NOT NULL DEFAULT current_timestamp(3) ON UPDATE current_timestamp(3),
  `enquiry_start_date` datetime(6) NOT NULL,
  `enquiry_end_date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `original_id` (`original_id`),
  KEY `FK_tender_broker` (`broker_id`),
  KEY `FK_tender_status` (`status_id`),
  CONSTRAINT `FK_tender_broker` FOREIGN KEY (`broker_id`) REFERENCES `brokers` (`id`),
  CONSTRAINT `FK_tender_status` FOREIGN KEY (`status_id`) REFERENCES `statuses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=302 DEFAULT CHARSET=utf8;

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

/* Procedure structure for procedure `sp_update_tender` */

DELIMITER $$

/*!50003 CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_update_tender`(
	IN `tender_json` LONGTEXT,
	IN `modified_date_string` VARCHAR(50),
	OUT `error_code` INT,
	OUT `error_description` VARCHAR(100)






)
BEGIN	
	set error_code = 0;
	set error_description = '';

	set @dateString = JSON_VALUE(tender_json,'$.data.enquiryPeriod.startDate'); 	# 2017-05-18T17:39:20.351569+03:00
	set @timeZone = '+00:00';

	IF SUBSTRING(@dateString, 27, 1) = '+' or SUBSTRING(@dateString, 27, 1) = '-' THEN 
		set @timeZone = SUBSTRING(@dateString, 27, 6);
	end if;

	set @enquiryPeriodStartDate = CONVERT_TZ(STR_TO_DATE(@dateString, '%Y-%m-%dT%H:%i:%s.%f'), @timeZone, '+00:00');	
	if @enquiryPeriodStartDate is null then #may be date without microseconds
		IF SUBSTRING(@dateString, 20, 1) = '+' or SUBSTRING(@dateString, 20, 1) = '-' THEN 
			set @timeZone = SUBSTRING(@dateString, 20, 6);
		end if;	
		set @enquiryPeriodStartDate = CONVERT_TZ(STR_TO_DATE(@dateString, '%Y-%m-%dT%H:%i:%s'), @timeZone, '+00:00');	
	end if;
	
	if @enquiryPeriodStartDate is null then 
		set error_code = -11;
		set error_description = CONCAT('Bad enquiryPeriod.startDate: ', IFNULL(@dateString,'NULL!'));	
	end if;

	if error_code = 0 then	
		set @dateString = JSON_VALUE(tender_json,'$.data.enquiryPeriod.endDate'); 	# 2017-05-18T17:39:20+03:00 - no microseconds!
		IF SUBSTRING(@dateString, 20, 1) = '+' or SUBSTRING(@dateString, 20, 1) = '-' THEN 
			set @timeZone = SUBSTRING(@dateString, 20, 6);
		end if;	
		
		set @enquiryPeriodEndDate = CONVERT_TZ(STR_TO_DATE(@dateString, '%Y-%m-%dT%H:%i:%s'), @timeZone, '+00:00');	
		
		if @enquiryPeriodEndDate is null then 
			set error_code = -12;
			set error_description = CONCAT('Bad enquiryPeriod.endDate: ', IFNULL(@dateString,'NULL!'));	
		end if;	
	end if;
		
	if error_code = 0 then	
		set @dateString = modified_date_string; # with microseconds
		IF SUBSTRING(@dateString, 27, 1) = '+' or SUBSTRING(@dateString, 27, 1) = '-' THEN 
			set @timeZone = SUBSTRING(@dateString, 27, 6);
		end if;	
		
		set @tenderDateModified = CONVERT_TZ(STR_TO_DATE(@dateString, '%Y-%m-%dT%H:%i:%s.%f'), @timeZone, '+00:00');	
		if @tenderDateModified is null then 
			set error_code = -13;
			set error_description = CONCAT('Bad dateModified: ', IFNULL(@dateString,'NULL!'));	
		end if;			
	end if;

	if error_code = 0 then	
		set @tenderHashId = JSON_VALUE(tender_json,'$.data.id');
		if @tenderHashId is null then
			set error_code = -14;
			set error_description = CONCAT('Bad or no tender hash ID: ', IFNULL(@tenderHashId, 'NULL!'));
		end if;
	end if;

	if error_code = 0 then	
		set @statusId := (select id FROM statuses WHERE code = JSON_VALUE(tender_json,'$.data.status'));
		
		if @statusId is null then
			set error_code = -3;
			set error_description = CONCAT('Bad status code: ', IFNULL(JSON_VALUE(tender_json,'$.data.status'),'NULL!'));
		end if;
	end if;

	if error_code = 0 then
	
		set @brokerId := (select id FROM brokers WHERE code = JSON_VALUE(tender_json,'$.data.owner'));

		if @brokerId is null then # very rare case			
			
			set @brokerCode = JSON_VALUE(tender_json,'$.data.owner');
			
			if @brokerCode is null or @brokerCode = '' then
				set error_code = -1;
				set error_description = CONCAT('Bad broker code: ', IFNULL(@brokerCode, 'NULL!'));
			else 
				insert into brokers (code) values (@brokerCode); # not in tran, possibly can be inserted already by another query
			
				set @brokerId := (select id FROM brokers WHERE code = @brokerCode);
						
				if @brokerId is null then
					set error_code = -2;
				end if;
			end if;
		end if;		
	end if;		
	
	if error_code = 0 then
		
		START TRANSACTION;
		
		set @id := (select id FROM tenders WHERE original_id = @tenderHashId);		
		if @id <> 0 then
			update tenders set 
				status_id = @statusId,
				broker_id = @brokerId,
				date_modified = @tenderDateModified,
				enquiry_start_date = @enquiryPeriodStartDate,
				enquiry_end_date =  @enquiryPeriodEndDate,
				updated_on = NOW(3)
			where id = @id;
		else
			insert into tenders (original_id, status_id, broker_id, date_modified, enquiry_start_date, enquiry_end_date)
			values (
				@tenderHashId, @statusId, @brokerId,
				@tenderDateModified, @enquiryPeriodStartDate, @enquiryPeriodEndDate
			);
		end if;
		
		COMMIT;
		
	end if;
END */$$
DELIMITER ;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
