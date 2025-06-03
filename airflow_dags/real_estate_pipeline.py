from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import subprocess

# Hàm kiểm tra có phải ngày cần train model không (Chủ Nhật)
def check_if_training_day(**context):
    """
    Kiểm tra xem hôm nay có phải là Chủ Nhật (ngày 6) không
    Nếu đúng thì chạy train_task, nếu không thì skip_training
    """
    execution_date = context['execution_date']
    weekday = execution_date.weekday()  # 0=Monday, 6=Sunday
    
    if weekday == 6:  # Chủ Nhật
        return 'train_model'
    else:
        return 'skip_training'

# Hàm restart API container
def restart_api():
    """
    Restart container real-estate-app để áp dụng model mới
    """
    try:
        # Restart container
        result = subprocess.run(['docker', 'restart', 'real_estate2_real-estate-app_1'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Container restarted successfully")
        else:
            print(f"Error restarting container: {result.stderr}")
    except Exception as e:
        print(f"Error: {e}")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    'real_estate_pipeline',
    default_args=default_args,
    description='Pipeline BDS: scrape hàng ngày, train model mỗi Chủ Nhật',
    schedule_interval='@daily',  # Chạy hàng ngày
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

# 1. Scrape dữ liệu mỗi ngày (luôn chạy)
scrape_task = BashOperator(
    task_id='scrape_data',
    bash_command='cd /app && python scraper/scraper.py',
    dag=dag,
)

# 2. Kiểm tra xem có phải ngày train model không
branch_task = BranchPythonOperator(
    task_id='check_training_day',
    python_callable=check_if_training_day,
    dag=dag,
)

# 3. Task skip training (cho những ngày không phải Chủ Nhật)
skip_training = DummyOperator(
    task_id='skip_training',
    dag=dag,
)

# 4. Train lại model (chỉ chạy vào Chủ Nhật)
train_task = BashOperator(
    task_id='train_model',
    bash_command='cd /app && python data_processing/train_model.py',
    dag=dag,
)

# 5. Export tham số model (chỉ chạy sau khi train)
export_params_task = BashOperator(
    task_id='export_model_params',
    bash_command='cd /app && python data_processing/export_model_params.py',
    dag=dag,
)

# 6. Restart API app2.py (chỉ chạy sau khi export)
task_restart_api = PythonOperator(
    task_id='restart_api',
    python_callable=restart_api,
    dag=dag,
)

# Thiết lập thứ tự các task
scrape_task >> branch_task
branch_task >> [skip_training, train_task]
train_task >> export_params_task >> task_restart_api
