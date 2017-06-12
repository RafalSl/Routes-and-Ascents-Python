# -*- coding: utf-8 -*-
import pymysql
import datetime

class Db:
    def connect(self):
        """Connects to database"""
        #Można dodać pętlę - czy próbować jeszcze raz
        conn_login = input("Podaj login do połączenia z bazą danych: ")
        conn_password = input("Podaj hasło do połączenia z bazą danych: ")  
        try:
            Db.conn = pymysql.connect('localhost', conn_login, conn_password, 'wykaz_p')      
            Db.c = self.conn.cursor()
            print('Połączono z "localhost"')
        except:
            print('Błąd połączenia')
            
    def sql_fetch(self, sql):
        try:
            Db.c.execute(sql)
            return Db.c.fetchall()
        except:
            print('Nie można pobrać danych z bazy.')
            
    def sql_insert(self, sql):
        try:
            Db.c.execute(sql)
            Db.conn.commit()
            print('Dodano nowy wpis do bazy')
        except:
            print('Błąd. Nie można dodać rekordu')
    
    def sql_insertFormat(self, string):
        if string is '':
            string = 'null'
        else:
            string = ("{0}{1}{0}".format("'", string))
        return string
    
    def sql_insertDate(self):
        while True:
            data = input("Podaj datę przejścia (YYYY-MM-DD): ")
            try:
                datetime.datetime.strptime(data, '%Y-%m-%d')
                break            
            except:
                if data == '':
                    break
                else:
                    print("Błąd!\nPodaj datę w prawidłowym formacie (YYYY-MM-DD) lub pozostaw puste pole.\n")
        data = self.sql_insertFormat(data)
        return data
    
class Login(Db):
    """Login and access control"""
    def __init__(self):
        Db.conn = None
        self.connect()
        if Db.conn:
            self.access()       
            
    def login(self):
        self.user = input('Podaj login: ')
        self.password = input('Podaj hasło: ')       
            
    def access(self):
        """Checks username, password and privileges, then grants user access to database"""
        if self.password_check() == True:
            if self.uprawnienia_db == "001":
                print('Witaj %s! (user)' % self.username_db)
                u1 = User()
                u1.mainMenu()
            elif self.uprawnienia_db == "011":
                print('Witaj %s! (admin)' % self.username_db)
                u1 = Admin()
                u1.mainMenu()
            else:
                self.pass_fail() #Tymczasowo - przydałby się inny komunikat
    
    def password_check(self):
        i = 3
        while i > 0: 
            try:
                self.login()
                i -= 1
                sql = ("select user_id, username, password, uprawnienia from user where username = '%s'" % self.user)
                Db.c.execute(sql)
                result = Db.c.fetchall()
                for res in result:
                    Db.user_id = res[0]
                    self.username_db = res[1]
                    self.password_db = res[2]
                    self.uprawnienia_db = res[3]
                if (self.password == self.password_db) and (self.user == self.username_db) == True:
                    print('Dostęp do bazy')
                    return True
                print('Niepoprawny login lub hasło (zostało prób: %i)' % i)
            except:
                print('Niepoprawny login lub hasło (zostało prób: %i)' % i)
        return False      
    
    def pass_fail(self):
        print('Brak dostępu')
        Db.conn.close()
        print('Rozłączono z "localhost"')   
    
