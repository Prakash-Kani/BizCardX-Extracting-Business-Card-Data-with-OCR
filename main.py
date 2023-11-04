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

# Load environment variables from .env file
load_dotenv()

# MYSQL Connection
mysql_host_name = os.getenv("MYSQL_HOST_NAME")
mysql_user_name = os.getenv("MYSQL_USER_NAME")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database_name = os.getenv("MYSQL_DATABASE_NAME")

db = mysql.connector.connect(host = mysql_host_name,
                             user = mysql_user_name,
                             password = mysql_password,
                             database = mysql_database_name)
mycursor = db.cursor(buffered = True)

lst=[]
def To_Data_identification(a):
    data = {'Image':'',
            'Name':'',
            'Designation': "",
            'Email_Address': '',
            'Area': '',
            'City': "",
            'State': "", 
            'Pincode':"",
            'Mobile_No' : "",
            'Website_Url' : '',
            'Company': '',
            'Category': "",
            'Business_Card_Image_base64':''}
    area =''
    address=''
    contact=[]
    companydetails=''
    for i in a:
        if a.index(i)==0:
            data['Name'] = i[1]
        elif a.index(i)==1:
            data['Designation'] = i[1]
        elif '+' in i[1] or '-' in i[1]:
            # print(i[1])
            result = re.split(r"-|\d{2}\d{3}\d{4},", i[1])
            result1=''.join(result).replace('+','')
            if result1:
                result2 = re.match(r"\d{10}",result1)
                if result2 is not None:
                    contact.append(result2.group())
                    data['Mobile_No']=','.join(contact)
                else:
                    data['Mobile_No']=result1+'not valid number'
        elif '@'in i[1] and '.com' in i[1]:
            data['Email_Address'] = i[1]
        elif '@'not in i[1] and 'com' in i[1] or 'www' in i[1].lower() :
            i[1].lower()
            if 'www' in i[1].lower() or 'WWW' in i[1]:
                data['Website_Url'] = i[1]
            else:
                data['Website_Url'] = 'www.'+i[1]
        elif 'St' in i[1] or re.match(r"\d{3}\s\w",i[1]) or re.match(r"\w+\s\d{6}|\d{6}",i[1]) or re.match('^E.*',i[1]):
            area =area +' '+ i[1]
            if re.findall(r"\b\d{6,7}\b",area):
                address= area.replace(' ,',',')
                address= address.replace(',,',',')
                address= address.replace(';',',')
                if 'global' in address:
                    address= address.replace('St,','')
                    address= address.replace('global','global St,')
                if address:
                    address=address.split(',')
                    data['Area'] = address[0].strip()
                    data['City'] = address[1].strip()
                    if len(address)==3:
                        address=address[2].strip()
                        if address.count(' ')==1:
                            data['State'] = address[:address.index(' ')].strip()
                            data['Pincode'] = int(address[address.index(' ')+1 : ].strip())
                    else:
                        data['State'] = address[2].strip()
                        data['Pincode'] = int(address[3].strip())           
        else:
            companydetails = companydetails + ' ' +i[1]
            if companydetails.strip().count(' '):
                data['Company'] = companydetails.strip()
                data['Category'] = data['Company'][data['Company'].index(' '):].strip()

    return data


def To_Create_table():
    try:
        mycursor.execute("CREATE DATABASE IF NOT EXISTS bizcard;")
        db.commit()
        mycursor.execute("""CREATE TABLE IF NOT EXISTS bizcard_details(
                            Name VARCHAR(250),
                            Designation VARCHAR(250),
                            Email_Address VARCHAR(250) PRIMARY KEY,
                            Area VARCHAR(250),
                            City VARCHAR(250),
                            State VARCHAR(250), 
                            Pincode INT,
                            Mobile_No VARCHAR(250),
                            Website_Url VARCHAR(250),
                            Company VARCHAR(250),
                            Category VARCHAR(250),
                            Business_Card_Image_base64 LONGTEXT);""")
        db.commit()
        return 'Table Created!'
    except Exception as e:
        return e
To_Create_table()

def To_Insert_MYSQL_Table(insert_values):
    # for value in insert_values:
    query=f"""INSERT INTO bizcard_details
            (Name, Designation, Email_Address, Area, City, State, Pincode, Mobile_No, Website_Url, Company, Category, Business_Card_Image_base64) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            Name = VALUES(Name),
            Designation = VALUES(Designation),
            Area = VALUES(Area),
            City = VALUES(City),
            State = VALUES(State),
            Pincode = VALUES(Pincode),
            Mobile_No = VALUES(Mobile_No),
            Website_Url = VALUES(Website_Url),
            Company = VALUES(Company),
            Category = VALUES(Category),
            Business_Card_Image_base64 = VALUES(Business_Card_Image_base64);"""
    mycursor.executemany(query,insert_values)
    db.commit()
    return 'Successfully Inserted!'
