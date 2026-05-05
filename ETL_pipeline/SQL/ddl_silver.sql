-- CREATE TABLE IF NOT EXISTS silver.us_flights_23 (
--     flight_date DATE,
--     day_of_week INT,
--     airline VARCHAR(50),
--     tail_number VARCHAR(50),
--     dep_airport VARCHAR(10),
--     dep_city_name VARCHAR(50),
--     dep_time_label VARCHAR(20),
--     dep_delay FLOAT,
--     dep_delay_tag VARCHAR(20),
--     dep_delay_type VARCHAR(20),
--     arr_airport VARCHAR(10),
--     arr_city_name VARCHAR(50),
--     arr_delay FLOAT,
--     arr_delay_type VARCHAR(20),
--     flight_duration INT,
--     distance_type VARCHAR(20),
--     delayCarrier INT,
--     delayWeather INT,
--     delayNAS INT,
--     delaySecurity INT,
--     delayLastAircraft INT,
--     manufacturer VARCHAR(50),
--     model VARCHAR(100),
--     aircraft_age INT
-- );

-- CREATE TABLE IF NOT EXISTS silver.airports_geolocation (
--     iata_code VARCHAR(10),
--     airport_name VARCHAR(50),
--     city VARCHAR(50),
--     state VARCHAR(3),
--     country VARCHAR(3),
--     latitude FLOAT,
--     longitude FLOAT
-- );

-- CREATE TABLE IF NOT EXISTS silver.cancelled_diverted_23 (
--     flight_date DATE,
--     day_of_week INT,
--     airline VARCHAR(50),
--     tail_number VARCHAR(50),
--     cancelled BOOLEAN,
--     diverted BOOLEAN,
--     dep_airport VARCHAR(3),
--     dep_city_name VARCHAR(30),
--     dep_time_label VARCHAR(20),
--     dep_delay FLOAT,
--     dep_delay_tag VARCHAR(20),
--     dep_delay_type VARCHAR(20),
--     arr_airport VARCHAR(10),
--     arr_city_name VARCHAR(50),
--     arr_delay FLOAT,
--     arr_delay_type VARCHAR(20),
--     flight_duration INT,
--     distance_type VARCHAR(20),
--     delayCarrier INT,
--     delayWeather INT,
--     delayNAS INT,
--     delaySecurity INT,
--     delayLastAircraft INT
-- );

-- CREATE TABLE IF NOT EXISTS silver.weather_by_airport (
--     date_time DATE,
--     tavg FLOAT,
--     tmin FLOAT,
--     tmax FLOAT,
--     prcp FLOAT,
--     snow FLOAT,
--     wdir FLOAT,
--     wspd FLOAT,
--     pres FLOAT,
--     airport_id VARCHAR(3)
-- );

CREATE TABLE IF NOT EXISTS silver.us_flights_clean (
    flight_date DATE,
    day_of_week INT,
    airline VARCHAR(50),
    tail_number VARCHAR(50),

    dep_airport VARCHAR(10),
    dep_city_name VARCHAR(100),
    dep_time_label VARCHAR(20),
    dep_delay FLOAT,
    dep_delay_tag VARCHAR(20),
    dep_delay_type VARCHAR(20),

    arr_airport VARCHAR(10),
    arr_city_name VARCHAR(100),
    arr_delay FLOAT,
    arr_delay_type VARCHAR(20),

    flight_duration INT,
    distance_type VARCHAR(20),

    -- delayCarrier INT,
    -- delayWeather INT,
    -- delayNAS INT,
    -- delaySecurity INT,
    -- delayLastAircraft INT,

    manufacturer VARCHAR(100),
    model VARCHAR(100),
    aircraft_age INT,

    iata_code_dep VARCHAR(10),
    airport_dep VARCHAR(100),
    city_dep VARCHAR(100),
    state_dep VARCHAR(50),
    latitude_dep FLOAT,
    longitude_dep FLOAT,

    iata_code_arr VARCHAR(10),
    airport_arr VARCHAR(100),
    city_arr VARCHAR(100),
    state_arr VARCHAR(50),
    latitude_arr FLOAT,
    longitude_arr FLOAT
);

