# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************

Aux personnes qui reprennent ce code : je me parle à la 2e personne, du coup si je dis "démerde toi" ou des trucs comme ça c'est pour moi, pas pour vous. Bonne journée !
"""

from qgis.PyQt.QtCore import *
from qgis.core import *
from qgis import processing
import urllib
from owslib.wfs import WebFeatureService



class InputFromCSVAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    CSV = 'CSV FILE'
    TERRITOIRE = 'Zone d\'étude'
    BUFFER = 'TAMPON'    
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return InputFromCSVAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'inputsfromcsv'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Inputs from CSV')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
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
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input CSV file
        self.addParameter(
            QgsProcessingParameterFile (
                self.CSV,
                self.tr('CSV source'),
                defaultValue = "//NAS415/Public2/NasDiskStation_1/public/SO_SIG/000_DEVELOPPEMENT/GéomaKit/sources_de_donnees.csv"
            )
        )
        
        # On ajoute l'emprise du territoire sur lequel on veut travailler
        self.addParameter(
            QgsProcessingParameterFeatureSource (
                self.TERRITOIRE,
                self.tr("Territoire d'étude"),
            )
        )
        
        # On ajoute l'emprise du territoire sur lequel on veut travailler
        self.addParameter(
            QgsProcessingParameterNumber (
                self.BUFFER,
                self.tr("Tampon autour du territoire (si on cherche des données complémentaires)"),
                defaultValue = 0
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        """
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )
        """
        

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.

        """


        source = self.parameterAsString(
            parameters,
            self.CSV,
            context
        )
        
        feedback.pushInfo(source)

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # On récupère le CSV contenant les sources de données et on l'ajoute à la carte
        sourceTableLayer = QgsVectorLayer(source, 'sourceCSV', 'ogr')
        
        # on révcupère les noms des champs
        field_names = sourceTableLayer.fields().names()
        # on compte le nombre de lignes à traiter dans le CSV
        fc = sourceTableLayer.featureCount()
        
        feedback.pushInfo(str(fc))
        
        for feat in sourceTableLayer.getFeatures():
            # On récupère les valeurs des champs dans une liste
            attributes = feat.attributes()
            # On récupère l'url des connexions
            uri = attributes[3]
            # On vérifie que le lien existe dans la source de données
            if not (uri is None or uri == '') :
                    
                # On indique à l'utilisateur la progression de l'algorithme
                feedback.pushInfo('Traitement en cours pour la connexion : ' + uri)

                # la variable wfs est un dictionnaire (type 'dict') contenant en clé le nom de la couche et en valeur la métadonnée de la couche
                wfs = WebFeatureService(url=uri, version='1.1.0')
                # feedback.pushInfo("wfs content: "+str(wfs.contents))                  # pour voir le résultat de la requête
                
                # la fonction items() permet d'itérer dans le dictionnaire
                for key, value in wfs.items():
                    feedback.pushInfo("import de la donnée : " + key)
                    layer = QgsVectorLayer("WFS:// pagingEnabled='true' typename=ms:"+key+" url="+uri+" version='auto'", key, "WFS")
                    QgsProject.instance().addMapLayer(layer, True)
                    """
                    # Si la couche WFS générée est invalide on envoie l'info à l'utilisateur
                    if not layer.isValid():
                        feedback.pushInfo("Layer " + key + " failed to load!")
                    else :
                        QgsProject.instance().addMapLayer(layer)
                    """
            elif not attributes[4] is None :
                feedback.pushInfo("Absence de lien WFS, chargement du lien WMS")
                uri = attributes[4]
                # TO DO : chargement lien WMS
            elif not attributes[5] is None :
                feedback.pushInfo("Absence de lien WMS, chargement de la couche du NAS")
                uri = attributes[5]
                # TO DO : chargement des couches NAS
            else : 
                feedback.pushInfo("Donnée " + attribute[0] + " introuvable!")
                # break ?

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / sourceTableLayer.featureCount() if sourceTableLayer.featureCount() else 0
        features = sourceTableLayer.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Update the progress bar
            feedback.setProgress(int(current * total))
          
        # ceci est un dictionnaire, démerde toi pour pouvoir l'afficher
        """
        for i in QgsProject.instance().mapLayers().items():
            feedback.pushInfo(i.name())
        """
        
        # à la fin de l'algorithme on retire la couche csv
        QgsProject.instance().removeMapLayer(sourceTableLayer)

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {}
