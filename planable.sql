CREATE TABLE users(
    id SERIAL PRIMARY KEY NOT NULL,
    email character varying NOT NULL UNIQUE,
    password character varying NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
)

INSERT INTO users(email,password) VALUES('test@gmail.com', 12345);