class Menu(Db):
    
    def mainMenu(self):
        print("""
----=== Menu ===----
1 : zobacz swoje przejścia
2 : dodaj nowe przejście
3 : edytuj swoje dane (nie zaimplementowane - wyświetla menu i kończy działanie programu)
q : wyjście z programu
                """)
        while True:
            dictMain = { "1" : self.showAscents, "2" : self.country, "3" : self.persInfoMenu, 'q' : 'q'}
            choice = input()
            chosen = dictMain.get(choice)
            if chosen and chosen != 'q':
                chosen()
                break
            elif chosen == 'q':
                confirm = input("Czy na pewno wyjść z programu? (t/n)")
                if (confirm == 't' or confirm == 'T'):
                    Db.conn.close()
                    print('Rozłączono z "localhost"')
                    raise SystemExit(0)
                else:
                    continue
            else:
                print("\nBłędny wybór Spróbuj jeszcze raz.\n")    

    def createMenu(self, sql, level, edit):
        """Creates dictionaries with ascending numbers as keys and names from database as values (dictMenuPrint for printing) and ID's (dictMenuChoice for navigating by ID's).
        It's size depends on no. of entries fetched from the DB."""
        self.result = self.sql_fetch(sql)
        self.dictMenuPrint = dict(edit)
        self.dictMenuChoice = dict(edit)
        i = 1
        for res in self.result:
            self.dictMenuPrint[str(i)] = res[1]
            self.dictMenuChoice[str(i)] = res[0]
            i += 1
        self.dictMenuPrint['q'] = 'Wyjście poziom wyżej'
        self.dictMenuChoice['q'] = 'Wyjście poziom wyżej'
        if level == 'indoorRoutes' or level == 'ascents':
            self.dictMenuPrint['a'] = 'add'
            self.dictMenuChoice['a'] = 'add'
    
    def printMenu(self, level):
        if level == 'tree':
            if self.result is ():
                print("--- Brak wpisów w tej kategorii ---")
            for key, value in self.dictMenuPrint.items():
                print(key, ':', value)          
        elif level == 'indoorRoutes':
            i = 1
            print("%-5s%-25s%-7s%s" % ('', 'Nazwa drogi', 'Wycena', 'Liczba przejść'))
            if self.result is ():
                print("--- Brak wpisów w tej kategorii ---")
            for key, value in self.dictMenuPrint.items():
                if (key != 'q' and key != 'a' and key != 0):
                    print("%-3s: %-25s%-7s%s" % (key, value, self.result[i-1][2], self.result[i-1][3]))
                    i += 1
            print("")
            print('Wybierz numer drogi, którą przeszedłeś i chcesz ją dodać do swojej bazy przejść lub:')
            print('a : Dodaj nową drogę')
            print('q : Wyjście poziom wyżej')
        elif level == 'ascents':
            i = 0
            print("%5s%-30s%-10s%-25s%-15s%-10s%-6s%-5s%-6s%s" % ('', 'Nazwa drogi', 'Wycena', 'Ściana', 'Kraj', 'Data', 'Styl', 'Waga', 'Ocena', 'Komentarz'))
            if self.result is ():
                print("--- Brak wpisów w tej kategorii ---"            )
            for key, value in self.dictMenuPrint.items():
                if (key != 'q' and key != 'a'):
                    print("%-2s : %-30s%-10s%-25s%-15s%-12s%-6s%-5s%-6s%s" % (key, value, self.result[i][2], self.result[i][4], self.result[i][5], self.result[i][3], self.result[i][6], self.result[i][7], self.result[i][8], self.result[i][9]))
                    i += 1
            print("")
            print('a : Dodaj nowe przejście')
            print('q : Wyjście poziom wyżej')
              
    def choiceMenu(self, level):
        """Allows user to pick an option and validate his choice"""
        while True:
            self.printMenu(level)
            choice = input()
            chosenID = self.dictMenuChoice.get(choice)
            chosenName = self.dictMenuPrint.get(choice)
            if chosenID: 
                return (chosenID, chosenName)
            else:
                print("\nBłędny wybór Spróbuj jeszcze raz.\n")
    
        
    def persInfoMenu(self):
        print("""
----=== O Tobie ===----
1 : zmień wagę
2 : zmień ksywę 
q : wyjście do głównego menu
                """)


