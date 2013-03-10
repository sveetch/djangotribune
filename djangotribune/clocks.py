# -*- coding: utf-8 -*-
"""
Tools to manipulate clocks
"""
import datetime

class ClockIndice(int):
    """
    ClockIndice accept an integer, his ``__str__`` method return a padded string with 
    zero on two digits and ``__unicode__`` return an exponent.
    
    This is an inherit of ``int`` so the real given value (the integer) are accessible 
    from the attribut ``real``.
    
    NOTE: ClockIndice is not conceived for indice with more than two digits, ``__unicode`` 
          could work with more but not ``__str__``.
    """
    _exposant_versions = u'¹²³⁴⁵⁶⁷⁸⁹⁰'
    
    def __repr__(self):
        return "<ClockIndice: {0}>".format(self.real)
    
    def __str__(self):
        return str(self.real).zfill(2)
    
    def __unicode__(self):
        return "".join( [self._exposant_versions[int(i)-1] for i in str(self.real)] )

class ClockstampManipulator:
    """
    Clock timestamp manipulator
    
    TODO: * indice seems dropped, but there are needed;
          * there is a bug in validation with a clock like "2013052"
    """
    def __init__(self, clockstamp):
        self.obj = False
        self.datestamp = None
        self.is_valid = False
        self.is_datetime = False
        self.clockstamp = clockstamp
        self.now = datetime.datetime.now()
        self.timestamp = clockstamp
        
        try:
            int(self.clockstamp)
        except ValueError:
            pass
        else:
            # Un time fait au moins 4caractères, un datetime pas plus de 14
            if len(self.clockstamp)>=4 and len(self.clockstamp)<=16:
                self.is_valid = True
        
        # Un datetime fait toujours plus de 6caractères (pour le time complet) 
        # et jamais plus de 14
        if len(self.clockstamp)>8 and len(self.clockstamp)<=16:
            self.is_datetime = True
        self.is_time = self.is_valid and not( self.is_datetime )
        
        # Détection d'une horloge avec "datetime" ou "time"
        if self.is_datetime:
            if len(self.clockstamp)>12:
                # Date avec l'année
                self.datestamp = clockstamp[0:8]
                self.timestamp = clockstamp[8:]
            else:
                # Date sans l'année
                self.datestamp = clockstamp[0:4]
                self.timestamp = clockstamp[4:]
            self.obj = self.get_clock_object(clocktype="datetime")
        else:
            self.obj = self.get_clock_object(clocktype="time")
        
    def get_clock_object(self, clocktype="datetime"):
        """
        Renvoi un objet datetime.time() de l'horloge si s'en est bien une.
        """
        if self.is_valid:
            # Heure de base, avec la microsecond à zéro
            clockDict = self.format_clock_time()
            if self.is_datetime:
                clockDict.update( self.format_clock_date() )
            # Rajoute une étape de fin
            clockDict_end = clockDict.copy()
            clockDict_end['microsecond'] = 999999
            # Init de l'objet datetime
            try:
                obj = getattr(datetime, clocktype)(**clockDict)
            except ValueError:
                self.is_valid = False
            else:
                return obj
        return None
    
    def format_clock_date(self):
        """
        Dictionnaire de la date de l'horloge. Le format date doit etre sous 
        la forme: YYYYMMDD
        
        YYYY : Année sous 4digits
        MM : Mois sous 2digits
        DD : Jour sous 2digits
        """
        clockDict = {
            'year': self.now.year,
            'month': self.now.month,
            'day': self.now.day,
        }
        clock = self.datestamp
        # Année optionnelle
        if len(clock) > 4:
            clockDict['year'] = int(clock[0:4])
            clock = clock[4:]
        # Mois
        if len(clock) > 0:
            clockDict['month'] = int(clock[0:2])
            clock = clock[2:]
            # Jour
            if len(clock) > 0:
                clockDict['day'] = int(clock[0:2])
        
        return clockDict
        
    def format_clock_time(self):
        """
        Dictionnaire du time de l'horloge. Le format time doit etre sous 
        la forme: HHTTSS
        
        HH : Heures sous 2digits
        TT : Minutes sous 2digits
        SS : Secondes sous 2digits
        
        Les secondes sont toujours optionnelles quelque soit le format.
        """
        clockDict = {
            'hour': 0,
            'minute': 0,
            'second': 0,
            'microsecond': 0,
        }
        clock = self.timestamp
        # Heure
        clockDict['hour'] = int(clock[0:2])
        clock = clock[2:]
        # Minutes
        if len(clock) > 0:
            clockDict['minute'] = int(clock[0:2])
            clock = clock[2:]
            # Secondes
            if len(clock) > 0:
                clockDict['second'] = int(clock[0:2])
                clock = clock[2:]
                # Microseconde de départ
                clockDict['microsecond'] = 0
        
        return clockDict
        
    def get_lookup(self):
        """
        Renvoi le bon lookup selon qu'on a un time ou un datetime.
        
        Le lookup renvoi toujours une requete de type "range" qui englobe 
        toute les microsecondes, étant donné qu'on ne les connaient jamais via 
        l'horloge.
        On les prends donc toute car l'éventualité que plusieurs posts soit 
        postés la meme seconde est assez maigre pour l'instant sauf avec des 
        bots.
        """
        # On doit vérifier qu'on a bien un datetime avant d'appeler ses méthodes
        if self.is_datetime:
            return self.get_datetime_lookup()
        # Dans le cas contraire on a obligatoirement un time
        else:
            return self.get_time_lookup()
        
    def get_time_lookup(self):
        """
        Renvoi un lookup de recherche pour les dernières horloges de la meme 
        heure.
        """
        if self.obj:
            return {
                'clock__range': (self.obj, self.obj.replace(microsecond=999999)),
            }
        
        return {}
    
    def get_datetime_lookup(self):
        """
        Renvoi un lookup de recherche pour les dernières horloges qui ont la 
        meme date et heure que celle donnée.
        """
        if self.obj:
            return {
                'created__range': (self.obj, self.obj.replace(microsecond=999999)),
            }
        
        return {}

## Tests
#if __name__ == "__main__":
    #clockstampsList = [
        #"07311001", # horloge correcte juste avec le time complet
        #"17112201", # horloge correcte juste avec le time complet
        #"1200", # horloge correcte juste avec le time sans les secondes
        #"2008032810431601", # horloge correcte, complète avec l'année
        #"032810431601", # horloge correcte, complète sans l'année
        #"456452008032810431601", # horloge trop longue
        #"42", # horloge trop courte
        #"foo", # pas une horloge
        #"17602201", # horloge avec une heure invalide
        #"2008032535431601", # horloge avec une heure invalide
        #"2008043110431601", # horloge avec une date invalide dans le calendrier
        #"2008043110431601", # horloge avec une date invalide dans le calendrier
    #]
    #for clock in clockstampsList:
        #print "~"*80
        #print "%s) %s [%s]" % (clockstampsList.index(clock)+1, clock, len(clock))
        ## Objet du timestamp
        #clockObject = ClockstampManipulator(clock)
        ## Retourne un lookup de recherche pour le timestamp
        #obj = clockObject.get_lookup()
        ## Rapport visuels des vérifs
        #print "is_valid:%s, is_datetime:%s, is_time:%s" % (clockObject.is_valid, clockObject.is_datetime, clockObject.is_time)
        #if obj:
            #print obj
