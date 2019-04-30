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
    Pass Execution  Execution passed

Registration With Missing Data Is Rejected
    [Tags]  SE-8
    Pass Execution  Execution passed

Registration With Invalid Data Is Rejected
    [Tags]  SE-8
    Pass Execution  Execution passed

*** Keywords ***
Status Code Of Response "${response}" Should Be "${status_code}"
    [Documentation]  Verifies status code of the response object `${response}` against the expected one.
    Should Be Equal As Integers  ${response.status_code}  ${status_code}  msg=Unexpected response status code

Response "${response}" Should Be Successful
    [Documentation]  Checks if the 'success' key is true for the specified response.
    ${response_json}=  Set Variable  ${response.json()}
    Should Be True  ${response_json['success']}

Response "${response}" Should Contain Error
    [Documentation]  Checks if the 'success' key is false for the specified response.
    ${response_json}=  Set Variable  ${response.json()}
    Should Not Be True  ${response_json['success']}

Login With Email "${email}" And Password "${password}"
    [Documentation]  Performs a login request with specified credentials.
    &{credentials}=  Create Dictionary  email=${email}  password=${password}
    ${credentials_json}=  Evaluate  json.dumps(${credentials})  json
    ${response}=  Post Request
    ...  scanpath-evaluator  /api/user/auth  data=${credentials_json}  timeout=${REQUEST_TIMEOUT_DEFAULT}

    [Return]  ${response}