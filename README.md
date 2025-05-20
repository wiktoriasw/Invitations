# Invitations

## Overview

**Invitations** is a FastAPI-based application for managing event invitations, such as weddings and other gatherings. It provides endpoints for creating, updating, and tracking invitations to streamline event planning and guest management.

## Run

1. Clone the repository:
    ```bash
    git clone https://github.com/wiktoriasw/Invitations.git
    ```

2. Navigate to the project directory:
    ```bash
    cd Invitations
    ```

3. Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up the SECRET_KEY as described in the [Configuration](#configuration) section below.
5. Run the server with:
    ```bash
    fastapi dev main.py
    ```

## Tests

1. Run tests:
    ```bash
    pytest
    ```

## Configuration

### Use environment variables or create `.env` file

- `SECRET_KEY` — JWT secret key. **No default value; you need to assign it.**
   
    - Generate key:
        ```bash
        openssl rand -hex 32
        ```
    - Example: 
        ```bash
        SECRET_KEY=4jfjir...
        ```

- `ALGORITHM` - JWT hashing algorithm - Default: `HS256`

- `SQLALCHEMY_DATABASE_URL` - Database connection string [SQLAlchemy compatible](https://docs.sqlalchemy.org/en/20/core/engines.html) - Default: `"sqlite:///./sql_app.db"`
