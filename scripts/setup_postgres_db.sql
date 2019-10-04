-- PostgreSQL database tables creation

CREATE TABLE song_info (
    id          BIGINT PRIMARY KEY,
    source_id   VARCHAR(255) NOT NULL,
    name        VARCHAR(255) NOT NULL, 
    artist      VARCHAR(255) NOT NULL,
    year        INT,
    source      VARCHAR(255) CHECK (source IN ('msd', 'spotify'))
);

CREATE TABLE song_vectors (
    id          BIGINT PRIMARY KEY,
    vector      FLOAT(32)[] NOT NULL,
    method      VARCHAR(255) CHECK (method in ('gauss', 'gmm', 'pca', 'cnn'))
);
