*** Settings ***
Library  RequestsLibrary

Suite Setup  Create Session 	scanpath-evaluator 	http://localhost:8888
Suite Teardown  Terminate Application

*** Keywords ***
Terminate Application
    [Documentation]  Attempts to stop the application via a predefined route.
    ${response}=  Post Request  scanpath-evaluator  /shutdown
    [Return]  ${response}

*** Test Cases ***
Example Test Case
    Log  Example test case