# G2P SelfServicePortal

### Technology **Stack**

* Utilizes Next.js as the primary framework for the front-end.
* Tailwind CSS is employed for styling and responsive design.
* tsed-formio for using formio forms alongside tailwind

### Functionality

Overview: The self-service portal is a reference implementation, developed with Next.js and enhanced with Tailwind, offers users the capability to log in using their MOSIP ID. It enables them to browse and access available programs, including forms for specific programs. Users can conveniently submit these forms. Additionally, the self-service portal provides access to a wide range of programs across various domains and offers an efficient search feature for locating specific programs

Supported Functionality:

* Access and submit forms of programs availble
* Since its reference implementation , each components can be tailored to any different design the country needs
* Integration with other OpenG2P API's for data processing

### Design notes

**User Authentication**

**Program Accessibility**:

* Provides a user-friendly interface for users to explore available programs.
* Ensures seamless navigation between different program categories.

**Form Handling**:

* Offers program-specific forms for users to submit.
* Validates and securely stores form data.

**Program Search**:

* Enables easy program discovery through a robust search feature.
* Optimizes search functionality for quick and precise results

**User Experience (UX)**:

* Focuses on creating an intuitive and visually appealing user interface.
* Prioritizes responsive design to ensure a seamless experience on different devices.

**Error Handling**:

* Includes error handling mechanisms to address user input errors and system issues.
* Provides clear and informative error messages to assist users

**Future Enhancements**:

* Identifies potential areas for future enhancements, such as integration with other systems or additional features.

### Source code

{% embed url="https://github.com/OpenG2P/openg2p-portal.git" %}

### Environment Setup: Next.js and FastAPI Integration

#### Prerequisites:

* Node.js and npm installed.
* Python 3.x installed.
* A code editor for development (e.g., Visual Studio Code).

#### Step 1: Clone the Repository

* Open your terminal.
* Clone the project repository from the provided link:

```
git clone https://github.com/OpenG2P/openg2p-portal.git
```

#### Step 2: Setting up the Next.js Application

* Navigate to the project directory:

```
cd openg2p-portal
```

* Install project dependencies:

```
npm install
```

* Start the Next.js development server:

```
npm run dev
```

Your Next.js app is accessible at [http://localhost:3000](http://localhost:3000/).

#### Step 3: Setting up the FastAPI Service

* Navigate to the directory for the FastAPI service:

```
cd fastapi-service
```

* Run the FastAPI service using Uvicorn:

```
uvicorn main:app --reload
```

Your FastAPI service is accessible at [http://localhost:8000](http://localhost:8000/).

#### Step 4: Integrate Next.js with FastAPI

* In your Next.js app is using client-side code to make HTTP requests to your FastAPI service's endpoints (e.g., `http://localhost:8000`).
* By Utilizing libraries like Axios or Fetch for making HTTP requests from your Next.js app.