reader = easyocr.Reader(['en'])

st.set_page_config(
    page_title="Business Card Data Extracting",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    selected = option_menu("Menu", ["Home", "Extract Data" ], 
                # icons=["house","graph-up-arrow","bar-chart-line", "exclamation-circle"],
                menu_icon= "menu-button-wide",
                default_index=0,
                )
st.header("Extracting Business Card Data with OCR", divider='rainbow')


if selected == 'Extract Data':
    st.title("Business Card Text Extraction")
    tab1, tab2= st.tabs(['**Single Image Ectraction**','**Multiple Image Ectraction**'],)
    with tab1:
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

        col1, col2 = st.columns([1,1], gap = 'medium')
        if uploaded_file is not None:
            with col1:
                # Display the uploaded image
                st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
                
            with col2:
                img_bytes = uploaded_file.read()
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                result = reader.readtext(img_bytes)

                fig, ax = plt.subplots()
                
                # Open the uploaded image
                img = Image.open(uploaded_file)
                ax.imshow(img)

                # Display the uploaded image      
                for detection in result:
                    points = detection[0]
                    rect = patches.Polygon(points, linewidth=1, edgecolor='b', facecolor='none')
                    ax.add_patch(rect)

                    # Annotate text above the rectangles
                    # x = points[0][0]
                    # y = points[0][1]
                    # ax.text(x, y, detection[1], color='red', va='bottom', ha='left')
                    text_x = max(points, key=lambda x: x[0])[0]  # Get the maximum X-coordinate of the rectangle
                    text_y = (points[0][1] + points[3][1]) / 2  # Calculate Y-coordinate for the text

                    # Annotate text on the right side of the rectangle
                    ax.text(text_x, text_y, detection[1], color='red', va='center', ha='left')

                # Show the plot
                st.pyplot(fig)
                data=To_Data_identification(result)
                data['Business_Card_Image_base64'] = base64_image
                if data:
                    df = pd.DataFrame([data])
                    df["Image"] = df.apply(lambda x: "data:image/png;base64,"+ x["Business_Card_Image_base64"], axis=1)

            st.dataframe(df, column_config={"Image": st.column_config.ImageColumn()})
            sql = st.button('Mysql')
            if sql and data:
                data.pop('Image')
                insert_value = [tuple(data.values())]
                print(type(insert_value), type(insert_value[0]))
                # To_Create_table()
                result =To_Insert_MYSQL_Table(insert_value)
                st.success(result)
 

    with tab2:
        uploaded_files = st.file_uploader("Upload multiple images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

        if uploaded_files is not None:
            col3, col4 = st.columns(2)

            with col3:
                for uploaded_file in uploaded_files:
                    st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

            with col4:
                data_list = []

                for uploaded_file in uploaded_files:
                    img_bytes = uploaded_file.read()
                    base64_image = base64.b64encode(img_bytes).decode('utf-8')
                    result = reader.readtext(img_bytes)
                    fig, ax = plt.subplots()
                    img = Image.open(uploaded_file)
                    ax.imshow(img)

                    for detection in result:
                        points = detection[0]
                        rect = patches.Polygon(points, linewidth=1, edgecolor='b', facecolor='none')

                        text_x = max(points, key=lambda x: x[0])[0]
                        text_y = (points[0][1] + points[3][1]) / 2

                        ax.add_patch(rect)
                        ax.text(text_x, text_y, detection[1], color='red', va='center', ha='left')

                    st.pyplot(fig)

                    # Extract text data for each image
                    data = To_Data_identification(result)
                    data['Business_Card_Image_base64'] = base64_image
                    data_list.append(data)

                df = pd.DataFrame(data_list)
            if len(data_list):

                df["Image"] = df.apply(lambda x: "data:image/png;base64,"+ x["Business_Card_Image_base64"], axis=1)

                st.dataframe(df, column_config={"Image": st.column_config.ImageColumn()})
                sql = st.button('Mysql ')
                if sql and not df.empty:
                    df = df.drop('Image', axis = 1)
                    insert_values = df.to_records(index = False)
                    insert_values = insert_values.tolist()
                    # To_Create_table()
                    result = To_Insert_MYSQL_Table(insert_values)
                    st.success(result)

