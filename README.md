# BizCardX-Extracting-Business-Card-Data-with-OCR
___

## Problem Statement
___

The goal of this project is to create an interactive Streamlit application enabling users to upload images of business cards for automated text extraction using EasyOCR. The extracted information includes critical details such as company name, cardholder name, designation, contact information, and address. Users can seamlessly store this extracted data into a MySQL database, supporting multiple entries. Additionally, they can perform read, update, and delete operations on the stored business card data through a user-friendly graphical interface. The emphasis is on a clean UI design and robust database management to ensure an intuitive experience and efficient data handling.


## Required Libraries

To run this project, you'll need to install the following Python libraries. You can do so using `pip`:

- **Streamlit:** Used to create interactive web applications in Python.
   -    pip install streamlit
- **Option Menu:** A Streamlit plugin for interactive dropdown menus.
   -    pip install streamlit-option-menu
- **EasyOCR:** A tool for optical character recognition (OCR).
   -    pip install easyocr
- **Pandas:** Essential for data handling and manipulation.
   -    pip install pandas
- **Matplotlib:** Library for data visualization and plotting.
   -    pip install matplotlib
- **Pillow:** Image processing library.
   -    pip install Pillow
- **io:** Core module for handling streams.
   - Installed with Python by default
- **Base64:** Library for encoding and decoding base64 data.
   - Installed with Python by default
- **MySQL Connector:** For communication with MySQL databases.
   -    pip install mysql-connector-python
- **dotenv:** For managing environment variables.
   -    pip install python-dotenv

Make sure to run these commands in your Python environment to install the required libraries.

## Example Import Statements

Here are the import statements you'll need in your Python program to use these libraries:

```
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import pandas as pd 
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import io
from io import BytesIO
import base64
import mysql.connector
import os
from dotenv import load_dotenv
```

## Setting Up Environment Variables

To securely configure your database connection and credentials, create a `.env` file at the root of your project and define the following environment variables:

```
MYSQL_HOST_NAME = 'Enter Your MYSQL Host Name'
MYSQL_USER_NAME = 'Enter Your MYSQL User Name'
MYSQL_PASSWORD = 'Enter Your MYSQL Password'
MYSQL_DATABASE_NAME = 'Enter Your MYSQL Database Name'
```

# ETL Process for Business Card Data Extraction
___

In this ETL (Extract, Transform, Load) process, we detail the steps involved in extracting, managing, and analyzing data from business cards. Here's the breakdown:

## 1. Data Extraction
- The first step involves extracting relevant information from the uploaded business card images. We utilize Streamlit to allow users to upload images, and EasyOCR extracts key data like company name, cardholder details, contact information, and location details.

## 2. Data Transformation
- Following the extraction, the data undergoes a transformation phase. We structure the extracted information into a well-organized DataFrame, making it easily understandable and accessible. Additional data processing techniques like resizing, cropping, and thresholding can be applied to enhance image quality before passing it to the OCR engine.

## 3. Data Migration to MySQL
- After transformation, the data is prepared for storage. We migrate this extracted and structured data to a MySQL database for efficient storage, retrieval, and further analysis.

## 4. User Interface and Operations
- Streamlit provides an intuitive user interface allowing users to extract text, modify, delete, and run direct SQL queries. This GUI guides users through the extraction process, offers insightful data visualization, and provides database management operations, ensuring an easy, seamless experience.

This ETL process simplifies the extraction, management, and storage of business card data, making it readily available for analysis and insights.


# Business Card Data Extraction User Guide
___

The Business Card Data Extraction application is designed to facilitate the extraction and management of information from business cards using uploaded images. The GUI is organized into different operations: "Extract Data," "Modify," "Delete," and "Direct MYSQL Query."

## Extract Data
- **Single Image Extract:** Upload a single image to extract text data. Click to save the extracted data in the MYSQL database.
- **Multi Image Extract:** Upload multiple images to extract text data and save it in the MYSQL database.

## Modify
- **Update Data:** Modify the stored data in the MySQL database by selecting the Email Address.

## Delete
- **Delete Data:** Remove specific data from the MySQL database by selecting the Email Address.

## Direct MYSQL Query
- **Retrieve Data:** Write your query to analyze and reference relevant table column names.
- **Retrieve Image:** View stored images and download by choosing the Email address.

This user guide provides an overview of the operations available in the Business Card Data Extraction application, guiding users through the process of managing, updating, deleting, and analyzing data from business cards.


# Getting Started
___

To start with the Business Card Data Extraction project, follow these steps:

1. **Clone the Repository:**
   - Begin by cloning this GitHub repository to your local machine. Use the following command:
     ```
     git clone https://github.com/Prakash-Kani/BizCardX-Extracting-Business-Card-Data-with-OCR.git
     ```

2. **Create the .env File for MySQL Connection:**
   - Create a new file named `.env` within your project directory.
   - Enter the following details in the `.env` file, replacing the placeholder values with your MySQL connection details:
     ```
     MYSQL_HOST_NAME = 'Enter Your MySQL Host Name'
     MYSQL_USER_NAME = 'Enter Your MySQL User Name'
     MYSQL_PASSWORD = 'Enter Your MySQL Password'
     MYSQL_DATABASE_NAME = 'Enter Your MySQL Database Name'
     ```
   - Save the `.env` file once you've entered your actual MySQL database connection information.


3. **Install Required Libraries:**
   - Ensure you have the necessary Python libraries installed. You can find the required libraries in the "Required Libraries" section of this README. Use pip for installation.

4. **Run the Business Card Extraction App:**
   - Open your terminal or command prompt and navigate to the project directory.
   - Execute the command:
     ```
     streamlit run main.py
     ```
   - This command will start the Streamlit application.

5. **Utilize the Business Card Extraction App:**
   - Once the app is launched, follow the instructions in the app for extracting data, modifying, deleting, and performing MySQL queries directly.

Now you're all set to use the Business Card Data Extraction app, managing and analyzing data from business cards with ease.
