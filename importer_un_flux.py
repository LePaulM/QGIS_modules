"""
Model exported as python.
Name : Importer un flux
Group : ProjetPaul
With QGIS : 31609
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterDefinition
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsExpression
import processing


class ImporterUnFlux(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        # Le dossier du projet.
        self.addParameter(QgsProcessingParameterFile('Dossierdenregistrementdescouches', 'Dossier d'enregistrement du projet', behavior=QgsProcessingParameterFile.Folder, fileFilter='Tous les fichiers (*.*)', defaultValue='\\\\nas415\\Public2\\NasDiskStation_1\\public\\00_BOITES NOMINATIVES\\Paul\\Dev\\arbo_test'))
        # Couche vecteur au format Shapefile
        self.addParameter(QgsProcessingParameterVectorLayer('Emprise', 'Emprise', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        # Fichier de style spécifique à la couche
        self.addParameter(QgsProcessingParameterFile('Fichierdestyle', 'Fichier de style', optional=True, behavior=QgsProcessingParameterFile.File, fileFilter='Tous les fichiers (*.*)', defaultValue='\\\\nas415\\Public2\\NasDiskStation_1\\public\\00_BOITES NOMINATIVES\\Paul\\Dev\\styles\\ZNIEFF1.qml'))
        param = QgsProcessingParameterNumber('Tamponautourduterritoireenmtres', 'Tampon autour du territoire (en mètres)', optional=True, type=QgsProcessingParameterNumber.Integer, minValue=0, maxValue=1e+09, defaultValue=100)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        # Source de donnée unique. Chemin d'accès ou lien d'un flux.
        self.addParameter(QgsProcessingParameterString('xh', 'Source de donnée', multiLine=False, defaultValue='WFS:// pagingEnabled=\'true\' restrictToRequestBBOX=\'1\' srsname=\'EPSG:2154\' typename=\'ms:Znieff1\' url=\'http://ws.carmencarto.fr/WFS/119/fxx_inpn?\' version=\'auto\''))
        self.addParameter(QgsProcessingParameterFeatureSink('Test', 'test', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(20, model_feedback)
        results = {}
        outputs = {}

        # Vérifier la validité donnée
        alg_params = {
            'ERROR_OUTPUT': 'TEMPORARY_OUTPUT',
            'IGNORE_RING_SELF_INTERSECTION': False,
            'INPUT_LAYER': parameters['xh'],
            'INVALID_OUTPUT': 'TEMPORARY_OUTPUT',
            'METHOD': 1,
            'VALID_OUTPUT': None,
            'INVALID_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            'VALID_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VrifierLaValiditDonne'] = processing.run('qgis:checkvalidity', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Branche conditionnelle
        alg_params = {
        }
        outputs['BrancheConditionnelle'] = processing.run('native:condition', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Vérifier la validité emprise
        alg_params = {
            'IGNORE_RING_SELF_INTERSECTION': False,
            'INPUT_LAYER': parameters['Emprise'],
            'METHOD': 1,
            'VALID_OUTPUT': 'TEMPORARY_OUTPUT',
            'VALID_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VrifierLaValiditEmprise'] = processing.run('qgis:checkvalidity', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Présence d'entités invalides
        alg_params = {
            'CONDITION': outputs['VrifierLaValiditEmprise']['INVALID_COUNT'],
            'MESSAGE': 'La couche en entrée présente des entités invalides.'
        }
        outputs['PrsenceDentitsInvalides'] = processing.run('native:raiseexception', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Emprise invalide
        alg_params = {
            'CONDITION': outputs['VrifierLaValiditEmprise']['ERROR_COUNT'],
            'MESSAGE': 'L\'emprise ou la couche en entrée est invalide.'
        }
        outputs['EmpriseInvalide'] = processing.run('native:raiseexception', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Tampon emprise donnée
        # Rectifier la géométrie des entités invalides.
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0,
            'END_CAP_STYLE': 0,
            'INPUT': outputs['VrifierLaValiditDonne']['INVALID_OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TamponEmpriseDonne'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Tampon emprise projet
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': parameters['Tamponautourduterritoireenmtres'],
            'END_CAP_STYLE': 0,
            'INPUT': outputs['VrifierLaValiditEmprise']['VALID_OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TamponEmpriseProjet'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Fusionner des couches vecteur
        # On fusionne les entités invalides qui ont été mises en tampon et les entités valides.
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:2154'),
            'LAYERS': [outputs['TamponEmpriseDonne']['OUTPUT'],outputs['VrifierLaValiditDonne']['VALID_OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FusionnerDesCouchesVecteur'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Extraction et enregistrement de la couche invalide
        alg_params = {
            'INPUT': outputs['FusionnerDesCouchesVecteur']['OUTPUT'],
            'INTERSECT': outputs['TamponEmpriseProjet']['OUTPUT'],
            'PREDICATE': [0],
            'OUTPUT': parameters['Test']
        }
        outputs['ExtractionEtEnregistrementDeLaCoucheInvalide'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Test'] = outputs['ExtractionEtEnregistrementDeLaCoucheInvalide']['OUTPUT']

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Branche conditionnelle invalide
        alg_params = {
        }
        outputs['BrancheConditionnelleInvalide'] = processing.run('native:condition', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extraction et enregistrement de la couche valide
        alg_params = {
            'INPUT': outputs['VrifierLaValiditDonne']['VALID_OUTPUT'],
            'INTERSECT': outputs['TamponEmpriseProjet']['OUTPUT'],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractionEtEnregistrementDeLaCoucheValide'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Pas de données dans la zone d'étude
        alg_params = {
            'CONDITION': QgsExpression('').evaluate(),
            'MESSAGE': 'Pas de données correspondantes dans la zone d\'étude'
        }
        outputs['PasDeDonnesDansLaZoneDtude'] = processing.run('native:raiseexception', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Sauvegarder les entités vectorielles invalides dans un fichier
        alg_params = {
            'DATASOURCE_OPTIONS': '',
            'INPUT': outputs['ExtractionEtEnregistrementDeLaCoucheInvalide']['OUTPUT'],
            'LAYER_NAME': '',
            'LAYER_OPTIONS': '',
            'OUTPUT': QgsExpression(' @Dossierdenregistrementdescouches + \'/1_Donnees_base/02 - Référentiels thématiques/Biodiversité et continuités écologiques/INPN/ZNIEFF/Znieff1_continentales.shp\'').evaluate(),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SauvegarderLesEntitsVectoriellesInvalidesDansUnFichier'] = processing.run('native:savefeatures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Charger la couche invalide dans le projet
        alg_params = {
            'INPUT': outputs['SauvegarderLesEntitsVectoriellesInvalidesDansUnFichier']['FILE_PATH'],
            'NAME': 'couche_test_ZNIEFF 1'
        }
        outputs['ChargerLaCoucheInvalideDansLeProjet'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Branche conditionnelle valide
        alg_params = {
        }
        outputs['BrancheConditionnelleValide'] = processing.run('native:condition', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Appliquer le style
        alg_params = {
            'INPUT': outputs['ChargerLaCoucheInvalideDansLeProjet']['OUTPUT'],
            'STYLE': parameters['Fichierdestyle']
        }
        outputs['AppliquerLeStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Pas de données dans la zone d'étude
        alg_params = {
            'CONDITION': QgsExpression('').evaluate(),
            'MESSAGE': 'Pas de données correspondantes dans la zone d\'étude'
        }
        outputs['PasDeDonnesDansLaZoneDtude'] = processing.run('native:raiseexception', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Sauvegarder les entités vectorielles valides dans un fichier
        alg_params = {
            'DATASOURCE_OPTIONS': '',
            'INPUT': outputs['ExtractionEtEnregistrementDeLaCoucheValide']['OUTPUT'],
            'LAYER_NAME': '',
            'LAYER_OPTIONS': '',
            'OUTPUT': QgsExpression(' @Dossierdenregistrementdescouches + \'/1_Donnees_base/02 - Référentiels thématiques/Biodiversité et continuités écologiques/INPN/ZNIEFF/Znieff1_continentales.shp\'').evaluate(),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SauvegarderLesEntitsVectoriellesValidesDansUnFichier'] = processing.run('native:savefeatures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Charger la couche valide dans le projet
        alg_params = {
            'INPUT': outputs['SauvegarderLesEntitsVectoriellesValidesDansUnFichier']['OUTPUT'],
            'NAME': 'couche_test_ZNIEFF 1'
        }
        outputs['ChargerLaCoucheValideDansLeProjet'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Appliquer le style
        alg_params = {
            'INPUT': outputs['ChargerLaCoucheValideDansLeProjet']['OUTPUT'],
            'STYLE': parameters['Fichierdestyle']
        }
        outputs['AppliquerLeStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'Importer un flux'

    def displayName(self):
        return 'Importer un flux'

    def group(self):
        return 'ProjetPaul'

    def groupId(self):
        return 'ProjetPaul'

    def createInstance(self):
        return ImporterUnFlux()
