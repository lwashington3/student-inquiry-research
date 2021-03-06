CREATE database police_brutality;
CREATE TABLE police_brutality.wapo_fatal_force(
    id INT PRIMARY KEY UNIQUE NOT NULL,
    name VARCHAR(80),
    date DATE NOT NULL,
    manner_of_death VARCHAR(20),
    weapon VARCHAR(40),
    age INT,
    gender enum('Male', 'Female', 'Unknown') DEFAULT 'Unknown',
    race enum('White', 'Black', 'Asian', 'Native American', 'Hispanic', 'Other', 'Unknown') DEFAULT 'Unknown',
    city VARCHAR(40),
    state CHAR(2) NOT NULL,
    mental_illness_symptoms BOOLEAN NOT NULL,
    threat_level enum('Attack', 'Other', 'Undetermined') DEFAULT 'Undetermined',
    fleeing enum('Not fleeing', 'Car', 'Foot', 'Other', 'Unknown'),
    body_camera BOOLEAN NOT NULL,
    longitude DECIMAL(6, 3),
    latitude DECIMAL(5, 3),
    exact_geocoding BOOLEAN NOT NULL
);

CREATE TABLE police_brutality.mapping_police_violence(
    id INT PRIMARY KEY UNIQUE NOT NULL,
    name VARCHAR(80) DEFAULT 'Name withheld by Police',
    age INT,
    gender enum('Male', 'Female', 'Unknown', 'Transgender') DEFAULT 'Unknown',
    race enum('White', 'Black', 'Asian', 'Native American', 'Hispanic', 'Other', 'Unknown', 'Pacific Islander') DEFAULT 'Unknown',
    date DATE NOT NULL,
    address VARCHAR(80),
    city VARCHAR(40),
    state VARCHAR(2),
    zipcode INT,
    county VARCHAR(40),
    responsible_agency VARCHAR(200),
    ori_agency_identifier VARCHAR(80),
    cause_of_death VARCHAR(50),
    official_disposition_of_death VARCHAR(200),
    criminal_charges VARCHAR (100),
    mental_illness_symptoms enum('true', 'false', 'Unknown') DEFAULT 'Unknown',
    armed enum('Allegedly Armed', 'Unclear', 'Vehicle', 'Unarmed') DEFAULT 'Unclear',
    alleged_weapon VARCHAR(40),
    alleged_threat_level enum('Attack', 'Undetermined', 'Other', 'None') DEFAULT 'Undetermined',
    fleeing enum('Not Fleeing', 'Unknown', 'Foot', 'Car', 'Other', 'Car and Foot') DEFAULT 'Unknown',
    body_camera enum('True', 'False', 'Unknown') DEFAULT 'Unknown',
    wapo_id INT UNIQUE,
    fatal_encounters_id INT UNIQUE,
    off_duty_killing BOOLEAN,
    population_density enum('Suburban', 'Urban', 'Rural', 'Undetermined') DEFAULT 'Undetermined',
    encounter_type VARCHAR(70),
    call_for_service enum('True', 'False', 'Unavailable') DEFAULT 'Unavailable',
    census_tract INT,
    census_tract_median_household_income INT,
    longitude FLOAT,
    latitude FLOAT,
    FOREIGN KEY (wapo_id) REFERENCES wapo_fatal_force(id)
);

# Skipping 'URL of image of victim', 'A brief description of the circumstances surrounding the death', 'Link to news article or photo of official document'