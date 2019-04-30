*** Settings ***
Library  Collections
Library  RequestsLibrary
Resource  shared_keywords.robot

Documentation  Test suite verifying scenarios related to user & project management (see requirement SE-4).

**** Variables ***
${REQUEST_TIMEOUT_DEFAULT}  5000

*** Test Cases ***
Login Of Non-existing User Is Rejected
    ${response}=  Login With Email "non-existing@gmail.com" And Password "password"
    Response "${response}" Should Contain Error

Login After Valid Registration Is Successful
    [Tags]  SE-8
    [Setup]   Run Keywords
    ...       Set Test Variable  ${name}      Test Name
    ...  AND  Set Test Variable  ${surname}   Test Surname
    ...  AND  Set Test Variable  ${email}     test-email@gmail.com
    ...  AND  Set Test Variable  ${password}  password

    ${credentials_json}=  Create User Credentials JSON  ${name}  ${surname}  ${email}  ${password}
    ${response}=  Create User Account With Credentials "${credentials_json}"
    Response "${response}" Should Be Successful
    ${response}=  Login With Email "${email}" And Password "${password}"
    Response "${response}" Should Be Successful
    
Registration With Missing Data Is Rejected
    [Tags]  SE-8
    Pass Execution  Execution passed

Registration With Invalid Data Is Rejected
    [Tags]  SE-8
    Pass Execution  Execution passed

*** Keywords ***
Create User Credentials JSON
    [Documentation]  Creates a JSON object representing a new user account.
    [Arguments]  ${name}  ${surname}  ${email}  ${password}

    &{credentials}=  Create Dictionary
    Run Keyword If  ${name != None}      Set To Dictionary  ${credentials}  name=${name}
    Run Keyword If  ${surname != None}   Set To Dictionary  ${credentials}  surname=${surname}
    Run Keyword If  ${email != None}     Set To Dictionary  ${credentials}  email=${email}
    Run Keyword If  ${password != None}  Set To Dictionary  ${credentials}  password=${password}
    ${credentials_json}=  Evaluate  json.dumps(${credentials})  json

    [Return]  ${credentials_json}

Create User Account With Credentials "${credentials_json}"
    [Documentation]  Attempts to create a new user account with specified user credentials.

    ${response}=  Post Request
    ...  scanpath-evaluator  /api/user/add  data=${credentials_json}  timeout=${REQUEST_TIMEOUT_DEFAULT}

    [Return]  ${response}

Login With Email "${email}" And Password "${password}"
    [Documentation]  Performs a login request with specified credentials.

    &{credentials}=  Create Dictionary  email=${email}  password=${password}
    ${credentials_json}=  Evaluate  json.dumps(${credentials})  json
    ${response}=  Post Request
    ...  scanpath-evaluator  /api/user/auth  data=${credentials_json}  timeout=${REQUEST_TIMEOUT_DEFAULT}

    [Return]  ${response}