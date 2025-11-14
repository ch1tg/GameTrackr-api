# 🚀 GameTrackr API (Backend)

This is the backend for the GameTrackr project, a full-stack game tracking application.

This API is built with **Flask (Python)** and serves as a production-ready REST API that handles user authentication, profile management, and wishlists. It also acts as a secure **proxy** for the [RAWG.io API](https://rawg.io/apidocs), hiding the private API key from the client.

---

## ✨ Key Features

* **Full JWT Authentication:** Secure login (`/login`), registration (`/register`), and logout (`/logout`) using `flask-jwt-extended` with HttpOnly cookies.
* **CSRF Protection:** Built-in protection for all authenticated endpoints.
* **User Management:** Full CRUD for user profiles, including `GET /me`, `PATCH /me`, `PUT /me/password`, and `DELETE /me`.
* **RAWG Proxy:** Securely fetches game data from RAWG.io without exposing the API key (endpoints: `/games/trending`, `/games/<id>`).
* **Wishlist System:** Complete protected API (`GET`, `POST`, `DELETE`) for managing user wishlists, sorted by date added.
* **Public Wishlist View:** A public, paginated endpoint (`/users/<username>/wishlist`) that aggregates wishlist data and game previews for user profiles.
* **Database Migrations:** Uses `Flask-Migrate` (Alembic) for easy database schema updates.
* **API Documentation:** Live, interactive API documentation powered by **Flasgger (Swagger)** available at `/apidocs`.

---

## 💻 Tech Stack

* **Framework:** Flask
* **ORM:** Flask-SQLAlchemy
* **Migrations:** Flask-Migrate
* **Schemas (Serialization):** Flask-Marshmallow
* **Authentication:** Flask-JWT-Extended (using HttpOnly Cookies)
* **Documentation:** Flasgger (Swagger UI)
* **Database:** MySQL
* **Containerization:** Docker & Docker Compose
* **WSGI Server:** Gunicorn

---

## ⚙️ Setup and Installation

### 1. Prerequisites

* Docker and Docker Compose must be installed.
* A [RAWG.io API Key](https://rawg.io/apidocs) (it's free).

### 2. Configuration

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/GameTrackr.git](https://github.com/your-username/GameTrackr.git)
    cd GameTrackr/GameTrackr-api
    ```

2.  **Create the Environment File:**
    Create a file named `.env` in the `GameTrackr-api/` directory.

3.  **Add Environment Variables:**
    Copy and paste the following into your `.env` file, filling in your own values.

    ```ini
    # Flask App Secrets
    SECRET_KEY=your_strong_random_secret_key_for_flask
    JWT_SECRET_KEY=your_strong_random_secret_key_for_jwt

    # Database (Docker)
    # You can keep these as-is
    MYSQL_ROOT_PASSWORD=your_root_password
    MYSQL_DATABASE=gametrackr
    MYSQL_USER=gametrackr
    MYSQL_PASSWORD=your_db_user_password
    DATABASE_URL=mysql+pymysql://gametrackr:your_db_user_password@db/gametrackr

    # RAWG.io API Key
    RAWG_API_KEY=your_rawg_api_key_goes_here
    ```

### 3. Running the Application

1.  **Build and Run Docker:**
    From the `GameTrackr-api/` directory, run:
    ```bash
    docker-compose up -d --build
    ```
    This will build the Flask app, start the MySQL database, and run them.

2.  **Apply Database Migrations:**
    The first time you run the app, you need to create the tables.
    ```bash
    docker-compose exec app flask db upgrade
    ```
    *(Run this command any time you change the `app/models/`)*

### 4. Accessing the API

* **API URL:** `http://localhost:80/api` (The Docker container maps port 5000 to port 80)
* **Swagger Docs:** `http://localhost:80/apidocs`
