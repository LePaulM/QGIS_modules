# -*- coding: utf-8 -*-
# Paul Miancien - 07/2022

"""
***************************************************************************
*                                                                         *
*   This script is used to copy the content of a folder into a new        *
*   folder. This script is free of use.                                   *
*                                                                         *
***************************************************************************
"""

import os
import shutil
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qgis.core import *
from qgis import processing
from qgis.utils import iface

class CopyFolderAlgorithm(QgsProcessingAlgorithm):
    """
    This script is used to copy the content of a folder into a new folder.
    
    Ce script est utilisé pour copier le contenu d'un dossier dans un nouveau dossier à l'emplacement souhaité.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    SOURCE = 'SOURCE'
    DESTINATION = 'DESTINATION'
    PROJECTTYPE = 'PROJECTTYPE'
    

    def getAvailablebleProjectTypes(self, path) :
        """
        L'énumeration retourne uniquement un Integer, on va donc créer une liste qui contient 
        le nom des dossiers pour que l'algorithme puisse sélectionner le bon type de projet dans la liste à partir de cet entier. 
        L'entier doit correspondre à la position du type de projet dans la lsite.
        """
        listeProjets= []
        for name in os.listdir(path) :
            listeProjets.append(name)

        return listeProjets


    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CopyFolderAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        
        Retourne le nom de l'algorithme.
        """
        return 'copy folder to folder'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        
        Affiche le nom de l'algorithme.
        """
        return self.tr('Copy folder to folder')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        
        Retourne le nom du groupe auquel appartient l'algorithme.
        """
        return self.tr('scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'scripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Copy folder content to new folder using pyqgis.\n\nCopier le contenu d'un dossier dans un nouveau dossier en utilisant pyqgis.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        
        Ici on définit les entrées et sorties de l'algorithme, ainsi que leurs propriétés respectives.
        """

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.SOURCE,
                self.tr('Source folder - Dossier source')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.DESTINATION,
                self.tr('Destination folder - Dossier de destination'),
            )
        )
        
        # Type de projet, disponible grace à une énumération en entrée dans le model builder
        self.addParameter(
            QgsProcessingParameterEnum(
                self.PROJECTTYPE,
                self.tr('Project Type'),
                allowMultiple=False,
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Ici on récupère les paramètres en entrées de l'algorithme et on les converti en chaînes de caractères.
        source = self.parameterAsString(
            parameters,
            self.SOURCE,
            context
        )
        
        destination = self.parameterAsString(
            parameters,
            self.DESTINATION,
            context
        )
        
        projectType = self.parameterAsString(
            parameters,
            self.PROJECTTYPE,
            context
        )
        
        listeprojets = self.getAvailablebleProjectTypes(source)
        
        source = source + listeprojets[int(projectType)]
        
        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        # Si l'une des entrées n'est pas renseignée on envoie une erreur pour indiquer que l'algorithme n'a pas fonctionné.
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SOURCE))
        elif destination is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DESTINATION))
        elif projectType is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.PROJECTTYPE))
        
        # Send some information to the dev
        # On renvoie les informations 
        QgsMessageLog.logMessage('SOURCE : ' + source, "CopyFolderToFolderLog")
        QgsMessageLog.logMessage('DESTINATION : ' + destination, "CopyFolderToFolderLog")
        QgsMessageLog.logMessage('PROJECT TYPE : ' + listeprojets[int(projectType)], "CopyFolderToFolderLog")

        # C'est ici que la copie se fait. Voir lien ci-dessous.
        # https://docs.python.org/3/library/shutil.html
        shutil.copytree(source, destination, symlinks=False)
        
        
        # Ici on essaie d'ouvrir le projet créé dans 03_DIAG
        project = QgsProject.instance() 
        project.read(destination + "//03_1_DIAG//Projet_DIAG.qgs")
        
        # Send some information to the user
        feedback.pushInfo(destination)

        # On ne met rien en retour car on n'a pas d'objet en sortie.
        return {}
