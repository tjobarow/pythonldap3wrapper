#!/.venv-linux/bin/ python
# -*-coding:utf-8 -*-
'''
@File    :   ldap3_wrapper.py
@Time    :   2025/01/14 13:00:39
@Author  :   Thomas Obarowski 
@Version :   1.0
@Contact :   tjobarow@gmail.com
@License :   MIT License
@Desc    :   None
'''

import logging
from ldap3 import Server, Connection, ALL, SUBTREE, SIMPLE, ALL_ATTRIBUTES  # noqa: F401
from ldap3 import get_config_parameter
from ldap3.utils.conv import to_unicode, to_raw, escape_bytes
from ldap3.core.exceptions import *  # noqa: F403
from functools import wraps


class Ldap3Wrapper():
    def __init__(
        self,
        ldap_server_host: str,
        bind_cn: str,
        bind_username: str,
        bind_password: str,
        bind_port: int = 389,
        use_ldaps: bool = False
    ):
        """_summary_

        Args:
            ldap_server_host (str): hostname or IP address of LDAP server to connect to
            bind_cn (str): base CN to bind to
            bind_username (str): username in the form of domain/user
            bind_password (str): password of user for binding
            bind_port (int, optional): Port to bind towards. Defaults to 389, unless use_ldaps set to True, then defaults to 636.
            use_ldaps (bool, optional): Communicate via LDAPS. Defaults to False.
        """
        #################################################
        # Get logger function. If there is a parent logger from the calling function,
        # it will attach as a sub-logger (log as callingClass.ServiceNowCmdbWrapper)
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Successfully initalized logging framework.")
        self._logger.info("Initalizing Ldap3Wrapper class...")

        # Initialize protected and private class fields based on init parameters
        self._ldap_server_host: str = ldap_server_host
        self._bind_cn: str = bind_cn
        self.__bind_username: str = bind_username
        self.__bind_password: str = bind_password
        self._use_ldaps: bool = use_ldaps
        self._bind_port: int = bind_port
        self.__ldap_conn: Connection = None
        #Delete the local parameters
        del ldap_server_host, bind_cn, bind_username, bind_password, bind_port, use_ldaps
        self._logger.info("Configured class-specifc fields.")

        # Configure LDAP or LDAPS
        if self._use_ldaps:
            # Update bind port to use 636 for ldaps if a specific bind port is not provided (its set to default)
            self._bind_port = 636 if self._bind_port == 389 else self._bind_port
            self._logger.info(f"Bind set to use LDAPS on port {self._bind_port}")
        else:
            self._logger.info(f"Bind set to use cleartext LDAP on port {self._bind_port}")

        # Bind to LDAP server
        self.bind()
    
    def is_bind_active(func):
        @wraps(func)
        def is_connection_binding_active(self, *args, **kwargs):
            self._logger.debug("Checking if self.__ldap_conn is active.")
            # If the ldap connection is none, or if it's not none, but connection.bound is False, bind it
            if self.__ldap_conn is None or ((self.__ldap_conn) and (not self.__ldap_conn.bound)):
                self._logger.debug(f"LDAP Connection is not bound - binding it now to {self._ldap_server_host}:{self._bind_port}")
                self.bind()
                return func(self, *args, **kwargs)
            else:
                self._logger.debug(f"LDAP Connection is bound to {self._ldap_server_host}:{self._bind_port}")
                return func(self, *args, **kwargs)
        return is_connection_binding_active
    
    def bind(self)-> None:
        if not self.__ldap_conn:
            self._logger.info(f"Setting up binding to {self._ldap_server_host}:{self._bind_port} at BASE CN {self._bind_cn}")
            # Attempt bind to ldap server
            self._logger.debug(f"Configuring ldap3.Server object with host={self._ldap_server_host},port={self._bind_port},use_ssl={self._use_ldaps}")
            self.__server: Server = Server(
                host=self._ldap_server_host,
                port=self._bind_port,
                use_ssl=self._use_ldaps,
            )
            self._logger.debug("Configuring ldap3.Connection object using configured server and SIMPLE authentication strategy, with auto-bind enabled.")
            try:
                self.__ldap_conn: Connection = Connection(server=self.__server, user=self.__bind_username, password=self.__bind_password, authentication=SIMPLE, raise_exceptions=True,auto_range=True)
                self.__ldap_conn.bind()
                self._logger.info(f"Successfully created a new connection binding to {self._ldap_server_host}:{self._bind_port}")
            except Exception as e:
                self._logger.error(e)
        else:
            self._logger.error("Ldap3Wrapper.Bind() called, but the LDAP connection is already bound.")
            
    def unbind(self) -> None:
        self.__ldap_conn.unbind()
        self.__ldap_conn = None
        self._logger.info("Successfully performed unbind operation on LDAP connection.")
    
    def escape_filter_chars(self, text, encoding=None, escape=u'\\*()\0'):
        """ Escape chars mentioned in RFC4515. """
        if encoding is None:
            encoding = get_config_parameter('DEFAULT_ENCODING')
        text = to_unicode(text, encoding)
        for char in escape:
            text = text.replace(char, escape_bytes(to_raw(char)))
        return text
    
    @is_bind_active
    def __ldap_search(self, search_filter: str = "", search_base: str|None = None, search_scope = SUBTREE, returned_attributes = ALL_ATTRIBUTES) -> list:
        # If search_base is not None, then a non-default searchbase was provided, otherwise use the bind cn as the base
        if search_base is None:
            search_base=self._bind_cn

        self._logger.info(f"Searching {search_base} with LDAP filter {search_filter}")
        self.__ldap_conn.search(search_base=search_base, search_filter=search_filter, search_scope=search_scope,attributes=returned_attributes)
        return [dict(resp_obj['attributes']) for resp_obj in self.__ldap_conn.response if 'searchResRef' not in resp_obj['type']]
    
    def search_user_by_email(self, user_email: str, search_base: str|None = None) -> dict:
        # If search_base is not None, then a non-default searchbase was provided, otherwise use the bind cn as the base
        if search_base is None:
            search_base=self._bind_cn
        self._logger.info(f"Searching for user email {user_email} at or below {search_base}")
        escaped_filter: str = self.escape_filter_chars(user_email,escape=u'\\()\0')
        search_filter: str = f"(&(objectClass=user)(mail={escaped_filter}*))"
        returned_records = self.__ldap_search(search_filter=search_filter, search_base=search_base)
        self._logger.info(f"Search returned {len(returned_records)} user objects.")
        return returned_records
    
    def search_user_by_userid(self, user_id: str, search_base: str|None = None) -> dict:
        # If search_base is not None, then a non-default searchbase was provided, otherwise use the bind cn as the base
        if search_base is None:
            search_base=self._bind_cn
        self._logger.info(f"Searching for user email {user_id} at or below {search_base}")
        escaped_filter: str = self.escape_filter_chars(user_id,escape=u'\\()\0')
        search_filter: str = f"(&(objectClass=user)(sAMAccountName={escaped_filter}*))"
        returned_records = self.__ldap_search(search_filter=search_filter, search_base=search_base)
        self._logger.info(f"Search returned {len(returned_records)} user objects.")
        return returned_records
    
    
    
    