Write-Host "Starting backend server..."
cd backend
conda activate python3.9.5
uvicorn app.main:app --reload