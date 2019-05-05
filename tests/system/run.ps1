$output_dir = "output_files"
$venv_path = "../../venv"

$psql_test_db_name = "scanpath-evaluator-test"
$psql_path = "C:\Program Files\PostgreSQL\9.5\bin\psql.exe"
$psql_dropdb_path = "C:\Program Files\PostgreSQL\9.5\bin\dropdb.exe"
$psql_dropuser_path = "C:\Program Files\PostgreSQL\9.5\bin\dropuser.exe"
$psql_service_name = "postgresql-x64-9.5"
$psql_service = Get-Service -Name $psql_service_name
$env:DATABASE_URL = "postgresql://test_user:test_user@localhost/$psql_test_db_name"

if ($psql_service.Status -ne "Running") {
    Write-host "Starting the PostgreSQL service"
    Start-Service $psql_service_name
    Start-Sleep -seconds 5
    $psql_service.Refresh()

    if ($psql_service.Status -eq 'Running') {
        Write-Host "PostgreSQL database is running"
    }
    else {
        Write-Host "Failed to start the PostgreSQL database"
    }
}

# Run the DB setup scripts
Write-Host "Setting up test database instance"
$env:PGPASSWORD  = "postgres"
& $psql_path -U postgres -f scripts/db_setup_core.sql -q
$env:PGPASSWORD  = "test_user"
& $psql_path -U test_user -d $psql_test_db_name -f scripts/db_setup_schema.sql -q
& $psql_path -U test_user -d $psql_test_db_name -f scripts/db_setup_data.sql -q

# Activate the Python virtual env
& $venv_path"/Scripts/activate.ps1"

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
$hostname = "http://localhost:8888"
locust --csv=output_files/performance_results --no-web -t60s -c 20 -r 2 --host=$hostname
Invoke-RestMethod -Method Post -Uri $hostname/api/shutdown

# Deactivate the Python virtual env
deactivate

# Database cleanup - drop the test DB, user and environment variables required for connecting
Write-Host "Cleaning up"
$env:PGPASSWORD  = "test_user"
& $psql_dropdb_path -U test_user $psql_test_db_name
$env:PGPASSWORD  = "postgres"
& $psql_dropuser_path -U postgres test_user
Stop-Service $psql_service_name
Remove-Item Env:\DATABASE_URL
Remove-Item Env:\PGPASSWORD