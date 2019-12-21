import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QColorDialog, QMessageBox, QCheckBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

#%%     Basic setup for the window
class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Pokemon Dex Tracker'        
        self.setWindowTitle(self.title)
        
        size = app.primaryScreen().availableGeometry() #Get the borders of the screen
        width = size.width()
        height = size.height()
        
#%%     Create Widgets
        
        self.EnterPokemonField = QLineEdit(self)
        self.EnterPokemonField.setGeometry(10, 10, 250, 30)
        
        self.ColorButton = QPushButton(self)
        self.ColorButton.setText('Select Color')
        self.ColorButton.setGeometry(270, 10, 90, 30)
        self.ColorButton.clicked.connect(self.OpenColorDialog)
        
        self.DeleteButton = QPushButton(self)
        self.DeleteButton.setGeometry(370, 10, 20, 30)
        self.DeleteButton.setText('-')
        self.DeleteButton.clicked.connect(self.UnmarkPokemon)
        self.DeleteButton.setToolTip('Unmark a pokemon, or mark a pokemon without it counting towards the total')  
        
        self.DexLoadButton = QPushButton(self)
        self.DexLoadButton.setGeometry(420, 10, 100, 30)
        self.DexLoadButton.setText('Load Pokemon List')
        self.DexLoadButton.clicked.connect(self.StartTracking)
        
        self.CheckBox = QCheckBox(self)
        self.CheckBox.setGeometry(775, 10, 110, 30)
        self.CheckBox.setText('Order by Nat Dex')
        
        Basic_Order = ['National', 'RBY', 'GSC', 'RSE', 'DP', 'Platinum', 'HgSs', 'BW', 'BW2', 'XY', 'OrAs', 'SuMo', 'UsUm', 'Galar']
        self.comboBox = QComboBox(self)
        for x in Basic_Order:
            self.comboBox.addItem(x+' Dex')
        for x in os.listdir(os.path.join('Pokemon Lists')):
            EndPoint = x.index('.')
            name = x[:EndPoint]
            if name[:-4] in Basic_Order:
                continue
            self.comboBox.addItem(name)
        self.comboBox.setGeometry(530, 10, 100, 30)
        self.comboBox.setCurrentIndex(0)
        self.comboBox.activated[str].connect(self.setDexList)
        
        self.PokemonAcrossField = QLineEdit(self)
        self.PokemonAcrossField.setGeometry(640, 10, 40, 30)
        self.PokemonAcrossField.setText(str(int(width/30)))
        self.PokemonAcross = str(int(width/30))
        
        self.InformationLabel = QLabel(self)
        self.InformationLabel.setText('Pokemon Across')
        self.InformationLabel.setGeometry(690, 10, 80, 30)
        
        
        self.ImportPokemonButton = QPushButton(self)
        self.ImportPokemonButton.setGeometry(width -150 -10, 10, 150, 30)
        self.ImportPokemonButton.setText('Import Marked Pokemon')
        self.ImportPokemonButton.clicked.connect(self.ImportMarked)
        
        self.ExportPokemonButton = QPushButton(self)
        self.ExportPokemonButton.setGeometry(width -150 -10 -150 -10, 10, 150, 30)
        self.ExportPokemonButton.setText('Export Marked Pokemon')
        self.ExportPokemonButton.clicked.connect(self.ExportMarked)
        
        
        self.CountLabel = QLabel(self)
        self.CountLabel.setStyleSheet('color: red')
        self.CountLabel.setFont(QFont('Arial', 15))
        self.CountLabel.setText('Total: 0/0')
        self.CountLabel.setGeometry(width-135, height-50, 135, 30)
        self.Count = 0
        
        self.Color = '#000000'
        self.pokemon_sprite = {} #sprites for the pokemon
        self.DexList = 'National Dex.txt' #dex list if no new list is specified
        self.MarkedList_number = [] # Create lists to add numbers/names/colors of marked pokemon
        self.MarkedList_pokemon = []
        self.MarkedList_color = []
        
        
        file = open(os.path.join('Pokemon Lists', 'National Dex.txt'), 'r')
        self.NationalDex = file.readlines()
        file.close()
        self.all_pokemon = []
        for string in self.NationalDex: 
            string_pokemon = string[5:len(string)-1]
            string_pokemon = string_pokemon.capitalize()
            self.all_pokemon.append(string_pokemon)
             
        #Initialize all pokemon
        for x in range(1, 922): 
            self.pokemon_sprite["string{0}".format(x)]= QLabel(self) #Create a label for every pokemon
        

        self.showMaximized()
     
