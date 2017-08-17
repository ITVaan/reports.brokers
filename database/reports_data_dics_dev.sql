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
/*Data for the table `procurement_method_types` */

insert  into `procurement_method_types`(`id`,`code`) values (2,'aboveThresholdEU');
insert  into `procurement_method_types`(`id`,`code`) values (1,'aboveThresholdUA');
insert  into `procurement_method_types`(`id`,`code`) values (3,'aboveThresholdUA.defense');
insert  into `procurement_method_types`(`id`,`code`) values (6,'belowThreshold');
insert  into `procurement_method_types`(`id`,`code`) values (5,'competitiveDialogueEU.stage2');
insert  into `procurement_method_types`(`id`,`code`) values (4,'competitiveDialogueUA.stage2');

/*Data for the table `statuses` */

insert  into `statuses`(`id`,`code`) values (3,'active.auction');
insert  into `statuses`(`id`,`code`) values (5,'active.awarded');
insert  into `statuses`(`id`,`code`) values (1,'active.enquiries');
insert  into `statuses`(`id`,`code`) values (9,'active.pre-qualification');
insert  into `statuses`(`id`,`code`) values (4,'active.qualification');
insert  into `statuses`(`id`,`code`) values (2,'active.tendering');
insert  into `statuses`(`id`,`code`) values (8,'cancelled');
insert  into `statuses`(`id`,`code`) values (7,'complete');
insert  into `statuses`(`id`,`code`) values (6,'unsuccessful');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
