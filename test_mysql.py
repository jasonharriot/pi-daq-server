import mysql.connector
import adam6200
import pi_daq_db
import fetch_df


db = pi_daq_db.PiDAQDB()

res = db.execute('show databases')

print('Databases available:')
for row in res:
    print(row)

#db.commit()

df_columns = fetch_df.fetch_columns(db)
print('Columns available:')
print(df_columns)

df = fetch_df.fetch_df_hours(db, 1, 100)
print('Data table:')
print(df)

print('Done.')
