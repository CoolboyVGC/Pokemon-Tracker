import sys
import os
import re
import traceback
import json
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QComboBox, QColorDialog, QMessageBox, QSpinBox, QCheckBox, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt


myappid = 'CoolboyVGC.PokedexTracker.2.0.0'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# %%     Basic setup for the window
class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle('Pokemon Dex Tracker')
        self.setWindowIcon(QIcon(resource_path('./Pokemon Sprites/Pokeball.ico')))
        
        size = app.primaryScreen().availableGeometry()  # Get the borders of the screen
        size = QDesktopWidget().screenGeometry(0)
        width = size.width()
        height = size.height()

# %%     Create Widgets

        self.EnterPokemonField = QLineEdit(self)
        self.EnterPokemonField.setGeometry(10, 10, 250, 30)

        self.ColorButton = QPushButton(self)
        self.ColorButton.setText('Select Color')
        self.ColorButton.setGeometry(270, 10, 90, 30)
        self.ColorButton.clicked.connect(self.openColorDialog)

        self.DeleteButton = QPushButton(self)
        self.DeleteButton.setGeometry(370, 10, 20, 30)
        self.DeleteButton.setText('-')
        self.DeleteButton.clicked.connect(self.unmarkPokemon)
        self.DeleteButton.setToolTip('Unmark a pokemon, or mark a pokemon without it counting towards the total')

        self.DexLoadButton = QPushButton(self)
        self.DexLoadButton.setGeometry(420, 10, 100, 30)
        self.DexLoadButton.setText('Load Pokemon List')
        self.DexLoadButton.clicked.connect(self.startTracking)
        self.DexLoadButton.setShortcut('F5')

        self.CheckBox = QCheckBox(self)
        self.CheckBox.setGeometry(825, 10, 110, 30)
        self.CheckBox.setText('Order by Nat Dex')

        Basic_Order = ['National', 'RBY', 'GSC', 'RSE', 'DP', 'Platinum', 'HgSs', 'BW', 'BW2', 'XY', 'OrAs', 'SuMo',
                       'UsUm', 'Galar']
        self.comboBox = QComboBox(self)
        for x in Basic_Order:
            self.comboBox.addItem(x + ' Dex')
        for x in os.listdir(os.path.join(resource_path('Pokemon Lists'))):
            EndPoint = x.index('.')
            name = x[:EndPoint]
            if name[:-4] in Basic_Order:
                continue
            self.comboBox.addItem(name)
        for x in os.listdir(os.path.join('Extra Lists')):
            EndPoint = x.index('.')
            name = x[:EndPoint]
            self.comboBox.addItem(name)
        self.comboBox.setGeometry(530, 10, 150, 30)
        self.comboBox.setCurrentIndex(0)
        self.comboBox.activated[str].connect(self.setDexList)

        self.PokemonAcrossField = QSpinBox(self)
        self.PokemonAcrossField.setGeometry(690, 10, 40, 30)
        self.PokemonAcrossField.setValue(int((width-10)/32))
        self.PokemonAcross = int((width-10)/32)

        self.InformationLabel = QLabel(self)
        self.InformationLabel.setText('Pokemon Across')
        self.InformationLabel.setGeometry(740, 10, 80, 30)

        self.ImportPokemonButton = QPushButton(self)
        self.ImportPokemonButton.setGeometry(width - 150 - 10, 10, 150, 30)
        self.ImportPokemonButton.setText('Import Marked Pokemon')
        self.ImportPokemonButton.clicked.connect(self.importMarked)

        self.ExportPokemonButton = QPushButton(self)
        self.ExportPokemonButton.setGeometry(width - 150 - 10 - 150 - 10, 10, 150, 30)
        self.ExportPokemonButton.setText('Export Marked Pokemon')
        self.ExportPokemonButton.clicked.connect(self.exportMarked)

        self.CountLabel = QLabel(self)
        self.CountLabel.setStyleSheet('color: red')
        self.CountLabel.setFont(QFont('Arial', 15))
        self.CountLabel.setText('Total: 0/0')
        self.CountLabel.setGeometry(10, 50, 135, 30)
        self.Count = 0

        self.Color = '#000000'
        self.pokemon_sprite = {}  # sprites for the pokemon
        self.DexList = 'National Dex.txt'  # dex list if no new list is specified
        self.NatDexNumberList = []
        self.MarkedList_number = []  # Create lists to add numbers/names/colors of marked pokemon
        self.MarkedList_pokemon = []
        self.MarkedList_color = []
        self.UnmarkedList = []

        file = open(os.path.join(resource_path('./Pokemon Lists/National Dex.txt')), 'r')
        self.NationalDex = file.read().split("\n")[:-1]
        file.close()
        self.all_pokemon = []
        for string in self.NationalDex:
            string_pokemon = string.capitalize()
            self.all_pokemon.append(string_pokemon)

        # Initialize all pokemon
        for x in range(1, 891):
            self.pokemon_sprite[f"string{x}"] = QLabel(self)  # Create a label for every pokemon

            pixmap = QPixmap(os.path.join(resource_path('Pokemon Sprites'), str(x)))
            pixmap = pixmap.scaled(32, 32)

            self.pokemon_sprite['string' + str(x)].setPixmap(pixmap)
            self.pokemon_sprite['string' + str(x)].resize(32, 32)
            self.pokemon_sprite['string' + str(x)].move(-40,  -40)

        self.showMaximized()

    # %%     Creating the functions

    def getNatDexNumber(self, regionalnumber, pokemon):
        if regionalnumber != 0:
            return self.NatDexNumberList[regionalnumber-1]
        else:
            return self.all_pokemon.index(pokemon) + 1

    def keyReleaseEvent(self, event):
        if event.key() == 16777220:
            try:
                self.markPokemon()
            except:
                pass

    def mousePressEvent(self, event):
        try:
            
            # Obtain Position where the marking must go
            x = event.x()
            x = 32 * int(x / 32)
            y = event.y()
            y = 15 + 32 * int((y - 15) / 32)

            if y > 44 and x < 32 * self.PokemonAcross:  # only Mark pokemon when clicking where there are pokemon
                # Determine what The national Dex Number of the pokemon is
                rows = int((y - 15) / 32)
                colomn = int(x / 32) + 1
                if colomn > self.PokemonAcross:
                    raise SyntaxError  # Create error to stop
                RegionalDexNumber = self.PokemonAcross * (rows - 1) + colomn
                NatDexNumber = self.getNatDexNumber(RegionalDexNumber, 0)
                self.EnterPokemonField.setText(self.all_pokemon[NatDexNumber - 1])

                if event.button() == 1:
                    self.markPokemon()

                elif event.button() == 2:
                    self.unmarkPokemon()
        except:
            pass

    def dragEnterEvent(self, event):
        try:
            if event.mimeData().hasUrls():
                event.accept()
            else:
                event.ignore()
        except:
            traceback.print_exc()

    def dragMoveEvent(self, event):
        try:
            if event.mimeData().hasUrls():
                event.setDropAction(Qt.CopyAction)
                event.accept()
            else:
                event.ignore()
        except:
            traceback.print_exc()

    def dropEvent(self, event):
        try:
            if event.mimeData().hasUrls():
                event.setDropAction(Qt.CopyAction)
                event.accept()
                
                for url in event.mimeData().urls():

                    if url.isLocalFile:
    
                        url = str(url.toLocalFile())
                        
                        "Determine what kind of file is added"
                        with open(url, 'r') as f:
                            text = f.read()
    
                            try:
                                json.loads(text)
                                "New Format marked list"
                                self.importMarked(url=url)
                                return
                            
                            except json.JSONDecodeError:
                                if len(text.split('\n')) > 1:
                                    if text.split('\n')[0] in self.all_pokemon:
                                        "Tracker List"
                                        self.startTracking(url=url)
                                        return
                                
                                else:
                                    "Old Format marked list"
                                    self.importMarked(url=url)
                                    return
                    
                    msg = QMessageBox(parent=self, text="The given file could not be interpreted")
                    msg.exec_()
                
            else:
                event.ignore()
        except:
            traceback.print_exc()

    def openColorDialog(self):
        try:
            color = QColorDialog.getColor()

            if color.isValid():
                self.Color = color.name()

                if self.Color[5] in 'cdef':  # Make sure the color isn't too similar to the color used to negative mark pokemon
                    if self.Color[1] in '0123456' and self.Color[3] in '0123456':
                        msg = QMessageBox(self)
                        msg.setWindowTitle('Color Error')
                        msg.setText('The color you entered is too similar to the color used to negative mark pokemon')
                        msg.setIcon(QMessageBox.Information)

                        msg.exec()

                        self.openColorDialog()

                self.ColorButton.setStyleSheet('color: %s' % self.Color)
        except:
            traceback.print_exc
            
    def setDexList(self, text):
        self.DexList = text + '.txt'

    def exportMarked(self):
        try:
            filename, ok = QFileDialog.getSaveFileName(self, "Save Progress", "", "JSON Files (*.json);;Text Files (*.txt);;All Files (*)")
            if ok:
            
                Dict = {"Doctype": "PkmnTrackerSavev2",
                        "pkmn": {}}
                
                for index, pokemon in enumerate(self.MarkedList_pokemon):
                    color = self.MarkedList_color[index]
                    Dict['pkmn'][pokemon] = color
            
                with open(filename, "w") as f:
                    json.dump(Dict, f, ensure_ascii=True, indent=4)
        except:
            traceback.print_exc()
        
    def importMarked(self, url=None):

        if not url:
            url, ok = QFileDialog.getOpenFileName(self, "Select Saved Progress", "", "JSON Files (*.json);;Text Files (*.txt);;All Files (*)")
            if not ok:
                return

        oldcolor = self.Color

        try:
            """New Format of Pokemon File"""
            Dict = json.loads(open(url, 'r').read())
            
            try:
                if Dict["Doctype"] != "PkmnTrackerSavev2":
                    raise KeyError
            except KeyError:
                msg = QMessageBox(parent=self, text="The given file could not be interpreted")
                msg.exec_()
                return
            
            for pokemon in Dict["pkmn"]:
                color = Dict['pkmn'][pokemon]

                self.Color = color
                self.EnterPokemonField.setText(pokemon)
                self.markPokemon()
            
            self.Color = oldcolor
            
            return
        
        except json.JSONDecodeError:
            pass
        
        try:
            """Old Format of Pokemon File, still needs to be supported"""
            pokemonlist = list(open(url, 'r').read())

            #file = open(os.path.join(resource_path('Pokemon Lists'), 'National Dex.txt'), 'r')
            #file.close()

            pokemonlist.append(',')  # This makes it easy to run the last pokemon as well

            # Adding some variables that will be used in this function
            current_pokemon = ''
            colorStarted = False

            for i in pokemonlist:
                if i == ' ':  # Exclude the spaces, they are only between pokemon for the users convinience
                    continue
                elif i == ',':  # Run the mark pokemon using the current pokemon

                    pokemon_number = ''
                    color_name = ''

                    # Split the string to the pokemon and the color
                    for character in current_pokemon:

                        if not colorStarted:
                            if character == '(':
                                colorStarted = True
                            else:
                                pokemon_number += character

                        elif character == ')':
                            break
                        else:
                            color_name += character

                    pokemon = int(pokemon_number)
                    pokemon_name = self.NationalDex[pokemon - 1][:-1]

                    self.Color = color_name

                    self.EnterPokemonField.setText(pokemon_name)
                    current_pokemon = ''
                    colorStarted = False
                    self.markPokemon()

                    self.Color = oldcolor

                else:
                    current_pokemon += i
        except:
            msg = QMessageBox(parent=self, text="The given file could not be interpreted")
            msg.exec_()

    def startTracking(self, url=None):
        try:
            self.Count = 0
            try:
                self.PokemonAcross = int(self.PokemonAcrossField.text())
            except:
                pass
    
            # Clear old Markings
            for number in range(1, len(self.all_pokemon)+1):
                pass
                self.pokemon_sprite['string' + str(number)].setStyleSheet('background-color: transparent')
                self.pokemon_sprite['string' + str(number)].move(-100, -100)
    
            self.NatDexNumberList = []
            self.MarkedList_number = []
            self.MarkedList_pokemon = []
            self.MarkedList_color = []
    
            # Create Pokemon List
            file_name = self.DexList
            if url:
                file = open(url, 'r')
            else:
                try:
                    file = open(resource_path('./Pokemon Lists/'+file_name), 'r')
                except FileNotFoundError:
                    file = open('./Extra Lists/'+file_name, 'r')
            DexNumber = 1
            self.remaining_list = []
            self.remaining_list_with_number = []
    
            self.RegionalDex = file.readlines()
            for i in range(len(self.RegionalDex)):
                string = self.RegionalDex[i]
                string = string[:-1]
                string = string.capitalize()
                self.RegionalDex[i] = string
    
            for string in self.RegionalDex:
                self.remaining_list.append(string[:-1])
    
                Pokemon = (string[:-1], DexNumber)
                self.remaining_list_with_number.append(Pokemon)
    
                DexNumber += 1
    
            self.CountLabel.setText('Total: 0/' + str(len(self.remaining_list)))
    
            file.close()
    
            # Load Pokemon Included
            file = open(os.path.join(resource_path('Pokemon Lists'), 'National Dex.txt'), 'r')
            self.NationalDex = file.readlines()
    
            if self.CheckBox.isChecked(): #sorts pokemon by National dex order
                self.RegionalDex = sorted(self.RegionalDex, key=lambda x: self.all_pokemon.index(x))
    
            
            DexNumber = 1
    
            for y in range(1, 35):
                for x in range(0, self.PokemonAcross):
    
                    if DexNumber > len(self.RegionalDex):
                        break
    
                    Pokemon = self.RegionalDex[DexNumber - 1]
                    if Pokemon == '':
                        break
    
                    DexNumber += 1
    
                    # Exclude alola and galarian forms if the national dex gets loaded
                    if self.DexList == 'National Dex.txt' and Pokemon.endswith(
                            '-a') or self.DexList == 'National Dex.txt' and Pokemon.endswith('-g'):
                        break
    
                    
                    NatDexNumber = self.getNatDexNumber(0, Pokemon)
    
                    self.NatDexNumberList.append(NatDexNumber)
    
    
                    self.pokemon_sprite['string' + str(NatDexNumber)].move(10 + 32 * x, 15 + 32 * y)
    
                    #a = random.randint(1, 25)
                    #if a == 1:
                    #    QApplication.processEvents()
                
                else:
                    continue
                break
    
            self.CountLabel.move(self.PokemonAcross * 32 - 135, 32 * y + 20)
            if x > self.PokemonAcross - 5:
                self.CountLabel.move(10, 32 * (y+1) + 20)
                
            
            file.close()
            
        except Exception:
            traceback.print_exc()

    def markPokemon(self):
        Pokemon = self.EnterPokemonField.text()
        Pokemon = Pokemon.capitalize()
        NatDexNumber = self.getNatDexNumber(0, Pokemon)
        if Pokemon in self.UnmarkedList:
            self.pokemon_sprite['string' + str(NatDexNumber)].setStyleSheet('background-color: transparent')
            self.EnterPokemonField.setText('')
            self.UnmarkedList.remove(Pokemon)

        elif Pokemon not in self.MarkedList_pokemon:

            self.pokemon_sprite['string' + str(NatDexNumber)].setStyleSheet('background-color: %s' % self.Color)

            self.EnterPokemonField.setText('')
            self.Count += 1
            self.CountLabel.setText('Total: ' + str(self.Count) + '/' + str(len(self.remaining_list)))

            self.MarkedList_pokemon.append(Pokemon)
            self.MarkedList_number.append(str(NatDexNumber))
            self.MarkedList_color.append(self.Color)

    def unmarkPokemon(self):
        try:
            Pokemon = self.EnterPokemonField.text()
            Pokemon = Pokemon.capitalize()
            if Pokemon in self.MarkedList_pokemon:

                self.EnterPokemonField.setText('')
                self.Count -= 1
                self.CountLabel.setText('Total: ' + str(self.Count) + '/' + str(len(self.remaining_list)))

                NatDexNumber = self.getNatDexNumber(0, Pokemon)

                self.pokemon_sprite['string' + str(NatDexNumber)].setStyleSheet('background-color: transparent')

                index = self.MarkedList_pokemon.index(Pokemon)
                self.MarkedList_pokemon.pop(index)
                self.MarkedList_number.pop(index)
                self.MarkedList_color.pop(index)

            else:
                self.EnterPokemonField.setText('')
                
                self.UnmarkedList.append(Pokemon)
                NatDexNumber = self.getNatDexNumber(0, Pokemon)
                self.pokemon_sprite['string' + str(NatDexNumber)].setStyleSheet('background-color: blue')
        except:
            pass


# %%     open the window
if __name__ == '__main__':
    app = 0
    app = QApplication(sys.argv)
    ex = App()
    ex.installEventFilter(ex)
    ex.show()
    sys.exit(app.exec_())
