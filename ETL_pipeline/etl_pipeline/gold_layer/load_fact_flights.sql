INSERT INTO gold.Fact_Flights (
    flight_date_id,
    airline_id,
    tail_number,
    dep_airport_id,
    arr_airport_id,
    dep_delay,
    dep_delay_tag,
    dep_delay_type,
    arr_delay,
    arr_delay_type,
    flight_duration,
    distance_type
)
SELECT
    f.flight_date,
    a.airline_id,
    f.tail_number,
    f.iata_code_dep,
    f.iata_code_arr,
    CAST(f.dep_delay AS INT),
    (f.dep_delay_tag::INT = 1) AS dep_delay_tag,  -- nếu dep_delay_tag đang dạng số, convert sang boolean
    f.dep_delay_type,
    CAST(f.arr_delay AS INT),
    -- (f.arr_delay_tag::INT = 1) AS arr_delay_tag,
    f.arr_delay_type,
    f.flight_duration,
    f.distance_type
FROM silver.us_flights_clean f
LEFT JOIN gold.Dim_Airline a ON f.airline = a.name
LEFT JOIN gold.Dim_Date d ON f.flight_date = d.date
LEFT JOIN gold.Dim_Plane p ON f.tail_number = p.tail_number
LEFT JOIN gold.Dim_Airport dep ON f.iata_code_dep = dep.airport_id
LEFT JOIN gold.Dim_Airport arr ON f.iata_code_arr = arr.airport_id
WHERE f.flight_date IS NOT NULL
    AND f.tail_number IS NOT NULL
    AND f.iata_code_dep IS NOT NULL
    AND f.iata_code_arr IS NOT NULL;



