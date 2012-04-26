# -*- coding: utf-8 -*-
"""
Tools to manipulate clocks
"""
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
