# Hướng dẫn sử dụng Airflow + Docker

## Cài đặt nhanh

1. **Cài đặt Docker Desktop** (nếu chưa có)
2. **Chạy file start.bat**
   ```cmd
   start.bat
   ```

## Truy cập các dịch vụ

- **Airflow Web UI**: http://localhost:8080
  - Username: `admin`
  - Password: `admin`

- **Real Estate App**: http://localhost:5000

## Cách hoạt động

### Pipeline tự động:
1. **Hàng ngày**: Scrape dữ liệu bất động sản
2. **Chủ Nhật**: Train lại model + Export parameters + Restart API

### Các task trong Airflow:
- `scrape_data`: Thu thập dữ liệu mới
- `check_training_day`: Kiểm tra có phải Chủ Nhật không
- `train_model`: Huấn luyện lại model
- `export_model_params`: Xuất tham số model
- `restart_api`: Khởi động lại API với model mới

## Quản lý

### Xem logs:
```cmd
docker-compose logs -f
```

### Xem trạng thái:
```cmd
docker-compose ps
```

### Dừng services:
```cmd
stop.bat
```

### Reset toàn bộ (xóa dữ liệu):
```cmd
docker-compose down -v
```

## Troubleshooting

### Nếu có lỗi port đã sử dụng:
- Thay đổi port trong `docker-compose.yml`
- Hoặc dừng service đang dùng port đó

### Nếu Airflow không khởi động:
```cmd
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
```

### Restart một service cụ thể:
```cmd
docker-compose restart real-estate-app
docker-compose restart airflow-scheduler
```
