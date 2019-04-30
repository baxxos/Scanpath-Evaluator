*** Settings ***
Library  RequestsLibrary

*** Keywords ***
Terminate Application
    [Documentation]  Attempts to stop the application via a predefined route.

    ${response}=  Post Request  scanpath-evaluator  /api/shutdown

    [Return]  ${response}

Status Code Of Response "${response}" Should Be "${status_code}"
    [Documentation]  Verifies status code of the response object `${response}` against the expected one.

    Should Be Equal As Integers  ${response.status_code}  ${status_code}  msg=Unexpected response status code

Response "${response}" Should Be Successful
    [Documentation]  Checks if the 'success' key is true for the specified response.

    ${response_json}=  Set Variable  ${response.json()}
    Log  ${response_json}
    Should Be True  ${response_json['success']}

Response "${response}" Should Contain Error
    [Documentation]  Checks if the 'success' key is false for the specified response.

    ${response_json}=  Set Variable  ${response.json()}
    Log  ${response_json}
    Should Not Be True  ${response_json['success']}
