'''import mysql.connector
conn=mysql.connector.connect(host="localhost",
                             user="root",
                             password="R1a2m3$%^",
                             )
c=conn.cursor()
#c.execute("create database travelDB")
c.execute("show databases")
for i in c:
    print(i)
'''
import pandas as pd
from sqlalchemy import create_engine

# Step 1: Read the Excel file with multiple sheets into a dictionary of DataFrames
file_path = 'D:\Python_Intern_project\project_python.xlsx'  # Update this to the correct path if necessary
sheets_dict = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')

# Step 2: Connect to the MySQL database
db_user = 'root'      
db_password = 'R1a2m3$%^'  
db_host = 'localhost'         
db_name = 'traveldb'          

connection_string = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
engine = create_engine(connection_string)

# Step 3: Loop through the dictionary and import each DataFrame into the corresponding table
for sheet_name, df in sheets_dict.items():
    table_name = sheet_name  # Use the sheet name as the table name, or change as needed
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"Data imported successfully into table {table_name} in the {db_name} database.")

print("All data imported successfully.")
