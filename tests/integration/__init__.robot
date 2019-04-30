*** Settings ***
Resource  shared_keywords.robot

Suite Setup  Create Session  scanpath-evaluator  http://localhost:8888
Suite Teardown  Run Keywords
...             Terminate Application
...       AND   Delete All Sessions