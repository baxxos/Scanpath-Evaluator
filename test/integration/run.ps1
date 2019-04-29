$output_dir = "output_files"
$psql_path = "C:\Program Files\PostgreSQL\9.5\bin\psql.exe"

& $psql_path -U postgres -f test_db_setup.sql postgres

if (!(Test-Path -Path $output_dir )) {
    New-Item -ItemType directory -Path $output_dir
    Write-Host "Creating output files directory"
}
else {
    Write-Host "Output files directory already exists"
}

& "../../venv/Scripts/activate.ps1"
robot --outputdir $output_dir example.robot
deactivate

& $psql_path -U postgres -f test_db_teardown.sql postgres