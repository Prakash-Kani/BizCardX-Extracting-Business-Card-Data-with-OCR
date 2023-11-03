import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import pandas as pd 
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image



lst=[]
def To_Data_identification(a):
    data={}
    area =''
    address=''
    contact=[]
    companydetails=''
    for i in a:
        if a.index(i)==0:
            data['Name'] = i[1]
        elif a.index(i)==1:
            data['Role'] = i[1]
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
            data['Email'] = i[1]
        elif '@'not in i[1] and 'com' in i[1] or 'www' in i[1].lower() :
            # print(i[1])
            i[1].lower()
            if 'www' in i[1].lower() or 'WWW' in i[1]:
                data['Website'] = i[1]
            else:
                data['Website'] = 'www.'+i[1]
        elif 'St' in i[1] or re.match(r"\d{3}\s\w",i[1]) or re.match(r"\w+\s\d{6}|\d{6}",i[1]) or re.match('^E.*',i[1]):
            # print(n,i[1])
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
                            data['Pincode'] = address[address.index(' ')+1 : ].strip()
                    else:
                        data['State'] = address[2].strip()
                        data['Pincode'] = address[3].strip()            
        else:
            companydetails = companydetails + ' ' +i[1]
            if companydetails.strip().count(' '):
                data['Company'] = companydetails.strip()
                data['Category'] = data['Company'][data['Company'].index(' '):].strip()

    return data

reader = easyocr.Reader(['en'])

st.set_page_config(
    page_title="Business Card Data Extracting",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    selected = option_menu("Menu", ["Home", "Single", "Multi" ], 
                # icons=["house","graph-up-arrow","bar-chart-line", "exclamation-circle"],
                menu_icon= "menu-button-wide",
                default_index=0,
                )
st.header("Extracting Business Card Data with OCR", divider='rainbow')


if selected == 'Single':
    st.title("Business Card Text Extraction")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

    col1, col2 = st.columns([1,1], gap = 'medium')
    with col1:
        if uploaded_file is not None:
        # Display the uploaded image
            st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

            img_bytes = uploaded_file.read()
            # reader = easyocr.Reader(['en'])
            # Use easyocr to extract text from the image
            result = reader.readtext(img_bytes)
    with col2:
        fig, ax = plt.subplots()
        
        # Open the uploaded image
        img = Image.open(uploaded_file)

        # Display the uploaded image
        ax.imshow(img)
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
        extract= st.button('Extract Text')
        if extract:
            data=To_Data_identification(result)
            st.write(data)
# elif selected == 'Multi':
#     st.title("Business Cards Text Extraction")
#     uploaded_files = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
#     col3, col4= st.columns([1,1], gap = 'medium')
#     if uploaded_files is not None:
#         with col3:
#             # if uploaded_files is not None:
#             # Display the uploaded image
#             for uploaded_file in uploaded_files:
#                 st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

#                 # img_bytes = uploaded_file.read()
#                 # # reader = easyocr.Reader(['en'])
#                 # # Use easyocr to extract text from the image
#                 # result = reader.readtext(img_bytes)
#         with col4:
#             data_list=[]
#             for uploaded_file in uploaded_files:
#                 img_bytes = uploaded_file.read()
#                 result = reader.readtext(img_bytes)
#                 fig, ax = plt.subplots()
                
#                 # Open the uploaded image
#                 img = Image.open(uploaded_file)

#                 # Display the uploaded image
#                 ax.imshow(img)
#                 for detection in result:
#                     points = detection[0]
#                     rect = patches.Polygon(points, linewidth=1, edgecolor='b', facecolor='none')

#                 text_x = max(points, key=lambda x: x[0])[0]  # Get the maximum X-coordinate of the rectangle
#                 text_y = (points[0][1] + points[3][1]) / 2  # Calculate Y-coordinate for the text

#                 # Annotate text on the right side of the rectangle
#                 ax.text(text_x, text_y, detection[1], color='red', va='center', ha='left')

#             # Show the plot
#                 st.pyplot(fig)
#                 data = To_Data_identification(result)
#                 data_list.append(data)
# #         # extract= st.button('Extract Text')
# #         # with col3:
# #         lst=[]
# #         for uploaded_file in uploaded_files:
# #             img_bytes = uploaded_file.read()
# #             result = reader.readtext(img_bytes)
# #             data=To_Data_identification(result)
# #             lst.apped(data)
#         if len(data_list):
#             df = pd.DataFrame(data_list)
#             st.dataframe(df)

elif selected == 'Multi':
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
                data_list.append(data)

            df = pd.DataFrame(data_list)
        if len(data_list):
            st.dataframe(df)
