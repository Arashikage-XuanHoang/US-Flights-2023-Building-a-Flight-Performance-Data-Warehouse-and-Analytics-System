CREATE TABLE IF NOT EXISTS gold.Dim_Date (
    date DATE PRIMARY KEY,
    quarter INTEGER,
    month INTEGER,
    week INTEGER,
    day INTEGER,
    day_of_week VARCHAR(3) CHECK (day_of_week IN ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')),
    is_holiday INTEGER
);

CREATE TABLE IF NOT EXISTS gold.Dim_Airline (
    airline_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS gold.Dim_Airport (
    airport_id VARCHAR(3) PRIMARY KEY,
    airport_name VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(2),
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE IF NOT EXISTS gold.Dim_Plane (
    tail_number VARCHAR(10) PRIMARY KEY,
    manufacturer VARCHAR(50),
    model VARCHAR(10),
    aircraft_age INT
);

CREATE TABLE IF NOT EXISTS gold.Fact_Flights (
    fact_id SERIAL PRIMARY KEY,
    flight_date_id DATE,
    airline_id INT,
    tail_number VARCHAR(6),
    dep_airport_id VARCHAR(3),
    arr_airport_id VARCHAR(3),
    dep_delay INT,
    dep_delay_tag BOOLEAN,
    dep_delay_type TEXT,
    arr_delay INT,
    arr_delay_type TEXT,
    flight_duration INT,
    distance_type TEXT,
    CONSTRAINT fk_flight_date FOREIGN KEY (flight_date_id) REFERENCES gold.Dim_Date(date),
    CONSTRAINT fk_airline FOREIGN KEY (airline_id) REFERENCES gold.Dim_Airline(airline_id),
    CONSTRAINT fk_plane FOREIGN KEY (tail_number) REFERENCES gold.Dim_Plane(tail_number),
    CONSTRAINT fk_dep_airport FOREIGN KEY (dep_airport_id) REFERENCES gold.Dim_Airport(airport_id),
    CONSTRAINT fk_arr_airport FOREIGN KEY (arr_airport_id) REFERENCES gold.Dim_Airport(airport_id)
);
