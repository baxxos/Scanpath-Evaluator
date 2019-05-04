*** Settings ***
Library  RequestsLibrary

*** Keywords ***
Terminate Application
    [Documentation]  Attempts to stop the application via a predefined route.

    ${response}=  Post Request  scanpath-evaluator  /api/shutdown

    [Return]  ${response}

Status Code Of Response Is "${status_code}"
    [Documentation]  Verifies status code of the response object `${response}` against the expected one.

    Should Be Equal As Integers  ${TEST_RESPONSE.status_code}  ${status_code}  msg=Unexpected response status code

Response Is Successful
    [Documentation]  Checks if the 'success' key is true for the specified response object.

    ${response_json}=  Set Variable  ${TEST_RESPONSE.json()}
    Log  ${response_json}
    Should Be True  ${response_json['success']}  msg=Response should have been successful, but it was not.

Response Is Not Successful
    [Documentation]  Checks if the 'success' key is false for the specified response object.

    ${response_json}=  Set Variable  ${TEST_RESPONSE.json()}
    Log  ${response_json}
    Should Not Be True  ${response_json['success']}  msg=Response should not have been successful, but it was.

Response Contains Payload "${payload}"
    [Documentation]  Checks if the specified success response contains the expected `${payload}`.

    ${response_json}=  Set Variable  ${TEST_RESPONSE.json()}
    Dictionary Should Contain Key  ${response_json}  load  msg=Data payload was not present in the response
    Should Be Equal  ${response_json['load']}  ${payload}  msg=Response does not contain the expected payload

Response Contains Error Message "${message}"
    [Documentation]  Checks if the specified error response contains the expected `${message}`.

    ${response_json}=  Set Variable  ${TEST_RESPONSE.json()}
    Dictionary Should Contain Key  ${response_json}  message  msg=Error message was not present in the response
    Should Contain  ${response_json['message']}  ${message}  msg=Response does not contain the expected error message
