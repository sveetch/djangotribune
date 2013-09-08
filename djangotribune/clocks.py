# -*- coding: utf-8 -*-
"""
Tools to manipulate clocks
"""
import datetime, re
from djangotribune.parser import POST_CLEANER_CLOCK_RE

PARSER_EXCEPTION_TYPERROR_EXPLAIN = "Unvalid clock format, should be 00:00[:00][^1]"

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


class ClockParser(object):
    clock_regex = re.compile(POST_CLEANER_CLOCK_RE)
    
    def is_valid(self, clock, _m=None):
        m = _m or self.clock_regex.match(clock)
        if not m:
            return False
            
        return True
    
    def parse(self, clock):
        """
        Try to parse the clock and return a simple dict
        """
        m = self.clock_regex.match(clock)
        if not self.is_valid(clock, _m=m):
            raise TypeError(PARSER_EXCEPTION_TYPERROR_EXPLAIN)
        
        _d = m.groupdict()
        stuff = {
            'hour': int(_d['h']),
            'minute': int(_d['m']),
            'second': 0,
            'microsecond': 0,
            'indice': 0,
        }
        if _d['s'] is not None: stuff['second'] = int(_d['s'])
        # Remove the ^ at beginning of the value
        if _d['sel'] is not None: stuff['indice'] = int(_d['sel'][1:])
        return stuff
        
    def get_time_object(self, clock):
        """
        Return a datetime.time object for the clock
        """
        _p = self.parse(clock)
        # Remove indice key as its not part of datetime.time arguments
        del _p['indice']
        
        return datetime.time(**_p)
        
    def get_time_lookup(self, clock):
        """
        Return a queryset lookup to search for last clock from the same XX:XX[:XX] range
        """
        obj = self.get_time_object(clock)
        return {
            'clock__range': (obj, obj.replace(microsecond=999999)),
        }
        
        return {}
