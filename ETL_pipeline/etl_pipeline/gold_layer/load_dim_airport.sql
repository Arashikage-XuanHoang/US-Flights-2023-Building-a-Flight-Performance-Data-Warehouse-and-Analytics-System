INSERT INTO gold.Dim_Airport (airport_id, airport_name, city, state, latitude, longitude)
SELECT DISTINCT
    iata_code_dep AS airport_id,
    airport_dep AS airport_name,
    city_dep AS city,
    state_dep AS state,
    latitude_dep AS latitude,
    longitude_dep AS longitude
FROM silver.us_flights_clean
WHERE iata_code_dep IS NOT NULL

UNION

SELECT DISTINCT
    iata_code_arr AS airport_id,
    airport_arr AS airport_name,
    city_arr AS city,
    state_arr AS state,
    latitude_arr AS latitude,
    longitude_arr AS longitude
FROM silver.us_flights_clean
WHERE iata_code_arr IS NOT NULL

ON CONFLICT (airport_id) DO NOTHING;


