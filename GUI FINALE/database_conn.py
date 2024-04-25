import sqlite3

class Comunicazione():
    def __init__(self):
        self.connection = sqlite3.connect("dati_utenti.db")

    def inserisci_utente(self, Name, Surname, Age, Gender, Height, Weight, Photo):
        cursor = self.connection.cursor()
        query = '''INSERT INTO tabella_utenti VALUES (:Name, :Surname, :Age, :Gender, :Height, :Weight, :Photo)'''
        cursor.execute(query, {'Name': Name, 'Surname':Surname, 'Age':Age, 'Gender':Gender, 'Height':Height, 'Weight':Weight, 'Photo':Photo})
        self.connection.commit()
        cursor.close()
    
    def mostra_dati(self):
        cursor = self.connection.cursor()
        query = '''SELECT * FROM tabella_dati'''
        cursor.execute(query)
        dati = cursor.fetchall()
        return dati
    
    def mostra_dati_nome(self, Name):
        cursor = self.connection.cursor()
        query = '''SELECT * FROM tabella_dati WHERE Name = ?'''
        cursor.execute(query, (Name,))
        dati = cursor.fetchall()
        return dati
    
    def mostra_dati_nome_cognome(self, Name, Surname):
        cursor = self.connection.cursor()
        query = '''SELECT * FROM tabella_dati WHERE Name = ? AND Surname = ?'''
        cursor.execute(query, (Name,Surname,))
        dati = cursor.fetchall()
        return dati
    
    def inserisci_dati(self, Name, Surname, Steps, Distance, Speed, Calories, Date):
        cursor = self.connection.cursor()
        query = '''INSERT INTO tabella_dati VALUES (:Name, :Surname, :Steps, :Distance, :Speed, :Calories, :Date)'''
        cursor.execute(query, {'Name': Name, 'Surname':Surname, 'Steps':Steps, 'Distance':Distance, 'Speed':Speed, 'Calories':Calories, 'Date':Date})
        self.connection.commit()
        cursor.close()
    
    def cerca_utente(self, Name, Surname):
        cursor = self.connection.cursor()
        query = '''SELECT * FROM tabella_utenti WHERE Name = ? AND Surname=? '''
        cursor.execute(query, (Name, Surname))
        utente = cursor.fetchall()
        cursor.close()
        return utente
    
    def ottieni_utenti(self):
        cursor = self.connection.cursor()
        query = '''SELECT Name, Surname FROM tabella_utenti'''
        cursor.execute(query)
        utenti = cursor.fetchall()
        return utenti
    
    
    def ottieni_utente(self, Name, Surname):
        cursor = self.connection.cursor()
        query = "SELECT * FROM tabella_utenti WHERE Name = '{}' AND Surname = '{}' ".format(Name,Surname)
        cursor.execute(query)
        utenti = cursor.fetchall()
        return utenti
    
    def invia_problema(self, Name, Surname, Mail, Issue, Type):
        cursor = self.connection.cursor()
        query = '''INSERT INTO tabella_assistenza VALUES (:Name, :Surname, :Mail, :Issue, :Type) '''
        cursor.execute(query, {'Name':Name, 'Surname':Surname, 'Mail':Mail, 'Issue':Issue, 'Type':Type})
        self.connection.commit()
        cursor.close()

    
    def aggiorna_utente(self, Name, Surname, Age, Gender, Height, Weight, Photo):
        cursor = self.connection.cursor()
        query = '''UPDATE tabella_utenti SET (Name, Surname, Age, Gender, Height, Weight, Photo) = (?,?,?,?,?,?,?) WHERE (Name, Surname)=(?,?)'''
        cursor.execute(query, (Name, Surname, Age, Gender, Height, Weight, Photo, Name, Surname))
        self.connection.commit()
        cursor.close()
    

