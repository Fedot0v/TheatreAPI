# Theater Reservation API

This is a Django REST Framework project designed to handle the reservation of tickets for theater shows. It includes functionality to manage shows, available seats, reservations, and ticketing.

## Features

- **Show Management**: Add and manage shows, including show times and seat availability.
- **Reservation System**: Allows users to reserve tickets for a show and automatically generates tickets.
- **Ticket System**: Tickets are linked to a reservation and contain information about the seat and show.
- **Availability Display**: View how many seats are still available for each show.
- **JWT Authentication**: JSON Web Tokens (JWT) are used for secure authentication.
- **API Documentation**: Auto-generated API documentation using Swagger.

## Technologies Used

- **Django**
- **Django REST Framework**
- **DjangoORM**:
- **PostgreSQL**
- **Docker**
- **Swagger**
- **Pytest**

## Installation

### From GitHub

1. Install PostgreSQL and create a database.

2. Clone the repository:
    ```bash
    git clone https://github.com/olga-kim7/Theatre-API-Service.git
    cd Theatre-API-Service
    ```

3. Set up a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Set environment variables:
    ```bash
    export DB_HOST=<your_db_hostname>
    export DB_NAME=<your_db_name>
    export DB_USER=<your_db_username>
    export DB_PASSWORD=<your_db_password>
    export SECRET_KEY=<your_secret_key>
    ```

6. Apply migrations and run the server:
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

### Running with Docker

1. Ensure Docker is installed on your system.

2. Build Docker containers:
    ```bash
    docker-compose build
    ```

3. Start Docker containers:
    ```bash
    docker-compose up
    ```

## Accessing the API

- Create a user: 
  ```bash
  POST /api/user/register/
  
- Obtain an access token:
  ```bash
  POST /api/user/token/

## API Documentation 

- Swagger API documentation is available at:
  ```bash
  http://localhost:8000/api/schema/swagger-ui/

## Access

- **Superuser**: Has full access to all CRUD operations for all resources.
- **Authenticated User**: Can view available shows and make reservations.

  ### Creating a Superuser

  To create a superuser, use the following command:
  ```bash
  python manage.py createsuperuser

### Logging In

After creating a user or superuser, you can log in via the `/api/user/login/` endpoint to obtain your authentication token. Use this token for authenticated requests:

```bash
Authorization: Bearer <your_access_token>
