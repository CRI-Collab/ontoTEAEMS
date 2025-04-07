import re
import sqlite3
class DatabaseManager:
    def __init__(self, db_name="know.db"):
        #self.connection = sqlite3.connect(db_name)
        self.connection = sqlite3.connect(db_name, check_same_thread=False)

        self.create_tables()
    
    def create_tables(self):
        cursor = self.connection.cursor()
    
    ###Patterns
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT
        )""")
    
    #### Softgoals
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Softgoals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT
        )""")
    
    ### Patterns <-> Softgoals
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patternId INTEGER,
            softgoalId INTEGER,
            influenceType TEXT,
            reason TEXT,           
            UNIQUE(patternId,softgoalId),
            FOREIGN KEY (patternId) REFERENCES Patterns (id),
            FOREIGN KEY (softgoalId) REFERENCES Softgoals (id)
        )""")

    # User Scores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserScores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patternId INTEGER NOT NULL,
            softgoalId INTEGER NOT NULL,
            influenceType TEXT,
            reason TEXT,
            score INTEGER NOT NULL,
            UNIQUE(patternId, softgoalId),
            FOREIGN KEY (patternId) REFERENCES Patterns(id),
            FOREIGN KEY (softgoalId) REFERENCES Softgoals(id)
        )""")
        self.connection.commit()
    
    #def checkExistingRelations(self, patName, softName, relaType):
    #   cursor = self.connection.cursor()
    #    cursor.execute("""
    #    SELECT 1 FROM Relations
    #    WHERE patternId = (SELECT id FROM Patterns WHERE name = ?)
    #    AND softgoalId = (SELECT id FROM Softgoals WHERE name = ?)
    #    AND relationsType = ?
    #    """, (patName, softName, relaType))
    #    return cursor.fetchone() is not None
    
    #### #### #### INSERT DATA -- ####  ####  #### ####
    def insertPatterns(self, name, description):
        cursor = self.connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO Patterns (name, description) VALUES (?, ?) ", (name, description))
        self.connection.commit()

    def insertSoftgoals(self, name, description):
        cursor = self.connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO Softgoals (name, description) VALUES (?, ?)", (name, description))
        self.connection.commit()

    def insertRelations(self, patName, softName, influenceType, reason):
        cursor = self.connection.cursor()
        cursor.execute("INSERT  OR IGNORE INTO Relations (patternId, softgoalId, influenceType, reason) VALUES (?, ?, ?, ?)",
                    (patName, softName, influenceType, reason))
        self.connection.commit()
    
    def insertScore(self, patName, softName, influenceType, reason, score):
        cursor = self.connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO UserScores (patternId, softgoalId, influenceType , reason, score) VALUES (?, ?, ?, ?, ?)", 
                       (patName, softName, influenceType,reason, score))
        self.connection.commit()

    #### #### #### GET RELATIONS FROM KB  ####  ####  #### ####
    def getScores(self):
        cursor = self.connection.cursor()
        return cursor.execute("SELECT * FROM UserScores").fetchall()

    def getUserScores(self):
        """ Récupère les scores des utilisateurs."""
        cursor = self.connection.cursor()
        return cursor.execute("SELECT user_id, patternId, softgoalId, score FROM UserScores").fetchall()
    
    def getPatternIdByName(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM Patterns WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def getAllPatterns(self):
        cursor = self.connection.cursor()
        return cursor.execute("SELECT name, description FROM Patterns").fetchall()
    
    def getAllSoftgoals(self):
        cursor = self.connection.cursor()
        return cursor.execute("SELECT name, description FROM Softgoals").fetchall()
    
    def getAllUserScores(self):
        cursor = self.connection.cursor()
        return cursor.execute("SELECT patternId, softgoalId, influenceType, reason, score FROM UserScores").fetchall()

    
    def getAllRelations(self):
        cursor = self.connection.cursor()
        return cursor.execute("SELECT patternId, softgoalId, influenceType, reason FROM Relations").fetchall()

    def getPatternsByName(self):
        """Récupère tous les softgoals."""
        cursor = self.connection.cursor()
        return [row[0] for row in cursor.execute("SELECT DISTINCT name FROM Patterns").fetchall()]
    
    def getSoftgoalsByName(self):
        """Récupère tous les softgoals."""
        cursor = self.connection.cursor()
        return [row[0] for row in cursor.execute("SELECT DISTINCT name FROM Softgoals").fetchall()]
    
    def topsisScore(self):
        cursor = self.connection.cursor()
        return cursor.execute("SELECT patternId, softgoalId, score FROM UserScores").fetchall()
    
    def getSoftgoalsForPattern(self, pattern_name):
        """
        Récupère les softgoals liés à un pattern donné.
        """
        query = """
        SELECT DISTINCT s.name 
        FROM Softgoals s
        JOIN Relations r ON s.id = r.softgoalId
        JOIN Patterns p ON p.id = r.patternId
        WHERE p.name = ?;
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (pattern_name,))
        return cursor.fetchall()
        
    def getScoresForPattern(self, pattern_name):
        cursor = self.connection.cursor()
        return cursor.execute("""
        SELECT patternId, softgoalId, influenceType, reason, score 
        FROM UserScores
        WHERE patternId = ?;
        """, (pattern_name,)).fetchall()
    
    def clear_tables(self):
        """Vide les tables de la base de données."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM Patterns;") 
            cursor.execute("DELETE FROM Softgoals;") 
            cursor.execute("DELETE FROM Relations;") 
            cursor.execute("DELETE FROM UserScores;")
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()