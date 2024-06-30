# VendorSphere Backend

Welcome to the backend repository of VendorSphere, the ultimate platform for vendors and retailers to discover, negotiate, contract, and collaborate with each other. Our application also provides comprehensive ERP services to streamline your business operations.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Technologies](#technologies)
- [Getting Started](#getting-started)
- [Contributing](#contributing)

## About

VendorSphere is designed to foster seamless collaboration between vendors and retailers. By providing tools for discovery, negotiation, contracting, and collaboration, we aim to streamline the entire vendor-retailer relationship. Additionally, our integrated ERP services help businesses manage their operations more efficiently.

## Features

- **Vendor Discovery:** Easily find and connect with potential vendors.
- **Negotiation Tools:** Streamline the negotiation process with built-in tools.
- **Contract Management:** Manage contracts effectively within the platform.
- **Collaboration Workspace:** Work together with vendors in a dedicated workspace.
- **ERP Services:** Integrated ERP solutions to manage inventory, orders, and more.

## Technologies

- **Backend:** Django
- **Database:** PostgreSQL
- **Deployment:** Google Cloud Platform (GCP)
- **Frontend:** [React (Separate Repository)](https://github.com/umer-farooq1784/VendorSphere-Frontend/)

## Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

- Python and pip installed
- PostgreSQL installed
- Git installed

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/your-username/vendorsphere-backend.git

2. Create Virtual Environment 
   ```sh
   python -m venv env

on windows
   ```sh
   .\env\Scripts\activate

3. Install req packages 
   ```sh
   pip install -r requirements.txt

4. Create Database
   ```sh
   CREATE DATABASE vendorsphere;
5. Apply Migrations
   ```sh
   python manage.py migrate

6. Start Server
   ```sh
   python manage.py runserver

## Contributing
We welcome contributions! To contribute:

### Fork the Project
- Create your Feature Branch (git checkout -b feature/AmazingFeature)
- Commit your Changes (git commit -m 'Add some AmazingFeature')
- Push to the Branch (git push origin feature/AmazingFeature)
- Submit a Pull Request
