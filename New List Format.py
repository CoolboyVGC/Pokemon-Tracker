import os

def ChangeText():
    file_name = input('File Name') + '.txt'
    
    while file_name.startswith(' '):
        file_name = file_name[1:]
    if file_name.endswith('.txt.txt'):
        file_name = file_name[:len(file_name)-4]
    
    file = open(os.path.join('Pokemon Lists', file_name), 'r')
    lines = file.readlines()
    file.close()
    
    file = open(os.path.join('Pokemon Lists', file_name), 'w')
    
    line = 0
    newfile = ''
    
    #Create the string for the new file
    for string in lines:
        
        line += 1
        
        while string.startswith(' '):
            string = string[1:]
        
        #If the inserted list is in a ranger browser format, replace it like this
        if string.startswith('r-'):
            string = '#' + string[2:]
        elif string.startswith('R-'):
            string = '#' + string[2:]
        
        if string.endswith('-a\n') or string.endswith('-g\n'):
            string = string[0: len(string)-3] + '\n'
        
        #If the current pokemon already starts with an #, it can still be wrong if it's not zeropad
        if string.startswith('#'):
            if line in range(1, 10):
                if string.startswith('#00'):
                    newfile += string
                    continue
                string = string[3:]
            
            elif line in range(10, 100):
                if string.startswith('#0'):
                    newfile += string
                    continue
                string = string[4:]
            
            elif line >99:
                if string.startswith('#'):
                    newfile += string
                    continue
                string = string[5:]
        
                
        
        
        string = string.capitalize()
        
        if line in range(1, 10):
            string = '#00' + str(line) + ' ' + string
        elif line in range(10, 100):
            string = '#0' + str(line) + ' ' + string
        elif line > 99:
            string = '#' + str(line) + ' ' + string
    
        if string.endswith('\n'):
            pass
        else:
            string += '\n'
        
        newfile += string
    
    file.write(newfile)
    
    file.close()

    test = input('Do Another File?')
    if test == True or test == 'yes' or test == 'y':
        ChangeText()

ChangeText()