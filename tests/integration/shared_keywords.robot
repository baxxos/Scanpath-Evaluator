*** Settings ***
Library  RequestsLibrary

*** Keywords ***
Terminate Application
    [Documentation]  Attempts to stop the application via a predefined route.
    ${response}=  Post Request  scanpath-evaluator  /api/shutdown
    [Return]  ${response}
