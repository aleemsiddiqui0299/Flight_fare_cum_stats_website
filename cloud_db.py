import ibm_db
import pandas as pd
import ibm_db_dbi


#my cloud database parameters
#Enter your credentials from IBM_D2B account
dsn_hostname = "0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud"
dsn_uid = "lmg03226"
dsn_pwd = "RVH1zLCHRTUB0A6p"

dsn_driver = "{IBM DB2 ODBC DRIVER}"
dsn_database = "bludb"
dsn_port = "31198"
dsn_protocol = "TCPIP"
dsn_security = "SSL"


#forming the connection string from above parameters
dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY={7};").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd,dsn_security)


# def recreate(conn):
#     dropQuery = "DROP TABLE CONTACTS"
#     dropSt = ibm_db.exec_immediate(conn, dropQuery)
#     createQuery = "CREATE TABLE CONTACTS(PHNO VARCHAR(20) PRIMARY KEY NOT NULL, FNAME VARCHAR(40), EMAIL_ID VARCHAR(40))"
#     createSt = ibm_db.exec_immediate(conn, createQuery)
#


def add_entries(name, phno, email):
    try:
        conn = ibm_db.connect(dsn, "", "")
        print("Connected to database: ", dsn_database, "as user: ", dsn_uid, "on host: ", dsn_hostname)

    except:
        print("Unable to connect: ", ibm_db.conn_errormsg())
        return "Not connected"

    insertQuery = "INSERT INTO CONTACTS VALUES('"+phno+"','"+name+"', '" + email+"' )"
    insertSt = ibm_db.exec_immediate(conn, insertQuery)
    ibm_db.close(conn)
    return "connected"




