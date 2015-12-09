USE fsriotemp;

delimiter $$

CREATE TABLE `agency_data` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `AGENCY_FULL_NAME` varchar(255) DEFAULT NULL,
  `AGENCY_ACRONYM` varchar(255) DEFAULT NULL,
  `US_GOVT` tinyint(4) NOT NULL DEFAULT '0',
  `DATE_ENTERED` date NOT NULL,
  `AGENCY_URL` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=153 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `agency_hierarchy` (
  `aid` int(11) NOT NULL DEFAULT '0' COMMENT 'The agency.ID of the agency.',
  `parent` int(11) NOT NULL DEFAULT '0' COMMENT 'The agency.ID of the agency''s parent. 0 indicates no parent.',
  PRIMARY KEY (`aid`,`parent`),
  KEY `parent` (`parent`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Stores the hierarchical relationship between agencies.'$$

delimiter $$

CREATE TABLE `agency_index` (
  `pid` int(11) NOT NULL DEFAULT '0' COMMENT 'The projects.ID of the linked project',
  `aid` int(11) NOT NULL DEFAULT '0' COMMENT 'The agency.ID of the linked agency',
  KEY `pid` (`pid`),
  KEY `aid` (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Maintains denormalized information about project/agency relationships.'$$

delimiter $$

CREATE TABLE `ars_publication_data` (
  `pub_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'The primary identifier for a publication',
  `status` int(1) NOT NULL DEFAULT '1' COMMENT 'The publication status of the article: 1 - pending, 2 - epub, 3 - printed.',
  `log_number` int(11) NOT NULL COMMENT 'The log number of the publication',
  `title` varchar(512) CHARACTER SET latin1 NOT NULL COMMENT 'The title of the publication',
  `journal` varchar(255) CHARACTER SET latin1 NOT NULL COMMENT 'The name of the journal which accepted the publication',
  `summary` longtext CHARACTER SET latin1 NOT NULL COMMENT 'An interpretive summary of the publication',
  `authors` longtext CHARACTER SET latin1 NOT NULL COMMENT 'The authors of the publication',
  `accepted_year` int(4) NOT NULL COMMENT 'The year that the article was accepted for publication',
  `accepted_month` int(2) NOT NULL COMMENT 'The month that the article was accepted for publication',
  `accepted_day` int(2) NOT NULL COMMENT 'The day that the article was accepted for publication',
  `url` varchar(255) CHARACTER SET latin1 NOT NULL DEFAULT '' COMMENT 'The URL to an online copy of the published publication',
  `naldc_url` varchar(255) NOT NULL DEFAULT '' COMMENT 'The URL of the publication''s full text in the NAL Digital Collections.',
  `publication_year` int(4) NOT NULL COMMENT 'Part of the citation - the journal issue''s year of printing',
  `publication_month` int(2) NOT NULL COMMENT 'Part of the citation - the journal issue''s month of printing',
  `publication_day` int(2) NOT NULL COMMENT 'Part of the citation - the journal issue''s day of printing',
  `volume` varchar(7) NOT NULL COMMENT 'Part of the citation - the journal issue''s volume number',
  `issue` varchar(10) NOT NULL COMMENT 'Part of the citation - the journal issue number',
  `pages` varchar(20) CHARACTER SET latin1 NOT NULL COMMENT 'Part of the citation - the page numbers of the article in the journal issue',
  `created` int(11) NOT NULL COMMENT 'The unix timestamp of when the record was created',
  `changed` int(11) NOT NULL COMMENT 'The UNIX timestamp when the record was last updated.',
  PRIMARY KEY (`pub_id`),
  FULLTEXT KEY `publication_data` (`title`,`authors`,`summary`)
) ENGINE=MyISAM AUTO_INCREMENT=2076 DEFAULT CHARSET=utf8 COMMENT='A list of food safety USDA ARS publications'$$


delimiter $$

CREATE TABLE `ars_publication_index` (
  `pid` int(11) NOT NULL COMMENT 'The project.pid of the linked project',
  `pub_id` int(11) NOT NULL COMMENT 'The publication_data.pub_id of the linked publication',
  KEY `pid` (`pid`),
  KEY `pub_id` (`pub_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Lists project/publication relationships'$$


delimiter $$

CREATE TABLE `cache_agency_children` (
  `aid` int(11) NOT NULL COMMENT 'The agency.ID of the parent agency.',
  `children` blob COMMENT 'A serialized array of child agency IDs.',
  `expire` int(11) NOT NULL DEFAULT '0' COMMENT 'A Unix timestamp indicating when the cache entry should expire, or 0 for never.',
  `created` int(11) NOT NULL DEFAULT '0' COMMENT 'A Unix timestamp indicating when the cache entry was created.',
  PRIMARY KEY (`aid`),
  KEY `expire` (`expire`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='A cache table for caching ID values of agency children'$$


delimiter $$

CREATE TABLE `category` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `CATEGORY_ABBREVIATION` varchar(10) DEFAULT NULL,
  `CATEGORY_NAME` varchar(200) DEFAULT NULL,
  `DATE_ENTERED` date NOT NULL DEFAULT '0000-00-00',
  `KEYWORDS` text NOT NULL,
  `IDENTIFIERS` text NOT NULL,
  `LAST_UPDATE` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `LAST_UPDATE_BY` varchar(50) NOT NULL DEFAULT '',
  `CATEGORY_DESCRIPTION` text NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `id` (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=25 DEFAULT CHARSET=latin1$$


delimiter $$

CREATE TABLE `countries` (
  `ID` int(9) unsigned NOT NULL AUTO_INCREMENT,
  `COUNTRY_NAME` char(50) NOT NULL DEFAULT '0',
  `DATE_ENTERED` date NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=195 DEFAULT CHARSET=latin1 ROW_FORMAT=FIXED$$


delimiter $$

CREATE TABLE `cris_main` (
  `CRIS_ID` int(11) NOT NULL AUTO_INCREMENT,
  `CRIS_Project_ID` varchar(255) DEFAULT NULL,
  `CRIS_AccessionNo` int(11) DEFAULT NULL,
  `CRIS_Title` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CRIS_ID`),
  KEY `Project ID` (`CRIS_Project_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=1540 DEFAULT CHARSET=latin1$$


delimiter $$

CREATE TABLE `farm_to_table_categories` (
  `cid` int(11) NOT NULL AUTO_INCREMENT COMMENT 'The primary identifier for a category',
  `name` varchar(50) NOT NULL COMMENT 'The human-readable name of the category',
  PRIMARY KEY (`cid`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COMMENT='Stores information about all defined Farm to Table categories'$$

delimiter $$

CREATE TABLE `institution_data` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `INSTITUTION_NAME` varchar(150) NOT NULL DEFAULT '0',
  `INSTITUTION_DEPARTMENT` varchar(150) DEFAULT NULL,
  `INSTITUTION_ADDRESS1` varchar(70) DEFAULT NULL,
  `INSTITUTION_ADDRESS2` varchar(70) DEFAULT NULL,
  `INSTITUTION_CITY` varchar(30) DEFAULT NULL,
  `INSTITUTION_COUNTRY` int(10) unsigned NOT NULL DEFAULT '0',
  `INSTITUTION_STATE` int(10) unsigned DEFAULT NULL,
  `INSTITUTION_ZIP` varchar(10) DEFAULT NULL,
  `DATE_ENTERED` date NOT NULL,
  `COMMENTS` text NOT NULL,
  `INSTITUTION_URL` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=1840 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `institution_index` (
  `pid` int(11) NOT NULL COMMENT 'The projects.ID of the linked project',
  `inst_id` int(11) NOT NULL COMMENT 'The institution_data.ID of the linked institution',
  KEY `pid` (`pid`,`inst_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1$$


delimiter $$

CREATE TABLE `investigator_data` (
  `ID` int(3) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '' COMMENT 'The name of the investigator',
  `EMAIL_ADDRESS` varchar(255) DEFAULT NULL,
  `PHONE_NUMBER` varchar(20) DEFAULT NULL,
  `INSTITUTION` int(4) DEFAULT NULL,
  `DATE_ENTERED` date NOT NULL,
  PRIMARY KEY (`ID`),
  FULLTEXT KEY `fulltext` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=8826 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `investigator_index` (
  `pid` int(11) NOT NULL DEFAULT '0' COMMENT 'The projects.ID of the linked project',
  `inv_id` int(11) NOT NULL DEFAULT '0' COMMENT 'The investigator_data.ID of the linked investigator.',
  KEY `pid` (`pid`),
  KEY `inv_id` (`inv_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `project` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `PROJECT_NUMBER` varchar(255) DEFAULT '',
  `PROJECT_TITLE` varchar(512) DEFAULT 'NULL',
  `source_url` varchar(512) NOT NULL DEFAULT '' COMMENT 'The URL of the webpage from which this project''s information was obtained.',
  `PROJECT_START_DATE` int(20) DEFAULT NULL,
  `PROJECT_END_DATE` int(20) DEFAULT NULL,
  `PROJECT_FUNDING` bigint(20) unsigned DEFAULT '0',
  `PROJECT_TYPE` int(11) unsigned DEFAULT '0',
  `PROJECT_KEYWORDS` text,
  `PROJECT_IDENTIFIERS` text,
  `PROJECT_COOPORATORS` text,
  `PROJECT_ABSTRACT` text,
  `PROJECT_PUBLICATIONS` text,
  `other_publications` text NOT NULL COMMENT 'Citations for non-journal publications.',
  `PROJECT_MORE_INFO` text,
  `PROJECT_OBJECTIVE` text,
  `PROJECT_ACCESSION_NUMBER` varchar(30) DEFAULT '',
  `ACTIVITY_STATUS` int(4) DEFAULT '1',
  `DATE_ENTERED` date DEFAULT NULL,
  `COMMENTS` text,
  `AUTO_INDEX_QA` varchar(2) NOT NULL DEFAULT '',
  `archive` tinyint(4) NOT NULL DEFAULT '0' COMMENT 'Boolean indicating whether the record is archived.',
  `LAST_UPDATE` datetime NOT NULL,
  `LAST_UPDATE_BY` varchar(50) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `project_date` (`PROJECT_START_DATE`,`PROJECT_END_DATE`),
  FULLTEXT KEY `project_title` (`PROJECT_TITLE`),
  FULLTEXT KEY `project_abstract` (`PROJECT_ABSTRACT`,`PROJECT_OBJECTIVE`,`PROJECT_MORE_INFO`),
  FULLTEXT KEY `project_number` (`PROJECT_NUMBER`),
  FULLTEXT KEY `project_keywords` (`PROJECT_KEYWORDS`,`PROJECT_IDENTIFIERS`),
  FULLTEXT KEY `fulltext` (`PROJECT_TITLE`,`PROJECT_KEYWORDS`,`PROJECT_IDENTIFIERS`,`PROJECT_ABSTRACT`,`PROJECT_OBJECTIVE`,`PROJECT_MORE_INFO`)
) ENGINE=MyISAM AUTO_INCREMENT=11897 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `project_backup` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `PROJECT_NUMBER` varchar(255) DEFAULT '',
  `PROJECT_TITLE` varchar(512) DEFAULT 'NULL',
  `source_url` varchar(512) NOT NULL DEFAULT '' COMMENT 'The URL of the webpage from which this project''s information was obtained.',
  `PROJECT_START_DATE` int(20) DEFAULT NULL,
  `PROJECT_END_DATE` int(20) DEFAULT NULL,
  `PROJECT_FUNDING` bigint(20) unsigned DEFAULT '0',
  `PROJECT_TYPE` int(11) unsigned DEFAULT '0',
  `PROJECT_KEYWORDS` text,
  `PROJECT_IDENTIFIERS` text,
  `PROJECT_COOPORATORS` text,
  `PROJECT_ABSTRACT` text,
  `PROJECT_PUBLICATIONS` text,
  `other_publications` text NOT NULL COMMENT 'Citations for non-journal publications.',
  `PROJECT_MORE_INFO` text,
  `PROJECT_OBJECTIVE` text,
  `PROJECT_ACCESSION_NUMBER` varchar(30) DEFAULT '',
  `ACTIVITY_STATUS` int(4) DEFAULT '1',
  `DATE_ENTERED` date DEFAULT NULL,
  `COMMENTS` text,
  `AUTO_INDEX_QA` varchar(2) NOT NULL DEFAULT '',
  `archive` tinyint(4) NOT NULL DEFAULT '0' COMMENT 'Boolean indicating whether the record is archived.',
  `LAST_UPDATE` datetime NOT NULL,
  `LAST_UPDATE_BY` varchar(50) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `project_date` (`PROJECT_START_DATE`,`PROJECT_END_DATE`),
  FULLTEXT KEY `project_title` (`PROJECT_TITLE`),
  FULLTEXT KEY `project_abstract` (`PROJECT_ABSTRACT`,`PROJECT_OBJECTIVE`,`PROJECT_MORE_INFO`),
  FULLTEXT KEY `project_number` (`PROJECT_NUMBER`),
  FULLTEXT KEY `project_keywords` (`PROJECT_KEYWORDS`,`PROJECT_IDENTIFIERS`),
  FULLTEXT KEY `fulltext` (`PROJECT_TITLE`,`PROJECT_KEYWORDS`,`PROJECT_IDENTIFIERS`,`PROJECT_ABSTRACT`,`PROJECT_OBJECTIVE`,`PROJECT_MORE_INFO`)
) ENGINE=MyISAM AUTO_INCREMENT=10878 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `project_category` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL DEFAULT '0',
  `category_id` int(11) NOT NULL DEFAULT '0',
  `DATE_ENTERED` date NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=25337 DEFAULT CHARSET=latin1 ROW_FORMAT=FIXED COMMENT='Lists project/category relationships'$$


delimiter $$

CREATE TABLE `project_counts` (
  `AGENCY_ID` int(11) NOT NULL DEFAULT '0',
  `PROJECT_COUNT` int(11) NOT NULL DEFAULT '0',
  `PROJECT_YEAR` int(11) NOT NULL DEFAULT '0',
  `AGENCY_ACRONYM` varchar(10) NOT NULL DEFAULT '',
  `PARENT_AGENCY` int(11) NOT NULL DEFAULT '0',
  `SUPER_AGENCY` int(11) NOT NULL DEFAULT '0',
  `AGENCY_ISSUPER` int(11) NOT NULL DEFAULT '0',
  `AGENCY_ISPARENT` int(11) NOT NULL DEFAULT '0',
  `DATE_ENTERED` date NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `project_farm_to_table` (
  `pid` int(11) NOT NULL COMMENT 'The project.ID this record belongs to',
  `cid` int(11) NOT NULL COMMENT 'The farm_to_table_categories.cid of categories that have been added to this project',
  PRIMARY KEY (`pid`,`cid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Data storage for the Farm to Table field'$$


delimiter $$

CREATE TABLE `project_farm_to_table_na` (
  `pid` int(11) NOT NULL COMMENT 'The projects.pid of a project with no F2T categories',
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Projects that do not have F2T categories'$$


delimiter $$

CREATE TABLE `project_reports` (
  `pid` int(11) NOT NULL COMMENT 'The projects.pid of the report''s project',
  `title` varchar(60) NOT NULL DEFAULT '' COMMENT 'The inner text of the report link',
  `url` varchar(255) NOT NULL COMMENT 'The href attribute of the report link',
  `final_report` tinyint(1) NOT NULL DEFAULT '0' COMMENT '1 if the report is a final report.  0 for any other kind of report.',
  `created` int(11) NOT NULL DEFAULT '0' COMMENT 'The Unix timestamp when the link was created',
  KEY `pid` (`pid`,`created`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1$$


delimiter $$

CREATE TABLE `project_titles` (
  `pid` int(10) NOT NULL,
  `title` varchar(255) NOT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='A temporary table for de-duping records imported from CRIS.'$$


delimiter $$

CREATE TABLE `projecttype` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) DEFAULT NULL,
  `DATE_ENTERED` date NOT NULL,
  `COMMENTS` text NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=66 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `publication_data` (
  `pub_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'The primary identifier for a publication',
  `title` varchar(512) CHARACTER SET latin1 NOT NULL COMMENT 'The title of the publication',
  `journal` varchar(255) CHARACTER SET latin1 NOT NULL COMMENT 'The name of the journal which accepted the publication',
  `authors` longtext CHARACTER SET latin1 NOT NULL COMMENT 'The authors of the publication',
  `url` varchar(255) CHARACTER SET latin1 NOT NULL DEFAULT '' COMMENT 'The URL to an online copy of the published publication',
  `naldc_url` varchar(255) NOT NULL DEFAULT '' COMMENT 'The URL of the publication''s full text in the NAL Digital Collections.',
  `publication_year` int(4) NOT NULL COMMENT 'Part of the citation - the journal issue''s year of printing',
  `publication_month` int(2) NOT NULL COMMENT 'Part of the citation - the journal issue''s month of printing',
  `publication_day` int(2) NOT NULL COMMENT 'Part of the citation - the journal issue''s day of printing',
  `volume` varchar(7) NOT NULL COMMENT 'Part of the citation - the journal issue''s volume number',
  `issue` varchar(10) NOT NULL COMMENT 'Part of the citation - the journal issue number',
  `pages` varchar(15) CHARACTER SET latin1 NOT NULL COMMENT 'Part of the citation - the page numbers of the article in the journal issue',
  `created` int(11) NOT NULL COMMENT 'The unix timestamp of when the record was created',
  `changed` int(11) NOT NULL COMMENT 'The UNIX timestamp when the record was last updated.',
  PRIMARY KEY (`pub_id`),
  FULLTEXT KEY `publication_data` (`title`,`authors`)
) ENGINE=MyISAM AUTO_INCREMENT=1121 DEFAULT CHARSET=utf8 COMMENT='A list of food safety USDA ARS publications'$$


delimiter $$

CREATE TABLE `publication_index` (
  `pid` int(11) NOT NULL COMMENT 'The project.pid of the linked project',
  `pub_id` int(11) NOT NULL COMMENT 'The publication_data.pub_id of the linked publication',
  KEY `pid` (`pid`),
  KEY `pub_id` (`pub_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Lists project/publication relationships'$$


delimiter $$

CREATE TABLE `reports` (
  `ID` int(3) unsigned NOT NULL AUTO_INCREMENT,
  `PROJECT_ID` int(3) NOT NULL DEFAULT '0',
  `REPORT_YEAR` int(4) DEFAULT NULL,
  `REPORT_LINK` varchar(255) DEFAULT NULL,
  `ANNUAL_FUNDING` int(10) NOT NULL DEFAULT '0',
  `DATE_ENTERED` date NOT NULL,
  `COMMENTS` text NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=9754 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `states` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `abbrv` varchar(6) DEFAULT NULL,
  `DATE_ENTERED` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=60 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC$$


delimiter $$

CREATE TABLE `status` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `TEXT` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC$$

