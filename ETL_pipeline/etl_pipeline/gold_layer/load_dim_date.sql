INSERT INTO gold.Dim_Date (
    date, 
    quarter, 
    month, 
    week, 
    day, 
    day_of_week, 
    is_holiday
)
SELECT DISTINCT
    flight_date AS date,
    EXTRACT(QUARTER FROM flight_date) AS quarter,
    EXTRACT(MONTH FROM flight_date) AS month,
    EXTRACT(WEEK FROM flight_date) AS week,
    EXTRACT(DAY FROM flight_date) AS day,
    TO_CHAR(flight_date, 'Dy') AS day_of_week,
    0 AS is_holiday -- giả định chưa có thông tin holiday, hoặc bạn thay bằng join bảng holiday nếu có
FROM silver.us_flights_clean
WHERE flight_date IS NOT NULL
ON CONFLICT (date) DO NOTHING; -- tránh trùng key

