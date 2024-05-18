# Distributed Image Processing System Using Cloud Computing

## Description

This project serves as the culmination of the **Distributed Computing course** offered by the **Faculty of Engineering, Ain Shams University**. Our goal was to demonstrate practical knowledge in distributed systems, scalability, and efficient computation. The system we developed showcases key concepts and technologies relevant to distributed computing. The system offers a variety of image processing services that are parallelized using MPI. The system leverages cloud services from Google Cloud such as Cloud Compute Engine and Cloud Storage. This system has also been load tested to demonstrate its capacity and scalability. Fault tolerance techniques have been implemented to ensure our system's reliability and availability.

## System Components

### 1. Client GUI

- **Description**: The user interface for submitting processing requests. The GUI is developed using PyQt5 to offer a modern feel that's user friendly and easy to navigate.
- **Functionality**:
    - Allows users to upload multiple images.
    - Specifies processing options.
    - Allows users to download results.

### 2. Processing Nodes

- **Description**: Compute engine instances with docker containers that are responsible for actual computation. These instances run MPI program that can parallelize the execution of the image processing through converting the image into and array and dividing the image into chunks keeping in mind how to deal with the ghost cells to ensure the processing doesn't just run fast and efficiently but right. Each process handles a chunk and performs the necessary processing whilst also updating the other processes with the needed data, finally all worker processes send the results back to the master process which reconstructs the arrays into the resulting image.
- **Functionality**:
    - Receive tasks from the requests queue.
    - Update their status (e.g., "in progress," "completed") in Redis.
    - Store processed results in cloud storage.

### 3. Cloud Storage

- **Description**: Stores processed data securely.
- **Functionality**:
    - Generates presigned links for users to download results.

### 4. Notification System (Redis)

- **Description**: Utilizes Redis as an in-memory data store.
- **Functionality**:
    - Processing nodes publish events (e.g., task completion) to Redis.
    - A separate notification service subscribes to these events.
    - Sends real-time notifications to users via the client GUI.

### 5. RabbitMQ Requests Queue

- **Description**: Manages the queue of incoming processing requests.
- **Functionality**:
    - Ensures reliable message delivery to processing nodes.

## Installation

Provide instructions on how to set up the project locally or deploy it in a cloud environment.

## Usage

Explain how users can interact with the system, submit tasks, and retrieve results.