#%%     Creating the functions
    
    
    def keyPressEvent(self, event):
         if event.key() == 16777220:
             try:
                 self.MarkPokemon()
             except:
                 pass
    
    def mousePressEvent(self, event):
        try:
            #Obtain Position where the marking must go
            x = event.x()
            x = 30* int(x/30)
            y = event.y()
            y = 15 + 30* int((y-15)/30)
            
            if y>44 and x<30*self.PokemonAcross: #only Mark pokemon when clicking where there are pokemon
                #Determine what The national Dex Number of the pokemon is
                rows = int((y-15)/30)
                colomn = int(x/30) + 1
                if colomn>self.PokemonAcross:
                    1[2] #Create error to stop
                RegionalDexNumber = self.PokemonAcross * (rows-1) + colomn
                NatDexNumber = self.NatDexNumberList[RegionalDexNumber-1]
                self.EnterPokemonField.setText(self.all_pokemon[NatDexNumber-1])
                
                if event.button() == 1:
                    self.MarkPokemon()
                
                elif event.button() == 2:
                    self.UnmarkPokemon()
        except:
            pass
                
    
    
    
    def OpenColorDialog(self):
        self.Color = QColorDialog.getColor()
        self.Color = self.Color.name()
        
        if self.Color[5] in 'cdef':  #Make sure the color isn't too similar to the color used to negative mark pokemon
            if self.Color[1] in '0123456' and self.Color[3] in '0123456':
                msg = QMessageBox(self)
                msg.setWindowTitle('Color Error')
                msg.setText('The color you entered is too similar to the color used to negative mark pokemon')
                msg.setIcon(QMessageBox.Information)
                
                msg.exec()
                
                self.OpenColorDialog()
        
        if self.Color == '#000000':
            self.ColorButton.setStyleSheet('background-color: %s; color: White' % (self.Color))
            
        else:
            self.ColorButton.setStyleSheet('background-color: %s; color: Black' % (self.Color))
    
    
    
    
    def setDexList(self, text):
        self.DexList = text + '.txt'
    
    
    def ExportMarked(self):
        number = 1
        marked = ''
        for pokemon in self.MarkedList_number:
            if number <len(self.MarkedList_number):
                marked += pokemon + '(' + self.MarkedList_color[number-1] + '), '
            else:
                marked += pokemon + '(' + self.Color + ')'
            
            
            number += 1
        
        self.EnterPokemonField.setText(marked)
    
    def ImportMarked(self):
        oldcolor = self.Color
        
        file = open(os.path.join('Pokemon Lists', 'National Dex.txt'),'r')
        file.close()
        
        pokemonlist = list(self.EnterPokemonField.text())
        pokemonlist.append(',') #This makes it easy to run the last pokemon as well

        #Adding some variables that will be used in this function
        current_pokemon = ''
        colorStarted = False
        
        for i in pokemonlist:
            if i == ' ': #Exclude the spaces, they are only between pokemon for the users convinience
                continue
            elif i == ',':  #Run the mark pokemon using the current pokemon
                
                pokemon_number = ''
                color_name = ''
                
                # Split the string to the pokemon and the color
                for character in current_pokemon:
                   
                    if colorStarted == False:
                        if character == '(':
                            colorStarted = True
                        else:
                            pokemon_number += character
                    
                    elif character == ')':
                        break
                    else:
                        color_name += character
                    
                try:
                    pokemon = int(pokemon_number)
                    pokemon_name = self.NationalDex[pokemon-1][5:len(self.NationalDex[pokemon-1])-1]
                    
                    self.Color = color_name
                    
                    self.EnterPokemonField.setText(pokemon_name)
                    current_pokemon = ''
                    colorStarted = False
                    self.MarkPokemon()
                    
                    self.Color = oldcolor
                except:
                    pass
                
            else:
                current_pokemon += i
    
    def StartTracking(self):
        
        self.Count = 0
        try:
            self.PokemonAcross = int(self.PokemonAcrossField.text())
        except:
            pass
        
        #Clear old Markings
        for number in range(1, len(self.all_pokemon)):
            pass
            self.pokemon_sprite['string'+str(number)].setStyleSheet('background-color: transparent')
        
        self.NatDexNumberList = []
        self.MarkedList_number = []
        self.MarkedList_pokemon = []
        self.MarkedList_color = []     
        
        
        #Create Pokemon List
        file_name = self.DexList
        file = open(os.path.join('Pokemon Lists', file_name), 'r')
        DexNumber = 1
        self.remaining_list = []
        self.remaining_list_with_number = []
        
        
        self.RegionalDex = file.readlines()
        for i in range(len(self.RegionalDex)):
            if i != 0:
                if self.RegionalDex[i][1:4] == self.RegionalDex[i-1][1:4]:
                    continue
            string = self.RegionalDex[i]
            string = string[5:len(string)-1]
            string = string.capitalize()
            self.RegionalDex[i] = string 
        
        
        
        for string in self.RegionalDex:
            
            self.remaining_list.append(string[:-1])
            
            Pokemon = (string[:-1], DexNumber)
            self.remaining_list_with_number.append(Pokemon)
            
            DexNumber += 1
        
        self.CountLabel.setText('Total: 0/' + str(len(self.remaining_list)))
        
        file.close()
       
        
        #Load Pokemon Included
        file = open(os.path.join('Pokemon Lists', 'National Dex.txt'), 'r')
        self.NationalDex = file.readlines()
        
        
        
       
        if self.CheckBox.isChecked():
            self.RegionalDex = sorted(self.RegionalDex, key = lambda x: self.all_pokemon.index(x))
        
        
        for Number in range(1, 922):
            self.pokemon_sprite['string'+str(Number)].clear()
        
        DexNumber = 1            
        
        for y in range(1, 35):
            for x in range(0, self.PokemonAcross):
                
                
                if DexNumber > len(self.RegionalDex):
                    break
                
                
                Pokemon = self.RegionalDex[DexNumber-1]
                Pokemon = Pokemon[:len(Pokemon)] 
                Pokemon = Pokemon.capitalize()
                if Pokemon == '':
                    break
                
                DexNumber += 1
                
                #Exclude alola and galarian forms if the national dex gets loaded
                if self.DexList == 'National Dex.txt' and Pokemon.endswith('-a') or self.DexList == 'National Dex.txt' and Pokemon.endswith('-g'):
                    break
                
                
                NatDexNumber = self.all_pokemon.index(Pokemon) + 1
                self.NatDexNumberList.append(NatDexNumber)
                
                pixmap = QPixmap(os.path.join('Pokemon Sprites', str(NatDexNumber)))
                pixmap = pixmap.scaled(30, 30)
                
                self.pokemon_sprite['string'+str(NatDexNumber)].setPixmap(pixmap)
                self.pokemon_sprite['string'+str(NatDexNumber)].resize(pixmap.width(),pixmap.height())
                self.pokemon_sprite['string'+str(NatDexNumber)].move(30*x, 15+30*y)
            
                a = random.randint(1, 25)
                if a == 1:
                    QApplication.processEvents()
 
            
        file.close()
           
    
    
    def MarkPokemon(self):
        Pokemon = self.EnterPokemonField.text()
        Pokemon = Pokemon.capitalize()
        if Pokemon not in self.MarkedList_pokemon:
            NatDexNumber = self.all_pokemon.index(Pokemon) + 1
           
            self.pokemon_sprite['string'+str(NatDexNumber)].setStyleSheet('background-color: %s' % (self.Color))
            
            self.EnterPokemonField.setText('')
            self.Count += 1
            self.CountLabel.setText('Total: ' + str(self.Count) + '/' + str(len(self.remaining_list)))
            
            
            self.MarkedList_pokemon.append(Pokemon)
            self.MarkedList_number.append(str(NatDexNumber))
            self.MarkedList_color.append(self.Color)
    
    def UnmarkPokemon(self):
        Pokemon = self.EnterPokemonField.text()
        Pokemon = Pokemon.capitalize()
        if Pokemon in self.MarkedList_pokemon:
            
            self.EnterPokemonField.setText('')
            self.Count -= 1
            self.CountLabel.setText('Total: ' + str(self.Count) + '/' + str(len(self.remaining_list)))
            
            NatDexNumber = self.all_pokemon.index(Pokemon) + 1
            
            self.pokemon_sprite['string'+str(NatDexNumber)].setStyleSheet('background-color: transparent')
            
            index = self.MarkedList_pokemon.index(Pokemon)
            self.MarkedList_pokemon.pop(index)
            self.MarkedList_number.pop(index)
            self.MarkedList_color.pop(index)
        
        else:
            self.EnterPokemonField.setText('')
            
            NatDexNumber = self.all_pokemon.index(Pokemon) + 1
            
            self.pokemon_sprite['string'+str(NatDexNumber)].setStyleSheet('background-color: blue')
            

        
        

#%%     open the window
if __name__ == '__main__':
    app = 0 # Cant Start the file after it has been closed before in a row if this line is not executed
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
