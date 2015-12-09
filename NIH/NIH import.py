__author__ = 'jzhou'


import os
import glob
import xml.etree.ElementTree as ET

import MySQLdb as mdb
from datetime import datetime

connection = mdb.connect(user="jzhou",
                           passwd="t1wWYX5ZnJ*E^Gz&",
                           db="fsriotemp",
                           host="wsumsftp01")

# def run_sql_file(filename, data_to_upload, db_connection):
#     """
#     The function takes a filename and a connection as input
#     and will run the SQL query on the given connection
#     """
#
#     sqlfile = open(filename, 'r')
#     sqlcommand = s = " ".join(file.readlines())
#
#     cursor = db_connection.cursor()
#     cursor.execute(sqlcommand,data_to_upload)
#     db_connection.commit()

connection.autocommit(True)

cursor = connection.cursor()

# will change path later
NIHfiles = glob.glob(os.path.join('U:\\FSRIO\\Code\\NIH data Importer\\sample NIH XML data', '*.xml'))

NIHabstracts = glob.glob(os.path.join('U:\\FSRIO\Code\\NIH data Importer\\sample NIH abstracts data', '*.xml'))

# Create a dictionary for abstracts

DictAbstracts = {}

for file in NIHabstracts:

    tree = ET.parse(file)

    root = tree.getroot()

    num_abstracts = len(root)

    for i in range(num_abstracts):

        ApplicationID = root[i].find('APPLICATION_ID')

        Abstract = root[i].find('ABSTRACT_TEXT')

        DictAbstracts[ApplicationID.text] = Abstract.text # have not applied any modifications to the original strings


