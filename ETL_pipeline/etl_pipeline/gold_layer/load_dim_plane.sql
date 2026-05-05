INSERT INTO gold.Dim_Plane (tail_number, manufacturer, model, aircraft_age)
SELECT DISTINCT
    tail_number,
    manufacturer,
    model,
    aircraft_age
FROM silver.us_flights_clean
WHERE tail_number IS NOT NULL
ON CONFLICT (tail_number) DO NOTHING;

