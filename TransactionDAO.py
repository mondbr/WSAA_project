# Transaction dao 
# a data layer that connects to a datbase
# this code was mostly written based on the book dao code by Andrew Beatty in WSAA course

import mysql.connector
import dbconfig as cfg

class TransactionDAO:
      connection = ""
      cursor = ''
      host = ''
      user = ''
      password = ''
      database = ''
   
      def __init__(self):
         self.host = cfg.mysql['host']
         self.user = cfg.mysql['user']
         self.password = cfg.mysql['password']
         self.database = cfg.mysql['database']
   
      def get_cursor(self):
         self.connection = mysql.connector.connect(
               host=self.host,
               user=self.user,
               password=self.password,
               database=self.database,
         )
         self.cursor = self.connection.cursor()
         return self.cursor
      
      def close_all(self):
         self.connection.close()
         self.cursor.close()
      
      def get_all(self):
         cursor = self.get_cursor()
         sql = "select * from transaction"
         cursor.execute(sql)
         results = cursor.fetchall()
         transactions = []
         #print(results)
         for result in results:
            #print(result)
            transactions.append(self.convert_to_dictionary(result))
         
         self.close_all()
         return transactions
      
      def find_by_id(self, id):
         cursor = self.get_cursor()
         sql = "select * from transaction where id = %s"
         values = (id,)
   
         cursor.execute(sql, values)
         result = cursor.fetchone()
         transaction = self.convert_to_dictionary(result)
         self.close_all()
         return transaction
      
      def create(self, transaction):
         cursor = self.get_cursor()
         sql = "insert into transaction (description, amount, transaction_type) values (%s, %s, %s)"
         values = (transaction.get('description'), transaction.get('amount'), transaction.get('transaction_type'))
         cursor.execute(sql, values)

         self.connection.commit()
         # https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-lastrowid.html auto increment id
         new_id = cursor.lastrowid
         transaction['id'] = new_id


         self.close_all()
         return transaction
      
      def update(self, id, transaction):
         cursor = self.get_cursor()
         sql = "update transaction set description = %s, amount = %s, transaction_type = %s where id = %s"
         values = (transaction.get('description'), transaction.get('amount'), transaction.get('transaction_type'), id)
         cursor.execute(sql, values)
         self.connection.commit()
         self.close_all()
      
      def delete(self, id):
         cursor = self.get_cursor()
         sql = "delete from transaction where id = %s"
         values = (id,)
         cursor.execute(sql, values)
         self.connection.commit()
         self.close_all()

         print("delete done")

      def convert_to_dictionary(self, result_line):
         transaction_keys = ['id', 'description', 'amount', 'transaction_type']
         transaction = {}
         
         for key in range(len(result_line)):
            transaction[transaction_keys[key]] = result_line[key]
            
         return transaction
      # convert_to_dictionary method is used to convert the result of a query into a dictionary format.

TransactionDAO = TransactionDAO()
# This line creates an instance of the TransactionDAO class, allowing  use its methods to interact with the database.