for file in NIHfiles:

    tree = ET.parse(file)

    root = tree.getroot()

    num_projects = len(root)

    for i in range(num_projects):

        data = {}

        AgencyFullName = root[i].find('IC_NAME')

        ApplicationID = root[i].find('APPLICATION_ID')

        CountryName = root[i].find('ORG_COUNTRY')

        InstitutionCity = root[i].find('ORG_CITY')
        InstitutionDepartment = root[i].find('ORG_DEPT')
        InstitutionName = root[i].find('ORG_NAME')
        InstitutionZip = root[i].find('ORG_ZIPCODE')

        Name = root[i].find('PIS')

        Name = Name.find('PI').find('PI_NAME') if Name is not None else None

        ProjectNumber = root[i].find('FULL_PROJECT_NUM')
        ProjectStartDate = root[i].find('PROJECT_START')
        ProjectEndDate = root[i].find('PROJECT_END')
        ProjectTitle = root[i].find('PROJECT_TITLE')
        ProjectFunding = root[i].find('TOTAL_COST')

        States = root[i].find('ORG_STATE')

        if ApplicationID is not None:
            ApplicationID = ApplicationID.text
            try:
                Abstract = DictAbstracts[ApplicationID]
            except KeyError:
                Abstract = None
        else:
            ApplicationID = None
            Abstract = None

        data = {
            "AgencyFullName": AgencyFullName.text if AgencyFullName is not None else None,
            "CountryName": CountryName.text if CountryName is not None else None,
            "InstitutionCity": InstitutionCity.text if InstitutionCity is not None else None,
            "InstitutionDepartment": InstitutionDepartment.text if InstitutionDepartment is not None else None,
            "InstitutionName": InstitutionName.text if InstitutionName is not None else None,
            "InstitutionZip": InstitutionZip.text if InstitutionZip is not None else None,
            "Name": Name.text if Name is not None else None,
            "ProjectType": 3,   # all 'grant'
            "ProjectNumber": ProjectNumber.text if ProjectNumber is not None else None,
            "ProjectStartDate": int(ProjectStartDate.text[6:]) if ProjectStartDate is not None and
                                              ProjectStartDate.text is not None else None,
            "ProjectEndDate": int(ProjectEndDate.text[6:]) if ProjectEndDate is not None and
                                            ProjectEndDate.text is not None else None,
            "ProjectTitle": ProjectTitle.text if ProjectTitle is not None else None,
            "ProjectFunding": int(
                ProjectFunding.text) if ProjectFunding is not None and ProjectFunding.text is not None else None,
            "States": States.text if States is not None else None,
            "ApplicationID": ApplicationID,
            "Abstract": Abstract
        }

        # compare with the current system time, determining if the project expired or not
        # Only two types now
        now = datetime.now()

        if ProjectEndDate.text is not None:
            deadline = datetime.strptime(ProjectEndDate.text,"%m/%d/%Y")
            if deadline >= now:
                ProjectStatus = 1   # active
            else:
                ProjectStatus = 4   # expired
        else:
            ProjectStatus = 0   # 0 represents unknown status

        data['ProjectStatus'] = ProjectStatus

        # 1. load project data
        InsertProjectSQL = '''
        INSERT INTO project
        (
            PROJECT_NUMBER,
            PROJECT_TITLE,
            PROJECT_FUNDING,
            PROJECT_START_DATE,
            PROJECT_END_DATE,
            PROJECT_ABSTRACT,
            PROJECT_TYPE,
            other_publications,
            ACTIVITY_STATUS,
            LAST_UPDATE,
            LAST_UPDATE_BY
        ) values (
            %(ProjectNumber)s,
            %(ProjectTitle)s,
            %(ProjectFunding)s,
            %(ProjectStartDate)s,
            %(ProjectEndDate)s,
            %(Abstract)s,
            %(ProjectType)s,
            '',
            %(ProjectStatus)s,
            '2015-11-26',
            ''
        );
        '''
        # project type all to be 'grant'
        cursor.execute(InsertProjectSQL, data)

        # 2. acquire project ID for the crosswalk table `institution_index`
        # always the last one
        GetPIDSQL = '''
        SELECT
            ID
        FROM
            project
        ORDER BY
            ID DESC
        LIMIT 1
        ;
        '''
        cursor.execute(GetPIDSQL)

        # PID should not be empty
        PID = cursor.fetchone()[0]

        # 3. fill PID in the crosswalk table `institution_index`
        #    temporarily assign -1 to `inst_id`, indicating requiring further work on it
        PIDtoInstIndex = '''
        INSERT INTO institution_index
        (
            pid,
            inst_id
        ) VALUES (
            {},
            -1
        )
        '''.format(PID)

        cursor.execute(PIDtoInstIndex)

        # 4. Looking for corresponding institution ID in the lookup table `institution_data`

        GetInstIDSQL = '''
        SELECT
            ID
        FROM
            institution_data
        WHERE
            INSTITUTION_NAME LIKE %(InstitutionName)s
        '''

        cursor.execute(GetInstIDSQL, data)

        # if ID found
        try:
            InstID = cursor.fetchone()[0]

        # if no ID found, insert a new record in lookup table `institution_data`
        except TypeError:

            # there are two numeric columns storing state and country codes.
            # check state and country code for the institution

            # getting state code
            GetStateCodeSQL = '''
            SELECT
                id, abbrv
            FROM
                states
            WHERE
                abbrv = '{}'
            '''.format(data['States'])

            cursor.execute(GetStateCodeSQL)

            try:
                StateID = cursor.fetchone()[0]
            except TypeError:
                # if no valid state code, assign 0
                StateID = 0

            # getting country code
            GetCountryIDSQL = '''
            SELECT
                ID, COUNTRY_NAME
            FROM
                countries
            WHERE
                COUNTRY_NAME LIKE '{}';
            '''.format(data['CountryName'])

            cursor.execute(GetCountryIDSQL)

            try:
                CountryID = cursor.fetchone()[0]
            except TypeError:
                # if unknown country name, add a new record in table `countries`
                if data['CountryName'] is not None:
                    InsertCountrySQL = '''
                    INSERT INTO countries
                    (
                        COUNTRY_NAME,
                        DATE_ENTERED
                    ) VALUES (
                        %(CountryName)s,
                        '2015-11-26'
                    );
                    '''

                    cursor.execute(InsertCountrySQL, data)

                    # obtaining Country ID again
                    cursor.execute(GetCountryIDSQL)
                    CountryID = cursor.fetchone()[0]
                else:
                    CountryID = 0 # representing unknown

            data["StateID"] = StateID
            data["CountryID"] = CountryID

            # time to add a new row in institution lookup table
            InsertInstSQL = '''
            INSERT INTO institution_data
            (
                INSTITUTION_CITY,
                INSTITUTION_DEPARTMENT,
                INSTITUTION_NAME,
                INSTITUTION_COUNTRY,
                INSTITUTION_STATE,
                INSTITUTION_ZIP,
                INSTITUTION_ADDRESS1,
                INSTITUTION_ADDRESS2,
                DATE_ENTERED,
                COMMENTS,
                INSTITUTION_URL
            ) VALUES (
                %(InstitutionCity)s,
                %(InstitutionDepartment)s,
                %(InstitutionName)s,
                %(CountryID)s,
                %(StateID)s,
                %(InstitutionZip)s,
                NULL,
                NULL,
                '2015-11-26',
                '',
                ''
            )
            '''

            cursor.execute(InsertInstSQL, data)

            GetInstIDSQL = '''
            SELECT
                ID
            FROM
                institution_data
            ORDER BY
                ID DESC
            ;
            '''

            cursor.execute(GetInstIDSQL)

            InstID = cursor.fetchone()[0]

        data['InstID'] = InstID

        # 5. update the crosswalk `institution_index`, replacing -1
        UpdateInstIndexSQL = '''
        UPDATE
            institution_index
        SET
            inst_id = %(InstID)s
        WHERE
            inst_id = -1
        ;
        '''

        cursor.execute(UpdateInstIndexSQL, data)

        # 6. get the agency_index table
        GetAgencyIDSQL = '''
        SELECT
            ID
        FROM
            agency_data
        WHERE
            AGENCY_FULL_NAME LIKE '{}'
        ;
        '''.format(data['AgencyFullName'])

        cursor.execute(GetAgencyIDSQL)

        try:
            AID = cursor.fetchone()[0]
        except TypeError:
            InsertAgencyDataSQL = '''
            INSERT INTO agency_data
            (
                AGENCY_FULL_NAME,
                US_GOVT,
                DATE_ENTERED,
                AGENCY_URL
            )   VALUES  (
                %(AgencyFullName)s,
                1,
                '2015-11-26',
                ''
            )
            ;
            '''
            # not sure if we can say all the agencies in NIH data are US govt, temporarily assign 99
            cursor.execute(InsertAgencyDataSQL, data)

            cursor.execute(GetAgencyIDSQL, data)

            AID = cursor.fetchone()[0]

            InsertAgencyHierSQL = '''
            INSERT INTO agency_hierarchy
            (
                aid,
                parent
            )   VALUES  (
                {},
                -1
            );
            '''.format(AID) # assigning parent as -1, indicating requirement of manual check

            cursor.execute(InsertAgencyHierSQL)

        data['PID'] = PID
        data['AID'] = AID

        # INSERT INTO agency crosswalk table

        InsertAgencyInsexSQL = '''
        INSERT INTO agency_index
        (
            pid,
            aid
        )   VALUES  (
            %(PID)s,
            %(AID)s
        );
        '''

        cursor.execute(InsertAgencyInsexSQL, data)

        # 7. start to deal with investigator info
        # use investigator's name
        if data['Name'] is not None:
            GetInvestigatorSQL = '''
            SELECT
                ID
            FROM
                investigator_data
            WHERE
                name LIKE %(Name)s
            ORDER BY
                DATE_ENTERED DESC
            LIMIT 1;
             '''

            cursor.execute(GetInvestigatorSQL, data)

            try:
                InvestigatorID = cursor.fetchone()[0]
            # if not found
            except TypeError:
                # insert new record for investigator data
                InsertInvestigatorSQL = '''
                INSERT INTO investigator_data
                (
                    name,
                    INSTITUTION,
                    DATE_ENTERED
                )   VALUES  (
                    %(Name)s,
                    %(InstID)s,
                    '2015-11-26'
                )
                ;
                 '''

                cursor.execute(InsertInvestigatorSQL, data)
                # acquire inv_id
                GetInvestigatorSQL = '''
                SELECT
                    ID
                FROM
                    investigator_data
                ORDER BY
                    ID DESC
                ;
                '''
                cursor.execute(GetInvestigatorSQL)
                InvestigatorID = cursor.fetchone()[0]
        # no email, and no name
        else:
            InvestigatorID = 0 # indicating no investigator info

        data['InvestigatorID'] = InvestigatorID

        # 10. insert new line into investigator_index
        InsertInvestigatorIndexSQL = '''
        INSERT INTO investigator_index
        (
            pid,
            inv_id
        )   VALUES (
            %(PID)s,
            %(InvestigatorID)s
        )
        '''

        cursor.execute(InsertInvestigatorIndexSQL, data)

connection.close()