CREATE TABLE users(
    username VARCHAR(15) PRIMARY KEY NOT NULL,
    email VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(60) NOT NULL,
    created_at DATE NOT NULL DEFAULT NOW(),
    role VARCHAR(10) NOT NULL
        CHECK (role='User' or role='Demo' or role='Admin')
);


CREATE TABLE projects(
    id SERIAL PRIMARY KEY NOT NULL,
    name VARCHAR(40) NOT NULL,
    description VARCHAR(125) NOT NULL,
    created_at DATE NOT NULL DEFAULT NOW()
);


CREATE TABLE works_on(
    username VARCHAR(15) NOT NULL,
    project_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL
        CHECK (role = 'Developer' or role = 'Project Manager'),

    CONSTRAINT works_users_fk
        FOREIGN KEY(username) REFERENCES users(username)
            ON DELETE CASCADE,

    CONSTRAINT works_projects_fk
        FOREIGN KEY(project_id) REFERENCES projects(id)
            ON DELETE CASCADE,

    PRIMARY KEY(username, project_id)
);


CREATE TABLE tickets(
    id SERIAL PRIMARY KEY NOT NULL,
    name VARCHAR(25) NOT NULL,
    priority VARCHAR(10) NOT NULL
        CHECK (priority = 'None' or priority = 'Low' or priority = 'Medium' or priority = 'High'),
    assigned_user VARCHAR(20) NOT NULL,
    Type VARCHAR(30) NOT NULL
        CHECK (type = 'Bugs/Errors' or type = 'Feature Requests' or type = 'Other Comments' or type = 'Training/Document Requests'),
    project INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL
        CHECK (status = 'New' or status = 'Open' or status = 'In Progress' or  status = 'Additional Info Required'),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT tickets_users_fk
        FOREIGN KEY(assigned_user) REFERENCES users(username)
            ON DELETE CASCADE,

    CONSTRAINT tickets_projects_fk
        FOREIGN KEY(project) REFERENCES projects(id)
            ON DELETE CASCADE
);


CREATE TABLE ticket_comments(
    ticket_id INTEGER PRIMARY KEY NOT NULL,
    message VARCHAR(250) NOT NULL,
    commentor VARCHAR(15) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT comments_tickets_fk
        FOREIGN KEY(ticket_id) REFERENCES tickets(id)
            ON DELETE CASCADE,

    CONSTRAINT comments_users_fk
        FOREIGN KEY(commentor) REFERENCES users(username)
            ON DELETE CASCADE
);

