$output_dir = "output_files"
$psql_path = "C:\Program Files\PostgreSQL\9.5\bin\psql.exe"

# Run the DB setup script
& $psql_path -U postgres -f test_db_setup.sql postgres

# Activate the Python virtual env
& "../../venv/Scripts/activate.ps1"

# Start the application
$proc = Start-Process python '../../run.py' -Passthru
Start-Sleep -Seconds 5

# Ensure that the tests output files directory exists
if (!(Test-Path -Path $output_dir )) {
    New-Item -ItemType directory -Path $output_dir
    Write-Host "Creating output files directory"
}
else {
    Write-Host "Output files directory already exists"
}

# Run the tests
robot --outputdir $output_dir example.robot

# Do cleanup (the app itself has already been terminated via a REST call in RobotFramework)
deactivate
& $psql_path -U postgres -f test_db_teardown.sql postgres
