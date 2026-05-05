INSERT INTO gold.Dim_Airline (name)
SELECT DISTINCT airline
FROM silver.us_flights_clean
WHERE airline IS NOT NULL
ON CONFLICT (name) DO NOTHING;