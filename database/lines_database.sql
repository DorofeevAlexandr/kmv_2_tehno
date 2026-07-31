
--counters
CREATE TABLE IF NOT EXISTS counters (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY key,
    time timestamp NOT NULL,
    lengths  bigint[],
    connection_counters  Boolean[]
);

CREATE index IF NOT EXISTS times_counters_idx ON counters(time);


--lines
CREATE TABLE IF NOT EXISTS lines (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY key,
    line_number INTEGER  NOT NULL unique,
    name text NOT NULL unique,
    pseudonym text NOT NULL unique,
    port text NOT NULL,
    modbus_adr Integer NOT NULL,
    department text NOT NULL,
    number_of_display Integer NOT NULL,
    cable_number Integer NOT NULL,
    cable_connection_number Integer NOT NULL,
    k  Float NOT NULL,
    created_dt timestamp,
	description text
);

--lines_current_params
CREATE TABLE IF NOT EXISTS lines_current_params (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY key,
    line_number INTEGER  NOT NULL unique,
    connection_counter Boolean,
    indicator_value bigint,
    length Float,
    speed_line Float,
    updated_dt timestamp
);

--lines_statistics
CREATE TABLE IF NOT EXISTS lines_statistics (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY key,
    date timestamp NOT NULL,
    made_kabel  bigint[]
);

CREATE index IF NOT EXISTS times_lines_statistics_idx ON lines_statistics(date);
