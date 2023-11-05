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
# To_Create_table()

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
# reader = easyocr.Reader(['en'])

st.set_page_config(
    page_title="Business Card Data Extracting",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    selected = option_menu("Menu", ["Home", "Extract Data", "Modify Data", "Delete Data", "Direct MYSQL Query" ], 
                # icons=["house","graph-up-arrow","bar-chart-line", "exclamation-circle"],
                icons=['house', 'cloud-upload','graph-up-arrow', "recycle", 'search'], 
                menu_icon= "cast",
                default_index=0,
                )
st.header("Extracting Business Card Data with OCR", divider='rainbow')


if selected == 'Extract Data':
    st.title("Business Card Text Extraction")
    tab1, tab2= st.tabs(['**Single Image Extraction**','**Multiple Image Extraction**'])
    with tab1:
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

        col1, col2 = st.columns([1,1], gap = 'medium')
        if uploaded_file is not None:
            with col1:
                # Display the uploaded image
                st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
                
            with col2:
                reader = easyocr.Reader(['en'])
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
                reader = easyocr.Reader(['en'])
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

elif selected == 'Modify Data':
    st.header('Update')
    mycursor.execute("""SELECT DISTINCT(Email_Address) FROM bizcard_details;""")
    Email = mycursor.fetchall()
    Email_Address = st.selectbox('***Select the Email Address To Update the Details***',[ email[0] for email in Email])


    mycursor.execute (f"""SELECT Business_Card_Image_base64 FROM bizcard_details WHERE Email_Address = '{Email_Address}';""")
    Business_Card_Image_base64 = mycursor.fetchall()
    image_data = base64.b64decode(str(Business_Card_Image_base64).split(',')[0])

    # # Convert the image data to bytes
    image_bytes = BytesIO(image_data)

    # Open the image using Pillow
    img = Image.open(image_bytes)
    st.image(img, width= 500)

    mycursor.execute(f"""SELECT Name, Designation, Area, City, State, Pincode, Mobile_No, Website_Url, Company, Category FROM bizcard_details
                      WHERE Email_Address = '{Email_Address}';""")
    details = mycursor.fetchall()
    details_df =pd.DataFrame(details, columns = [i[0] for i in mycursor.description])

    Name = st.text_input(details_df.columns[0], details_df[details_df.columns[0]].iloc[0] )
    Designation = st.text_input(details_df.columns[1], details_df[details_df.columns[1]].iloc[0] )
    Area = st.text_input(details_df.columns[2], details_df[details_df.columns[2]].iloc[0] )
    City = st.text_input(details_df.columns[3], details_df[details_df.columns[3]].iloc[0] )
    State = st.text_input(details_df.columns[4], details_df[details_df.columns[4]].iloc[0] )
    Pincode = st.number_input(details_df.columns[5], details_df[details_df.columns[5]].iloc[0] )
    Mobile_No = st.text_input(details_df.columns[6], details_df[details_df.columns[6]].iloc[0] )
    Website_Url = st.text_input(details_df.columns[7], details_df[details_df.columns[7]].iloc[0] )
    Company = st.text_input(details_df.columns[8], details_df[details_df.columns[8]].iloc[0] )
    Category = st.text_input(details_df.columns[9], details_df[details_df.columns[9]].iloc[0] )
    # st.dataframe(details_df)
    # st.write(Name, Designation, Area, City, State, Pincode, Mobile_No, Website_Url, Company, Category)
    st.markdown('***To Click Below Button To Update***')
    update= st.button('Update')
    if update and Name and Designation and Area and City and State and Pincode and Mobile_No and Website_Url and Company and Category and Email_Address:
        query = f"""UPDATE bizcard_details
                    SET Name = '{Name}', 
                        Designation = '{Designation}', 
                        Area = '{Area}',
                        City = '{City}',
                        State = '{State}',
                        Pincode = {Pincode},
                        Mobile_No = '{Mobile_No}',
                        Website_Url = '{Website_Url}',
                        Company = '{Company}',
                        Category = '{Category}'
                    WHERE Email_Address = '{Email_Address}';"""
        mycursor.execute(query)
        db.commit()
        st.success('Successfully Updated!')
        mycursor.execute(f"""SELECT Name, Designation, Area, City, State, Pincode, Mobile_No, Website_Url, Company, Category FROM bizcard_details
                      WHERE Email_Address = '{Email_Address}';""")
        updated_details = mycursor.fetchall()
        updated_details_df =pd.DataFrame(updated_details, columns = [i[0] for i in mycursor.description])
        st.dataframe(updated_details_df)

elif selected == "Delete Data":
    st.header('Delete')
    st.markdown('The below dataframe shows the stored Bizcard details')

    mycursor.execute(f"""SELECT * FROM bizcard_details;""")
    stored_data = mycursor.fetchall()
    data_df =pd.DataFrame(stored_data, columns = [i[0] for i in mycursor.description])
    st.dataframe(data_df)

    mycursor.execute("""SELECT DISTINCT(Email_Address) FROM bizcard_details;""")
    Email = mycursor.fetchall()
    Email_address = st.selectbox('***Select the Email Address To Update the Details***',[ email[0] for email in Email])

    delete = st.button('DELETE')

    if delete and Email_address:
        mycursor.execute (f"""DELETE FROM bizcard_details WHERE Email_Address = '{Email_address}';""")
        db.commit()
        st.success('Deleted!')

elif selected == "Direct MYSQL Query":
    tab3, tab4 = st.tabs(['Retrieve Data', 'Retrieve Image'])
    with tab3:
        query = st.text_area('**Enter your own query**', 'SELECT * FROM bizcard_details')
        # query = query.lower()
        result = st.button( "Retrieve Data")
        if result == False:
            mycursor.execute("DESCRIBE bizcard_details")
            data1 = mycursor.fetchall()
            
            st.write("""Refer to the below tables for guidance, where title is represented as the table name,
                        and their corresponding column names are provided as row values.""")
            st.header(':blue[bizcard_details]')
            data1 = [i[0] for i in data1]
            st.dataframe(pd.DataFrame(data1, columns = ['Column Name']))  
        elif result == True:
            query1 = query.lower()
            if 'select' in query1:
                try:
                    mycursor.execute(query)
                    data = mycursor.fetchall()
                    df = pd.DataFrame(data, columns = [i[0] for i in mycursor.description])
                    if "Business_Card_Image_base64" in df.columns:
                        df["image"] = df.apply(lambda x: "data:image/png;base64,"+ x["Business_Card_Image_base64"], axis=1)
                        new_order = ['image'] + [col for col in df.columns if col != 'image']
                        df = df[new_order]
                        st.dataframe(df, column_config={"image": st.column_config.ImageColumn()})
                    else:
                        st.dataframe(df)
                except Exception as e:
                    st.exception(e)
            else:
                st.warning('Access Denied', icon="⚠️")
    with tab4:
        mycursor.execute("""SELECT DISTINCT(Email_Address) FROM bizcard_details;""")
        Email = mycursor.fetchall()
        email_address = st.selectbox('***Select the Email Address To Read the Business Card***',[ email[0] for email in Email])

        mycursor.execute (f"""SELECT Business_Card_Image_base64 FROM bizcard_details WHERE Email_Address = '{email_address}';""")
        Business_Card_Image_base64 = mycursor.fetchall()
        image_data = base64.b64decode(str(Business_Card_Image_base64).split(',')[0])

        # # Convert the image data to bytes
        image_bytes = BytesIO(image_data)

        # Open the image using Pillow
        img = Image.open(image_bytes)
        st.image(img, width= 500)
        st.markdown('Click ***Download BizCard*** button to download the Business card image')
        btn = st.download_button(
        label="Download BizCard",
        data=image_bytes,
        file_name="BizCard.png",
        mime="image/png"
        )

elif selected == 'Home':
    col5, col6 = st.columns(2, gap = 'small')
    with col6:
        image= Image.open(r'overview.png')
        st.image(image)
    with col5:
        st.header('Overview:')
        st.markdown(""" The Streamlit app helps users upload business card images, extracting key details such as company name, holder name, 
                    contact, and location using easyOCR. The app also lets users save this data and the uploaded images into a database. 
                    It operates using Python, Streamlit, easyOCR, and databases like SQLite or MySQL, providing a straightforward user interface 
                    for smooth image uploads and data extraction. The collected info is neatly displayed, and users can effortlessly add, read, 
                    update, and delete the data directly through the Streamlit app. This project demands expertise in image processing, OCR, GUI 
                    development, and database management, emphasizing scalable, maintainable, and well-documented architecture.""")
    st.header('User Guide')
    st.markdown('### ***Extract Data***')
    st.markdown(""" - ***Single Image Extract:*** Upload a single image to extract text data.
                    \n- ***Multi-Image Extract:*** Upload multiple images to extract text data.""")
    st.markdown('### ***Modify Data***')
    st.markdown(""" - Choose the email address to update stored information in MySQL.""")
    st.markdown('### ***Delete Data***')
    st.markdown(""" - Select the email address to remove stored information.""")
    st.markdown('### ***Direct MYSQL Query***')
    st.markdown('#### ***Retrieve Data:***')
    st.markdown(""" - ***Function:*** Allows users to write custom queries and analyze the relevant table columns.
                  \n- ***Usage:*** Write SQL queries in the given input area to retrieve specific information from the database table.
                  \n- ***Table Column Reference:*** For reference, a list of table column names will be provided to help construct accurate SQL queries..""")
    st.markdown('#### ***Retrieve Data:***')
    st.markdown(""" - ***Function:*** Permits users to view stored images and download them based on Email addresses.
                    \n- ***Usage:*** Select an Email address to view the associated image stored in the database.
                    \n- ***Action:*** Provides an option to download the image for the chosen Email address.""")