# Dự án Dự đoán Giá Bất động sản

Dự án này là một ứng dụng web cho phép dự đoán giá bất động sản dựa trên các đặc điểm như địa chỉ (để tính khoảng cách đến một điểm trung tâm), diện tích, số phòng ngủ và số phòng tắm. Dự án bao gồm các thành phần để thu thập dữ liệu, làm sạch dữ liệu, huấn luyện mô hình học máy với PySpark, và cung cấp API cũng như giao diện người dùng thông qua Flask.

## Các tính năng chính

*   Giao diện web để nhập thông tin và nhận dự đoán giá nhà.
*   API endpoint để dự đoán giá theo chương trình.
*   Quy trình xử lý dữ liệu: làm sạch và tính toán các đặc trưng (ví dụ: khoảng cách).
*   Huấn luyện mô hình hồi quy tuyến tính sử dụng PySpark.
*   Lưu trữ dữ liệu bất động sản và lịch sử dự đoán bằng MongoDB.
*   Luồng xử lý dữ liệu thời gian thực với Apache Kafka (consumer được cung cấp, producer cần được thiết lập riêng, ví dụ: từ các script cào dữ liệu).


## Yêu cầu hệ thống

*   Python 3.8+
*   MongoDB
*   Apache Kafka & Zookeeper
*   Apache Spark (có thể cài đặt riêng hoặc sử dụng bản đi kèm PySpark)

## Cài đặt

1.  **Clone repository**
    ```bash
    git clone <your-repository-url>
    cd real_estate2
    ```

2.  **Tạo và kích hoạt môi trường ảo:**
    ```bash
    python -m venv venv
    # Trên Windows
    # venv\Scripts\activate
    # Trên macOS/Linux
    # source venv/bin/activate
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Đảm bảo MongoDB và Kafka đang chạy:**
    *   Khởi động Zookeeper.
    *   Khởi động Kafka server.
    *   Khởi động MongoDB server.

5.  **Tạo Kafka topic:**
    Topic mặc định được sử dụng là `real_estate_data` (xem trong [`kafka_pipeline/kafka_config.py`](kafka_pipeline/kafka_config.py)).

## Quy trình vận hành

### 1. Chuẩn bị dữ liệu và Huấn luyện mô hình

a.  **(Tùy chọn) Làm sạch dữ liệu trong MongoDB:**
    Nếu bạn có dữ liệu thô trong MongoDB cần được làm sạch (ví dụ: tính khoảng cách, trích xuất quận), chạy script:
    ```bash
    python data_processing/clean_data.py
    ```
    Script này sẽ đọc dữ liệu từ collection `test` trong database `real_estate` của MongoDB, tính toán khoảng cách đến Hoàn Kiếm và trích xuất quận, sau đó cập nhật lại các bản ghi.

b.  **Huấn luyện mô hình:**
    Chạy script để huấn luyện mô hình hồi quy tuyến tính bằng PySpark. Script này đọc dữ liệu từ MongoDB (collection `properties2`, database `real_estate`).
    ```bash
    python data_processing/train_model.py
    ```
    **Lưu ý:** Để lưu mô hình Spark đã huấn luyện (cần cho `app.py` và `export_model_params.py`), hãy bỏ comment dòng `model.save("models/lr_model")` trong [`data_processing/train_model.py`](data_processing/train_model.py).

c.  **Trích xuất tham số mô hình (cho `app.py`):**
    Sau khi mô hình Spark được huấn luyện và lưu tại `models/lr_model`, chạy script sau để trích xuất các hệ số (coefficients) và intercept, rồi lưu vào `output/model_params.json`.
    ```bash
    python data_processing/export_model_params.py
    ```

### 2. Luồng dữ liệu Kafka 

a.  **Chạy Kafka Consumer:**

b.  **Chạy Kafka Producer:**

### 3. Chạy ứng dụng Web Flask

Dự án cung cấp hai phiên bản ứng dụng Flask:

a.  **`app2.py` (Sử dụng NumPy và `model_params.json`):**
    Ứng dụng này tải các tham số mô hình từ `output/model_params.json` và thực hiện dự đoán bằng NumPy.
    ```bash
    python app2.py
    ```

Sau khi chạy ứng dụng trên, truy cập vào `http://127.0.0.1:5000/` trong trình duyệt của bạn.

## API Endpoints

Ứng dụng Flask (`app.py`) cung cấp api endpoint dự đoán
        ```

## Công nghệ sử dụng

*   **Backend:** Python, Flask
*   **Machine Learning:** PySpark (Spark MLlib), NumPy
*   **Database:** MongoDB (sử dụng Pymongo và Mongo Spark Connector)
*   **Data Streaming:** Apache Kafka (sử dụng kafka-python)
*   **Frontend:** HTML, CSS (Bootstrap 5), JavaScript
*   **Thư viện khác:** requests (để gọi API geocoding)


