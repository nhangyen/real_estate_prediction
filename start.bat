@echo off
echo Khoi dong Airflow + Real Estate App voi Docker...

REM Tao thu muc logs neu chua co
if not exist "logs" mkdir logs

echo Building Docker image...
docker-compose build

echo Starting services...
docker-compose up -d

echo Doi 30 giay de services khoi dong...
timeout /t 30

echo.
echo ===========================================
echo THONG TIN TRUY CAP:
echo ===========================================
echo Airflow Web UI: http://localhost:8080
echo   - Username: admin
echo   - Password: admin
echo.
echo Real Estate App: http://localhost:5000
echo.
echo PostgreSQL: localhost:5432
echo   - Username: airflow
echo   - Password: airflow
echo ===========================================
echo.
echo Cac lenh huu ich:
echo   docker-compose ps          (xem trang thai services)
echo   docker-compose logs -f     (xem logs)
echo   docker-compose down        (dung tat ca services)
echo ===========================================

pause
