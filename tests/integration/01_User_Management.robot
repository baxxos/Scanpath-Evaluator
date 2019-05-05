*** Settings ***
Library  Collections
Library  RequestsLibrary
Resource  shared_keywords.robot

Documentation  Test suite verifying scenarios related to user & project management (see goal SE-4).

**** Variables ***
${REQUEST_TIMEOUT_DEFAULT}  5000

*** Test Cases ***
Login Of Non-existing User Is Rejected
    [Tags]  SE-8  SE-27
    
    When Log In With Email "test@email.com" And Password "password"
    Then Response Is Not Successful
    and Response Contains Error Message "Invalid user credentials - try again."

Deletion Of Non-existing User Is Rejected
    [Tags]  SE-8  SE-27

    When Delete User Account With Email "test@email.com" And Password "password"
    Then Response Is Not Successful
    and Response Contains Error Message "Invalid user credentials - try again."

Login After Valid Registration Is Successful
    [Tags]   SE-8  SE-27
    [Setup]  Set Test Variable  &{credentials}
    ...      name=Test Name  surname=Test Surname  email=test@email.com  password=password
    
    Given User Account With Credentials "${credentials}" Is Created
    and Response Is Successful
    When Log In With Email "${credentials['email']}" And Password "${credentials['password']}"
    Then Response Is Successful
    
    [Teardown]  Run Keywords
    ...  Delete User Account With Email "${credentials['email']}" And Password "${credentials['password']}"

Registration With Missing Data Is Rejected
    [Tags]  SE-8  SE-26  SE-27
    [Setup]  Set Test Variable  &{credentials}
    ...      name=Test Name  surname=Test Surname  email=test@email.com
    
    When User Account With Credentials "${credentials}" Is Created
    Then Response Is Not Successful
    and Response Contains Error Message "Required user attributes are missing"

Registration With Empty Data Is Rejected
    [Tags]  SE-8  SE-26  SE-27
    [Setup]  Set Test Variable  &{credentials}
    ...      name=${NONE}  surname=${NONE}  email=${NONE}  password=${NONE}
    
    When User Account With Credentials "${credentials}" Is Created
    Then Response Is Not Successful
    and Response Contains Error Message "Required user attributes are empty"

Registration With Invalid Data Is Rejected
    [Tags]  SE-8  SE-26  SE-27
    [Setup]  Set Test Variable  &{credentials}
    ...      name=Test Name  surname=Test Surname  email=test-email.com  password=password
    
    When User Account With Credentials "${credentials}" Is Created
    Then Response Is Not Successful
    and Response Contains Error Message "Malformed input data - please, try again."

Duplicate Registration Is Rejected
    [Tags]  SE-8  SE-27
    [Setup]   Set Test Variable  &{credentials}
    ...  name=Test Name  surname=Test Surname  email=test@email.com  password=password

    Given User Account With Credentials "${credentials}" Is Created
    and Response Is Successful
    When User Account With Credentials "${credentials}" Is Created
    Then Response Is Not Successful
    and Response Contains Error Message "Integrity error: e-mail address is already taken."

    [Teardown]  Run Keywords
    ...  Delete User Account With Email "${credentials['email']}" And Password "${credentials['password']}"

*** Keywords ***
User Account With Credentials "${credentials}" Is Created
    [Documentation]  Attempts to create a new user account with specified user credentials and sets the response as
    ...  a test variable.

    ${credentials_json}=  Evaluate  json.dumps(${credentials})  modules=json
    ${response}=  Post Request
    ...  scanpath-evaluator  /api/user/add  data=${credentials_json}  timeout=${REQUEST_TIMEOUT_DEFAULT}
    
    Set Test Variable  ${TEST_RESPONSE}  ${response}

Delete User Account With Email "${email}" And Password "${password}"
    [Documentation]  Attempts to delete a user account based on the specified credentials and sets the response as
    ...  a test variable.

    &{credentials}=  Create Dictionary  email=${email}  password=${password}
    ${credentials_json}=  Evaluate  json.dumps(${credentials})  modules=json
    ${response}=  Delete Request
    ...  scanpath-evaluator  /api/user/delete  data=${credentials_json}  timeout=${REQUEST_TIMEOUT_DEFAULT}
    
    Set Test Variable  ${TEST_RESPONSE}  ${response}

Log In With Email "${email}" And Password "${password}"
    [Documentation]  Performs a login request with specified credentials and sets the response as a test variable.

    &{credentials}=  Create Dictionary  email=${email}  password=${password}
    ${credentials_json}=  Evaluate  json.dumps(${credentials})  json
    ${response}=  Post Request
    ...  scanpath-evaluator  /api/user/auth  data=${credentials_json}  timeout=${REQUEST_TIMEOUT_DEFAULT}
    
    Set Test Variable  ${TEST_RESPONSE}  ${response}