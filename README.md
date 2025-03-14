# Multi-User Event Management System

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)

A robust and scalable web platform designed to streamline event creation, management, and participation. Built with **FastAPI**, **SQLAlchemy**, and **Docker**, this system empowers administrators, event organizers, and participants with comprehensive tools—all secured with JWT-based authentication.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Usage Instructions](#usage-instructions)
- [Contributing](#contributing)
- [License](#license)
- [Contact & Support](#contact--support)

---

## Overview

The **Multi-User Event Management System** is an all-in-one platform designed for:

- **Event Organizers:** Seamlessly create, update, and manage events.
- **Participants:** Easily browse, join, and leave events.
- **Administrators:** Oversee user management and event activity.

Built with a modern RESTful API architecture, this solution ensures efficient data handling, enhanced security, and smooth integration with external applications.

---

## Key Features

- **User Authentication & Authorization:**  
  Secure registration, login, and role-based access control using JWT tokens.
  
- **Event Management:**  
  Full CRUD capabilities for events – from creation to deletion.
  
- **User Management:**  
  Manage user profiles with endpoints for registration, login, and profile updates.
  
- **Event Participation:**  
  RSVP functionality allows users to join or leave events effortlessly.
  
- **API-Driven:**  
  Comprehensive RESTful API endpoints with interactive documentation available via `/docs`.
  
- **Containerized Deployment:**  
  Leverage Docker & Docker Compose for consistent deployment across environments.
  
- **Clean Architecture:**  
  Well-organized code structure with clear separation between configuration, routes, models, schemas, and services.

---

## Project Structure

```
multi-user-event-management-main/
├── .env                   # Environment variable configurations
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Multi-container deployment configuration
├── README.md              # This documentation file
├── requirements.txt       # Python dependencies
├── test.db                # SQLite database file (for development/testing)
└── app/
    ├── config.py          # Application configuration settings
    ├── db.py              # Database connection & session management
    ├── main.py            # Application entry point
    ├── middleware.py      # Custom middleware for enhanced request handling
    ├── models.py          # SQLAlchemy models for the database
    ├── schemas.py         # Pydantic schemas for data validation & serialization
    ├── routes/
    │   ├── events.py      # Endpoints for event management
    │   ├── event_participation.py  # Endpoints for event participation
    │   └── users.py       # Endpoints for user management
    └── services/
        └── auth.py        # Authentication logic & token management
```

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed ([Download Python](https://www.python.org/downloads/))
- **Docker & Docker Compose** installed ([Get Docker](https://docs.docker.com/get-docker/))
- **Git** installed ([Get Git](https://git-scm.com/downloads))

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd multi-user-event-management-main
```

### 2. Configure Environment Variables
- Copy `.env` (or create one if necessary) and update settings such as:
  - **DATABASE_URL** (default uses SQLite)
  - **JWT_SECRET_KEY** (for token generation)
  - Other environment-specific variables

### 3. Install Dependencies

#### Using a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Using Docker
```bash
docker-compose up --build
```

### 4. Initialize the Database
- For **SQLite**, the `test.db` file will be created automatically.
- For other databases, run your migration or initialization scripts as required.

---

## Running the Application

### Local Development
```bash
python app/main.py
```

### Docker Deployment
```bash
docker-compose up --build
```

Access the API at [http://localhost:8000](http://localhost:8000) and view interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## API Endpoints

### **User Endpoints:**
- **POST `/register`** – Register a new user.
- **POST `/login`** – Authenticate a user and obtain a JWT.
- **GET `/users`** – List all users.
- **GET `/users/{user_id}`** – Retrieve user details by ID.
- **PUT `/users/{user_id}`** – Update a user's information.
- **DELETE `/users/{user_id}`** – Remove a user.

### **Event Endpoints:**
- **POST `/events`** – Create a new event.
- **PUT `/events/{event_id}`** – Update event details.
- **DELETE `/events/{event_id}`** – Delete an event.
- **GET `/events`** – List all events.
- **GET `/events/{event_id}`** – Retrieve details of a specific event.

### **Event Participation Endpoints:**
- **POST `/events/{event_id}/join`** – Join an event (RSVP).
- **DELETE `/events/{event_id}/leave`** – Leave an event.

---

## Contributing

1. **Fork the Repository.**
2. **Create a Feature Branch:**
   ```bash
   git checkout -b feature-branch
   ```
3. **Commit Your Changes:**
   ```bash
   git commit -m "Describe your changes"
   ```
4. **Push to Your Branch:**
   ```bash
   git push origin feature-branch
   ```
5. **Open a Pull Request:**  
   Provide a detailed description of your changes for review.

---

## Contact & Support

For questions, suggestions, or issues, please contact:

- **Name:** Shubham Madhavi
- **Email:** samsunite2@gmail.com

---
