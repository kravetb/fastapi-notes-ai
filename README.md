# fastapi-notes-ai
## Test task execution plan
### Development settings
Configured git repositories, created a project, thought out the architecture,
created Docker containers for the PostgresSQL database and web application,
launched a server for local development via Docker Desktop.
### RESTful API development
Created models for notes and note versions,
developed paths for each CRUD operation for a Note,
and also added the ability to get the version history of a Note
and the ability to revert to an old version.
### Integration GEMINI AI
Received an API token, created a function that uses AI to return 
a summary of the content in a Note, 
integrated this function into the path to retrieve 
all notes to reduce the content without losing content
### Creating a function Analytics
Created a CRUD function that retrieves all notes from 
the database and returns statistics for all notes using
the NLTK and Numpy libraries
### Creating tests
Wrote tests for each path in the API,
fixed any bugs that arose during the writing process

## How to launch the app

#### 1. Copy repository from HitHub
#### 2. Add a <u>.env</u> file based on the <u>.env.sample</u> file
#### 3. Compile and run the application using the command:
`docker-compose up --build`
