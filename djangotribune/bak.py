# -*- coding: utf-8 -*-
"""
For Message filter
"""
from djangotribune import __version__ as djangotribune_version
from djangotribune.models import FILTER_TARGET_ALIASES, FILTER_KIND_ALIASES

DEFAULT_KIND_VALUE = ('==', 'exact')

class BakController(object):
    """
    Controller filled in session with all user message filters
    """
    item_key = "{target}_{kind}={pattern}"
    
    def __init__(self, author):
        self.author = author
        self.active = True
        self._target_alias = dict(FILTER_TARGET_ALIASES)
        self._kind_alias = dict(FILTER_KIND_ALIASES)
        self.version = djangotribune_version # Used to clean old version stored in session before updates
        self.reset()
        
    def __repr__(self):
        author_name = "Anonymous"
        if self.author and self.author.is_authenticated():
            author_name = "'{0}'".format(self.author.username)
        return "<BakController {author}>".format(author=author_name)
        
    def reset(self):
        """Clean registry"""
        self.rules = {}
        self.saved = False
        self.loaded = False
    
    def get_filters(self):
        """Return the rules as tuples (target, pattern, kind)"""
        return self.rules.values()
        
    def get_key(self, target, pattern, kind):
        """Get a flat key from given args"""
        return self.item_key.format(target=target, pattern=pattern, kind=kind)
        
    def has_rule(self, target, pattern, kind=DEFAULT_KIND_VALUE[1]):
        """Check if given args allready exists in registry"""
        if self.get_key(target, pattern, kind) in self.rules:
            return True
        return False
        
    def _internal_target(self, front_target):
        """Reverse front target key to internal target field name"""
        return self._target_alias[front_target]
        
    def _internal_kind(self, front_kind):
        """Reverse front kind key to internal lookup kind"""
        return self._kind_alias[front_kind]
        
    def front_to_internal(func):
        def magic(self, target, pattern, kind=DEFAULT_KIND_VALUE[0]):
            target = self._internal_target(target)
            kind = self._internal_kind(kind)
            return func(self, target, pattern, kind)
        return magic
        
    def _add_internal_rule(self, target, pattern, kind):
        """Internal method to add a new rule from the given args"""
        if not self.has_rule(target, pattern, kind):
            key = self.get_key(target, pattern, kind)
            self.rules[key] = (target, pattern, kind)
            self.saved = False
            return True
        return False
        
    def _del_internal_rule(self, target, pattern, kind):
        """Internal method to delete a rule from the given args"""
        if self.has_rule(target, pattern, kind):
            key = self.get_key(target, pattern, kind)
            del self.rules[key]
            self.saved = False
            return True
        return False
        
    @front_to_internal
    def add_rule(self, target, pattern, kind=DEFAULT_KIND_VALUE[1]):
        """Add a new rule from the given args"""
        return self._add_internal_rule(target, pattern, kind)
    
    @front_to_internal
    def del_rule(self, target, pattern, kind=DEFAULT_KIND_VALUE[1]):
        """Del a rule corresponding to the given args"""
        return self._del_internal_rule(target, pattern, kind)
        
    def load(self):
        """
        Clean registry and load rules from the saved filters if author is not 
        anonymous
        """
        if self.author and self.author.is_authenticated():
            self.reset()
            for target, pattern, kind in self.author.filterentry_set.get_filters():
                self._add_internal_rule(target, pattern, kind)
            self.loaded = True
        
    def save(self):
        """Save the memorized rules in database if not allready saved"""
        if not self.saved and self.author and self.author.is_authenticated():
            # Cleanup all previous saved filters
            self.author.filterentry_set.all().delete()
            # Save all rules in memory
            for rule_key, rule_items in self.rules.items():
                print rule_key
                target, pattern, kind = rule_items
                self.author.filterentry_set.create(
                    target=target,
                    kind=kind,
                    value=pattern,
                )
            self.saved = True
        
    def on(self):
        self.active = True
        
    def off(self):
        self.active = False