class User(Menu):
    global style
    global oceny
    global skale
    style = ('FL', 'PP', 'TR', 'RK', 'AF', '')
    oceny = ('1', '2', '3', '4', '5', '')
    skale = ('uiaa', 'fr', 'kurtyki', 'usa')
    
    """Following methods - country, city, gym, indoorRoutes allow user to navigate through tables"""
    def country(self, edit = ()):
        sql = ("select kraj_id, nazwa_kraju from kraj order by nazwa_kraju")
        level = 'tree'
        print("Wyberz kraj:")
        self.createMenu(sql, level, edit)
        choice = self.choiceMenu(level)
        if choice[0] == "Wyjście poziom wyżej":
            self.mainMenu()
        elif choice[0] == "Edytuj wpisy":
            print("Edycja wspisów")
        else:
            print("Wybierz miasto z kraju", choice[1])
            self.countryID = choice[0]
            self.city(self.countryID)
    
    def city(self, countryID, edit = ()):
        sql = ("select miasto_id, nazwa_miasta from miasto where kraj_id = '%i' order by nazwa_miasta" % self.countryID)
        level = 'tree'
        self.createMenu(sql, level, edit)
        choice = self.choiceMenu(level)
        if choice[0] == "Wyjście poziom wyżej":
            self.country()
        elif choice[0] == "Edytuj wpisy":
            print("Edycja wspisów")
        else:
            print("Wybierz ścianę z miasta", choice[1])
            self.cityID = choice[0]            
            self.gym(self.cityID)
            
    def gym(self, cityID, edit = ()):
        sql = ("select sciana_id, nazwa_sciany from sciana where miasto_id = '%i' order by nazwa_sciany" % self.cityID)
        level = 'tree'
        self.createMenu(sql, level, edit)
        choice = self.choiceMenu(level)
        if choice[0] == "Wyjście poziom wyżej":
            self.city(self.cityID)
        elif choice[0] == "Edytuj wpisy":
            print("Edycja wspisów")
        else:
            print("Wybierz drogę na ścianie", choice[1])
            self.gymID = choice[0]            
            self.indoorRoutes(self.gymID)
    
    def indoorRoutes(self, gymID, edit = ()):
        sql = ("""select droga_p.droga_p_id, droga_p.nazwa_drogi_p, 
(case 
when droga_p.skala_p = 'uiaa' then wyceny.uiaa
when droga_p.skala_p = 'fr' then wyceny.fr 
when droga_p.skala_p = 'kurtyki' then wyceny.kurtyki
else wyceny.usa
end) as 'Wycena',
droga_p.l_przejsc_p,
sciana.nazwa_sciany
from droga_p left join wyceny on droga_p.wycena_p = wyceny.wycena
natural left join sciana where droga_p.sciana_id = '%i' order by droga_p.nazwa_drogi_p""" % self.gymID)
        level = 'indoorRoutes'
        self.createMenu(sql, level, edit)
        choice = self.choiceMenu(level)
        if choice[0] == "Wyjście poziom wyżej":
            self.gym(self.cityID)
        elif choice[0] == "add":
            print("Dodawanie nowej drogi")
            self.addRoute()
        else:
            print("Edycja drogi o nazwie", choice[1])
            inRouteID = choice[0]
            self.addAscent(inRouteID)
            
    def addRoute(self):
        nazwa = input("Podaj nazwę: ")
        wycena = input("Podaj wycenę: ")
        while True:
            skala = input("Podaj skalę " + str(skale))
            if skala in skale:
                break
        sql = ("""INSERT INTO wykaz_p.droga_p (sciana_id, nazwa_drogi_p, wycena_p, skala_p, l_przejsc_p) VALUES ('%s', '%s', '%s', '%s', '0')""" %(self.gymID, nazwa, wycena, skala))
        print(sql)
        self.sql_insert(sql)
        self.indoorRoutes(self.gymID)
    
    def addAscent(self, rid):
        sql = ("""select droga_p.droga_p_id, droga_p.nazwa_drogi_p, 
(case 
when droga_p.skala_p = 'uiaa' then wyceny.uiaa
when droga_p.skala_p = 'fr' then wyceny.fr 
when droga_p.skala_p = 'kurtyki' then wyceny.kurtyki
else wyceny.usa
end) as 'Wycena',
droga_p.l_przejsc_p,
sciana.nazwa_sciany
from droga_p left join wyceny on droga_p.wycena_p = wyceny.wycena
natural left join sciana where droga_p.droga_p_id = '%i'""" % rid)
        result = self.sql_fetch(sql)
        print("Dodajesz przejście do drogi", result[0][1], "(wycena:" + result[0][2] + ") na ścianie:", result[0][4] + ". Dotychczasowa liczba przejść:", result[0][3])
        data = self.sql_insertDate()  
        while True:
            styl = input("Styl przejścia " + str(style))
            if styl in style:
                styl = self.sql_insertFormat(styl) 
                break
        while True:       
            ocena = input("Twoja ocena tej drogi " + str(oceny))
            if ocena in oceny:
                ocena = self.sql_insertFormat(ocena)                
                break
        sql = ("select waga from wspinacz where wspinacz_id = '%i'" % Db.user_id)
        waga = self.sql_fetch(sql)[0][0]
        komentarz = input("Dodaj opcjonalny komentarz do drogi/przejścia: ")
        komentarz = self.sql_insertFormat(komentarz) 
        sql = ("INSERT INTO przejscia_p (wspinacz_id_p, data_pp, droga_p_id, styl, ocena_p, komentarz_p, waga_pp) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6})".format(Db.user_id, data, rid, styl, ocena, komentarz, waga))
        self.sql_insert(sql)
        input("Naciśnij dowolny klawisz")
        self.mainMenu()
    
    def showAscents(self, edit = ()):
        sql = ("""
select przejscia_p.przejscia_p_id, droga_p.nazwa_drogi_p, droga_p.wycena_p, przejscia_p.data_pp, sciana.nazwa_sciany, kraj.nazwa_kraju, przejscia_p.styl, przejscia_p.waga_pp, przejscia_p.ocena_p, przejscia_p.komentarz_p from przejscia_p natural left join droga_p natural left join sciana natural left join miasto natural left join kraj left join wspinacz on przejscia_p.wspinacz_id_p = wspinacz.wspinacz_id where przejscia_p.wspinacz_id_p = '%i' order by przejscia_p.data_pp""" % Db.user_id)
        level = 'ascents'
        self.createMenu(sql, level, edit)
        choice = self.choiceMenu(level)
        if choice[0] == "Wyjście poziom wyżej":
            self.mainMenu()
        elif choice[0] == "add":
            print("Dodawanie nowego przejścia")
            self.country()
        else:
            print("Wybrano edycję przejścia na drodze",choice[1], "ID:", choice[0])
            print("Funkcja czeka na implementację")
            self.mainMenu()
        
class Admin(User):
    global edit 
    edit = [('0','Edytuj wpisy - nie zaimplementowane')]
    
    def country(self):
        super().country(edit)
        
    def city(self, countryID):
        super().city(self.countryID, edit)  
    
    def gym(self, cityID):
        super().gym(self.cityID, edit)

start = Login()