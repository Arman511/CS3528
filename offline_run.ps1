# Start MongoDB service
try {
    Start-Service -Name "MongoDB"
    Write-Host "MongoDB service started successfully."
} catch {
    Write-Host "Failed to start MongoDB service. Error: $_"
}

# Set environment variables
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "1"
$env:IS_TEST = "False"
$env:OFFLINE = "True"

# Run Flask application
flask run