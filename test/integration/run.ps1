& "C:\Program Files\PostgreSQL\9.5\bin\psql.exe" -U postgres -f test_db_setup.sql postgres

$dir = "output_files"
if (!(Test-Path -Path $dir )) {
    New-Item -ItemType directory -Path $dir
    Write-Host "Creating output files directory"
}
else {
    Write-Host "Output files directory already exists"
}

& "../../venv/Scripts/activate.ps1"
robot --outputdir $dir example.robot
deactivate