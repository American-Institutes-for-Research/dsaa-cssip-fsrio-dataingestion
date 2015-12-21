
"""

This is a draft of dumping new NSF data into temp FSRIO database

"""

# load required packages
import os
import glob
import xml.etree.ElementTree as elementTree # introduced to parse XML files


import MySQLdb as mdb
from datetime import datetime

# setting up the connection to DB
connection = mdb.connect(user="",
                           passwd="",
                           db="",
                           host="")

connection.autocommit(True)

cursor = connection.cursor()

# will change path later
# NSF data to be uploaded

NSFfiles = glob.glob(os.path.join('U:\\FSRIO\\code\\NSF data Importer\\nsf_sample', "*.xml"))


# loop over all the NSF XML files

for file in NSFfiles:

    # parse raw XML data first
    tree = elementTree.parse(file)

    rootTagElement = tree.getroot()

    # Elements for project table

    awardElement = rootTagElement.find("Award")

    if awardElement is not None:
        AwardID = awardElement.find("AwardID")
        AwardTitle = awardElement.find("AwardTitle")
        AwardAmount = awardElement.find("AwardAmount")
        AbstractNarration = awardElement.find("AbstractNarration")
        StartDate = awardElement.find("AwardEffectiveDate")
        AwardStartDate = int(StartDate.text[6:]) if StartDate is not None else None
        EndDate = awardElement.find("AwardExpirationDate")
        AwardEndDate = int(EndDate.text[6:]) if EndDate is not None else None
        AwardInstrument = awardElement.find("AwardInstrument").find("Value")

    else:
        AwardID = None
        AwardTitle = None
        AwardAmount = None
        AbstractNarration = None
        AwardStartDate = None
        AwardEndDate = None
        AwardInstrument = None

    # compare with the current system time, determining if the project expired or not
    # Only two types now
    now = datetime.now()

    deadline = datetime.strptime(EndDate.text,"%m/%d/%Y")

    if deadline >= now:
        if 'Continuing' in AwardInstrument.text:
            ProjectStatus = 5
        else:
            ProjectStatus = 1
    else:
        ProjectStatus = 4

    ######

    # Elements for institution_data table
    institutionElement = awardElement.find("Institution")
    if institutionElement is not None:
        InstitutionName = institutionElement.find("Name")
        InstitutionCity = institutionElement.find("CityName")
    else:
        InstitutionName = None
        InstitutionCity = None

    # Elements for investigator_data table
    investigatorElement = awardElement.find("Investigator")

    if investigatorElement is not None:
        FirstName = investigatorElement.find("FirstName")
        LastName = investigatorElement.find("LastName")
        Email = investigatorElement.find("EmailAddress")
    else:
        FirstName = None
        LastName = None
        Email = None

    if LastName is not None and FirstName is not None:
        Name = LastName.text + ", " + FirstName.text
    else:
        Name = None

    # Elements for states table
    if institutionElement is not None:
        StateName = institutionElement.find("StateName")
        StateCode = institutionElement.find("StateCode")
    else:
        StateName = None
        StateCode = None

    # Element for countries table
    if institutionElement is not None:
        CountryName = institutionElement.find("CountryName")
    else:
        CountryName = None

    # Save all the relevant data into dict first
    data = {
        "AwardID": AwardID.text if AwardID is not None else None,
        "AwardTitle": AwardTitle.text if AwardTitle is not None else None,
        "Abstract": AbstractNarration.text if AbstractNarration is not None else None,
        "AwardStartDate": AwardStartDate if AwardStartDate is not None else None,
        "AwardEndDate":  AwardEndDate if AwardEndDate is not None else None,
        "AwardAmount": int(AwardAmount.text) if AwardAmount is not None else None,
        "Name": Name if Name is not None else 'NA',
        "Email": Email.text if Email is not None else None,
        "InstitutionName": InstitutionName.text if InstitutionName is not None else '0',
        "InstitutionCity": InstitutionCity.text if InstitutionCity is not None else None,
        "StateName": StateName.text if StateName is not None else None,
        "StateCode": StateCode.text if StateCode is not None else None,
        "CountryName": CountryName.text if CountryName is not None else '0',
        "ProjectStatus": ProjectStatus,
        "SourceURL": "http://www.nsf.gov/awardsearch/showAward?AWD_ID="+AwardID.text+"&HistoricalAwards=false"
    }

    # cannot simply run sql files any more, need a series of manipulation

    # drafting MySQL commands that dump the raw project info one by one into corresponding table
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
            LAST_UPDATE_BY,
            source_url
        ) values (
            %(AwardID)s,
            %(AwardTitle)s,
            %(AwardAmount)s,
            %(AwardStartDate)s,
            %(AwardEndDate)s,
            %(Abstract)s,
            999,
            '',
            %(ProjectStatus)s,
            '2015-11-26',
            '',
            %(SourceURL)s
        );
        '''
    cursor.execute(InsertProjectSQL, data)


    # 2. acquire project ID for the crosswalk table `institution_index`
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
    data['PID'] = PID
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

    GetInstIDsql = '''
    SELECT
        ID
    FROM
        institution_data
    WHERE
        INSTITUTION_NAME = '{}'
    '''.format(data['InstitutionName'])

    cursor.execute(GetInstIDsql)

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
        '''.format(data['StateCode'])

        cursor.execute(GetStateCodeSQL)

        try:
            StateID = cursor.fetchone()[0]
        except TypeError:
            # if no valid state code, assign 0
            #StateID = 0
            InsertStateSQL = '''
            INSERT INTO states
            (
                name,
                abbrv,
                DATE_ENTERED
            ) VALUES (
                %(StateName)s,
                %(StateCode)s,
                '2015-11-26'
            );
            '''

            cursor.execute(InsertStateSQL,data)

            # obtaining Country ID again
            cursor.execute(GetStateCodeSQL)
            StateID = cursor.fetchone()[0]

        # getting country code
        GetCountryIDSQL = '''
        SELECT
            ID, COUNTRY_NAME
        FROM
            countries
        WHERE
            COUNTRY_NAME = '{}';
        '''.format(data['CountryName'])

        cursor.execute(GetCountryIDSQL)

        try:
            CountryID = cursor.fetchone()[0]
        except TypeError:
            # if unknown country name, add a new record in table `countries`
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

            cursor.execute(InsertCountrySQL,data)

            # obtaining Country ID again
            cursor.execute(GetCountryIDSQL)
            CountryID = cursor.fetchone()[0]

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
        ) values (
            %(InstitutionCity)s,
            NULL,
            %(InstitutionName)s,
            %(CountryID)s,
            %(StateID)s,
            NULL,
            NULL,
            NULL,
            '2015-11-26',
            '',
            ''
        )
        '''

        cursor.execute(InsertInstSQL, data)

        #
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
        inst_id = {}
    WHERE
        inst_id = -1
    ;
    '''.format(InstID)

    cursor.execute(UpdateInstIndexSQL)

    # 6. update the agency_index table
    UpdateAgencyIndexSQL = '''
    INSERT INTO agency_index
    (
        pid,
        aid
    )   VALUES (
        {},
        6
    )
    ;
    '''.format(PID)

    cursor.execute(UpdateAgencyIndexSQL)

    # 7. check project types
    # specifically treat 'standard grant' and 'continuing grant' as the same

    if "grant" in AwardInstrument.text.lower():
        ProjectTypeID = 3
    else:
        # try checking if project type is known
        GetProjectTypeIDSQL = '''
        SELECT
            ID
        FROM
            projecttype
        WHERE
            `NAME` like '{}'
        '''.format(AwardInstrument.text)

        cursor.execute(GetProjectTypeIDSQL)
        try:
            ProjectTypeID = cursor.fetchone()[0]
        # if not found, insert a new line in project type lookup table
        except TypeError:
            InsertProjectTypeSQL = '''
            INSERT INTO projecttype
            (
                NAME,
                DATE_ENTERED,
                COMMENTS
            )   VALUES  (
                '{}',
                '2015-11-26',
                ''
            );
            '''.format(AwardInstrument.text)
            #  Thanksgiving date! In order to distinguish the newly added types from the existing ones

            cursor.execute(InsertProjectTypeSQL)

            GetNewProjectTypeIDSQL = '''
            SELECT
                ID
            FROM
                projecttype
            ORDER BY
                ID DESC
            LIMIT 1;
            '''

            cursor.execute(GetNewProjectTypeIDSQL)
            ProjectTypeID = cursor.fetchone()[0]

    data['ProjectType'] = ProjectTypeID

    # 8. update project table

    UpdateProjectTypeSQL = '''
    UPDATE
        project
    SET
        PROJECT_TYPE = {}
    WHERE
        PROJECT_TYPE = 999
    '''.format(data['ProjectType'])

    cursor.execute(UpdateProjectTypeSQL)

    # 9. start to deal with investigator info
    # look at email info first
    if data['Email'] is not None:
        GetInvestigatorSQL = '''
        SELECT
            ID
        FROM
            investigator_data
        WHERE
            EMAIL_ADDRESS LIKE '{}';
        '''.format(data['Email'])

        cursor.execute(GetInvestigatorSQL)
        # see if we can match by email address
        try:
            InvestigatorID = cursor.fetchone()[0]
        # if not insert new record
        except TypeError:
            InsertInvestigatorSQL = '''
            INSERT INTO investigator_data
            (
                name,
                EMAIL_ADDRESS,
                INSTITUTION,
                DATE_ENTERED
            )   VALUES  (
                %(Name)s,
                %(Email)s,
                %(InstID)s,
                '2015-11-26'
             )
             ;
             '''

            cursor.execute(InsertInvestigatorSQL, data)
            # get the newly added inv_id
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

    # if no email, use investigator's name
    elif data['Name'] is not None:
        GetInvestigatorSQL = '''
        SELECT
            ID
        FROM
            investigator_data
        WHERE
            name LIKE '{}'
        ORDER BY
            DATE_ENTERED DESC
        LIMIT 1;
         '''.format(data['Name'])

        cursor.execute(GetInvestigatorSQL)

        try:
            InvestigatorID = cursor.fetchone()[0]
        # if not found
        except TypeError:
            # insert new record for investigator data
            InsertInvestigatorSQL = '''
            INSERT INTO investigator_data
            (
                name,
                EMAIL_ADDRESS,
                INSTITUTION,
                DATE_ENTERED
            )   VALUES  (
                %(Name)s,
                %(Email)s,
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
        InvestigatorID = 0

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

