# Utilitaire de comparaison de jeux de données Pacejka
# E. Cabrol
# 10/09/2018

#import os
import re
from collections import defaultdict

#Les fichiers .tir à comparer
files=('TASS_car205_60R15.tir','PACEJKA__MF51_T1_IMT5__P26bar_XY 19 04 2010.tir')

#Le fichier de sortie
log_filename='tir_compare.log'

#Les catégories que l'on souhaite traiter
categories = ['SCALING_COEFFICIENTS','LONGITUDINAL_COEFFICIENTS','OVERTURNING_COEFFICIENTS','LATERAL_COEFFICIENTS','ROLLING_COEFFICIENTS','ALIGNING_COEFFICIENTS']

# Un peu d'initialisation
tir_database={} 
# A la fin ça ressemblera à 
#   tir_database["monFichier.tir"]["PCX1"]["value"]=1.37
#   tir_database["monFichier.tir"]["PCX1"]["descr"]="Shape factor bla bla"

# Bien pratique ce defaultdict
paramsInCategory=defaultdict(dict)
paramsNullInCategory=defaultdict(dict)

for filename in files:
    
    #On initialise un dictionnaire réinitialisé à chaque fichier qui ressemblera à
    #param["PCX1"]["value"]=1.37
    #param["PCX1"]["descr"]="Shape factor bla bla"
    param=defaultdict(dict)
    #NB : on pourrait définir directement tir_database, mais on y perdrait en lisibilité
    
    with open(filename) as file :
        print("Fichier "+filename+" ouvert correctement")
        for line in file :
             #Si la ligne commence par [TOTO] c'est qu'on est dans la catégorie .. TOTO. Dingue non ? 
             matchCategory=re.match('\[(.+)\]',line)
             if matchCategory:
                 current_category = matchCategory.group(1)
                 # On initialise alors la liste des paramètres associés à cette
                 # catégorie pour le fichier en cours
                 paramsInCategory[current_category][filename]=[]
                 # ... ainsi que la liste des paramètres nuls
                 paramsNullInCategory[current_category][filename]=0
                 #Une petite boucle pour savoir si on doit traiter la catégorie
                 process=0
                 for cat in categories:
                     if(cat==current_category):
                         process=1
             #Si ce n'est pas le cas on passe à l'itération suivante
             if(process==0):
                 continue
             # Une petite regexp des familles pour isoler 
             # 1- le nom du paramètre (lettres éventuellement suivies de chiffres)
             # 2- la valeur (possibilités : 0 / -0.1 / 1.2E2 / 1.2E-02)
             # 3- la description (qui vient après le dernier signe $)
             # On utilise les parenthèses pour récuperer les résultats via search.group
             searchData=re.search('(\w+\d*)\s*=\s*(-*\d+\.*\d*[eE]*-*\d*).+\$(.+)',line)
             if searchData:
                 paramsInCategory[current_category][filename].append(searchData.group(1))
                 # On convertit la valeur pour ne pas avoir une chaine
                 param[searchData.group(1)]["value"] = float(searchData.group(2))
                 # Si la valeur est nulle on l'ajoute à la liste qui va bien
                 if param[searchData.group(1)]["value"] ==0:
                     paramsNullInCategory[current_category][filename] +=1
                 # Enfin on stocke la description
                 param[searchData.group(1)]["descr"] = searchData.group(3)
    
    # On affecte enfin le "méta"-dictionnaire final
    tir_database[filename]=param

print("File parsing terminated")

#Ecriture du fichier de log
with open(log_filename, 'w') as logFile :
    
    # On commence par un petit tableau à coller dans Excel
    # avec le nb de paramètres par catégorie pour chaque fichier
    # et entre parenthèses le nb de paramètres nuls
    logFile.write('category\tTNO\tRNO\n')
    for cat in categories:
        string = cat
        for filename in files:
            string+="\t"+str(len(paramsInCategory[cat][filename]))
            string+=" ("+str(paramsNullInCategory[cat][filename])+")"
        logFile.write(string+"\n")
    logFile.write("\n")
    
    # On cherche ensuite les éléments présents dans un .tir et absents de l'autre
    logFile.write("***\n\nParameters present in TNO file but absent from Renault file :\n\n")
    for cat in categories:
        set_TNO = paramsInCategory[cat]['TASS_car205_60R15.tir']
        set_RNO = paramsInCategory[cat]['PACEJKA__MF51_T1_IMT5__P26bar_XY 19 04 2010.tir']   
        string = cat+"\n"
        for elem in set_TNO:
            if elem not in set_RNO:
                string+="\t"+elem+"\t"+tir_database['TASS_car205_60R15.tir'][elem]["descr"]+"\n"
        logFile.write(string+"\n")
    
    # ... et vice-versa    
    logFile.write("***\n\nParameters present in Renault file but absent from TNO file :\n\n")
    for cat in categories:
        set_TNO = paramsInCategory[cat]['TASS_car205_60R15.tir']
        set_RNO = paramsInCategory[cat]['PACEJKA__MF51_T1_IMT5__P26bar_XY 19 04 2010.tir']   
        string = cat+"\n"
        for elem in set_RNO:
            if elem not in set_TNO:
                string+="\t"+elem+"\t"+tir_database['PACEJKA__MF51_T1_IMT5__P26bar_XY 19 04 2010.tir'][elem]["descr"]+"\n"
        logFile.write(string+"\n")       

print("File "+log_filename+" has been written")
