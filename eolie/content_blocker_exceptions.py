# Copyright (c) 2017-2021 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gio

import json

from eolie.define import EOLIE_DATA_PATH
from eolie.logger import Logger


class ContentBlockerExceptions:
    """
        Exception handler
    """
    __JSON_PATH = "%s/content_blocker_json" % EOLIE_DATA_PATH

    def __init__(self, name):
        """
            Init constructor
        """
        try:
            self.__name = name
            self.__rules = []
            f = Gio.File.new_for_path(
                "%s/exceptions_%s.json" % (self.__JSON_PATH, self.__name))
            if f.query_exists():
                (status, contents, tag) = f.load_contents(None)
                if status:
                    self.__rules = json.loads(contents.decode("utf-8"))
        except Exception as e:
            Logger.error("AdblockExceptions::__init__(): %s", e)

    def save(self):
        """
            Save rules to disk
        """
        try:
            f = Gio.File.new_for_path(
                "%s/exceptions_%s.json" % (self.__JSON_PATH, self.__name))
            content = json.dumps(self.__rules)
            f.replace_contents(content.encode("utf-8"),
                               None,
                               False,
                               Gio.FileCreateFlags.REPLACE_DESTINATION,
                               None)
        except Exception as e:
            Logger.error("AdblockExceptions::save(): %s", e)

    def add_domain_exception(self, domain, url_filter=".*", internal=False):
        """
            Add an exception for domain
            @param domain as str
            @param url_filter as str
            @param internal as bool
        """
        if internal:
            rule = self.__get_rule_for_internal_domain(domain, url_filter)
            if rule in self.__rules:
                self.__rules.remove(rule)
        else:
            rule = self.__get_rule_for_domain(domain, url_filter)
            self.__rules.append(rule)

    def remove_domain_exception(self, domain, url_filter=".*", internal=False):
        """
            Remove an exception for domain
            @param domain as str
            @param url_filter as str
            @param internal as bool
        """
        if internal:
            rule = self.__get_rule_for_internal_domain(domain, url_filter)
            self.__rules.append(rule)
        else:
            rule = self.__get_rule_for_domain(domain, url_filter)
            if rule in self.__rules:
                self.__rules.remove(rule)

    def remove_all_domain_exceptions(self, domain):
        """
            Remove all exceptions for a domain
            @param domain as str
        """
        for rule in list(self.__rules):
            if rule["trigger"]["if-domain"] == ["*%s" % domain]:
                self.remove_domain_exception(
                    domain, rule["trigger"]["url-filter"])

    def is_domain_exception(self, domain, url_filter=".*", internal=False):
        """
            True if domain exception exists
            @parma domain as str
            @param url_filter as str
            @param internal as bool
            @return bool
        """
        if internal:
            rule = self.__get_rule_for_internal_domain(domain, url_filter)
            return rule not in self.__rules
        else:
            rule = self.__get_rule_for_domain(domain, url_filter)
            return rule in self.__rules

    @property
    def rules(self):
        """
            Get rules
            @return []
        """
        return self.__rules

#######################
# PRIVATE             #
#######################
    def __get_rule_for_domain(self, domain, url_filter):
        """
            Return rule for domain
            @param domain as str
            @param url_filter as str
            @return {}
        """
        value = "*%s" % domain
        return {
            "trigger": {
                "url-filter": url_filter,
                "if-domain": [value]
            },
            "action": {
                "type": "ignore-previous-rules"
            }
        }

    def __get_rule_for_internal_domain(self, domain, url_filter):
        """
            Return rule for domain
            @param domain as str
            @param url_filter as str
            @return {}
        """
        value = "*%s" % domain
        return {
            "trigger": {
                "url-filter": url_filter,
                "if-domain": [value]
            },
            "action": {
                "type": "block"
            }
        }
