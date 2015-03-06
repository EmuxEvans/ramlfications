# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB

from __future__ import absolute_import, division, print_function

import attr
from six.moves import BaseHTTPServer as httpserver

from .validate import *  # NOQA

HTTP_RESP_CODES = httpserver.BaseHTTPRequestHandler.responses.keys()
AVAILABLE_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'head',
                     'options', 'trace', 'connect']


class RAMLParserError(Exception):
    pass


@attr.s
class RootNode(object):
    """
    API Root Node

    :param str raml_file: string path to RAML file
    :param dict raw: dict of loaded RAML data
    :param str version: API version
    :param str base_uri: API's base URI
    :param list base_uri_params: parameters for base URI, or ``None``
    :param list uri_params: URI parameters that can apply to all resources, \
        or ``None``
    :param list protocols: API-supported protocols, defaults to protocol \
        in ``base_uri``
    :param str title: API Title
    :param list docs: list of :py:class:`parameters.Documentation` objects, \
        or ``None``
    :param list schemas: list of dictionaries, or ``None``
    :param str media_type: default accepted request/response media type, \
        or ``None``
    :param list resource_types: list of :py:class:`ResourceTypeNode`, \
        or ``None``
    :param list traits: list of :py:class:`TraitNode`, or ``None``
    :param list security_schemes: list of \
        :py:class:`parameters.SecurityScheme` objects, or ``None``
    :param list resources: list of :py:class:`ResourceNode` objects, \
        or ``None``
    :param raml_obj: loaded :py:class:`raml.RAMLDict` object
    """
    raml_file        = attr.ib()
    raw              = attr.ib(repr=False)
    version          = attr.ib(repr=False, validator=root_version)
    base_uri         = attr.ib(repr=False, validator=root_base_uri)
    base_uri_params  = attr.ib(repr=False,
                               validator=root_base_uri_params)
    uri_params       = attr.ib(repr=False, validator=root_uri_params)
    protocols        = attr.ib(repr=False, validator=root_protocols)
    title            = attr.ib(repr=False, validator=root_title)
    docs             = attr.ib(repr=False, validator=root_docs)
    schemas          = attr.ib(repr=False, validator=root_schemas)
    media_type       = attr.ib(repr=False, validator=root_media_type)
    resource_types   = attr.ib(repr=False, init=False)
    traits           = attr.ib(repr=False, init=False)
    security_schemes = attr.ib(repr=False, init=False)
    resources        = attr.ib(repr=False, init=False,
                               validator=root_resources)
    raml_obj         = attr.ib(repr=False)


@attr.s
class BaseNode(object):
    """
    :param dict raw: The raw data parsed from the RAML file
    :param RootNode root: Back reference to the node's API root
    :param list headers: List of node's :py:class:`parameters.Header` \
        objects, or ``None``
    :param list body: List of node's :py:class:`parameters.Body` objects, \
        or ``None``
    :param list responses: List of node's :py:class:`parameters.Response`\
        objects, or ``None``
    :param list uri_params: List of node's :py:class:`parameters.URIParameter`\
        objects, or ``None``
    :param list base_uri_params: List of node's base \
        :py:obj:`parameters.URIParameter` objects, or ``None``
    :param list query_params: List of node's \
        :py:class:`parameters.QueryParameter` objects, or ``None``
    :param list form_params: List of node's \
        :py:class:`parameters.FormParameter` objects, or ``None``
    :param str media_type: Supported request MIME media type. Defaults to \
        :py:class:`RootNode`'s ``media_type``.
    :param str description: Description of node.
    :param list protocols: List of ``str`` 's of supported protocols. \
        Defaults to :py:class:`RootNode`'s ``protocols``.
    """
    raw             = attr.ib(repr=False)
    root            = attr.ib(repr=False)
    headers         = attr.ib(repr=False)
    body            = attr.ib(repr=False)
    responses       = attr.ib(repr=False)
    uri_params      = attr.ib(repr=False)
    base_uri_params = attr.ib(repr=False)
    query_params    = attr.ib(repr=False)
    form_params     = attr.ib(repr=False)
    media_type      = attr.ib(repr=False)
    description     = attr.ib(repr=False)
    protocols       = attr.ib(repr=False)


@attr.s
class TraitNode(BaseNode):
    """
    RAML Trait object

    :param str name: Name of trait
    :param str usage: Usage of trait
    """
    name  = attr.ib()
    usage = attr.ib(repr=False)


@attr.s
class ResourceTypeNode(BaseNode):
    """
    RAML Resource Type object

    :param str name: Name of resource type
    :param str type: Name of inherited :py:class:`ResourceTypeNode` object,
        or ``None``.
    :param str method: Supported method. If ends in ``?``, parameters will \
        only be applied to assigned resource if resource implements this \
        method. Else, resource must implement the method.
    :param str usage: Usage of resource type, or ``None``
    :param bool optional: Inherited if resource defines method.
    :param list is\_: List of assigned trait names, or ``None``
    :param list traits: List of assigned :py:class:`TraitNode` objects, \
        or ``None``
    :param str secured_by: List of ``str`` s or ``dict`` s of assigned \
        security scheme, or ``None``. If a ``str``, the name of the security \
        scheme.  If a ``dict``, the key is the name of the scheme, the values \
        are the parameters assigned (e.g. relevant OAuth 2 scopes).
    :param list security_schemes: A list of assigned \
        :py:class:`parameters.SecurityScheme` objects, or ``None``.
    :param str display_name: User-friendly name of resource; \
        defaults to ``name``

    """
    name             = attr.ib()
    type             = attr.ib(repr=False, validator=assigned_res_type)
    method           = attr.ib(repr=False)
    usage            = attr.ib(repr=False)
    optional         = attr.ib(repr=False)
    is_              = attr.ib(repr=False, validator=assigned_traits)
    traits           = attr.ib(repr=False)
    secured_by       = attr.ib(repr=False)
    security_schemes = attr.ib(repr=False)
    display_name     = attr.ib(repr=False)


@attr.s
class ResourceNode(BaseNode):
    """
    Supported API-endpoint (“resource”)

    :param str name: Resource name
    :param ResourceNode parent: parent node object if any, or ``None``
    :param str method: HTTP method for resource, or ``None``
    :param str display_name: User-friendly name of resource; \
        defaults to ``name``
    :param str path: relative path of resource
    :param str absolute_uri: Absolute URI of resource: \
        :py:class:`RootNode`'s ``base_uri`` + ``path``
    :param list is\_: A list of ``str`` s or ``dict`` s of resource-assigned \
        traits, or ``None``
    :param list traits: A list of assigned :py:class:`TraitNode` objects, \
        or ``None``
    :param str type: The name of the assigned resource type, or ``None``
    :param ResourceTypeNode resource_type: The assigned \
        :py:class:`ResourceTypeNode` object
    :param list secured_by: A list of ``str`` s or ``dict`` s of resource-\
        assigned security schemes, or ``None``. If a ``str``, the name of the \
        security scheme.  If a ``dict``, the key is the name of the scheme, \
        the values are the parameters assigned (e.g. relevant OAuth 2 scopes).
    :param list security_schemes: A list of assigned \
        :py:class:`parameters.SecurityScheme` objects, or ``None``.
    """
    name             = attr.ib(repr=False)
    parent           = attr.ib(repr=False)
    method           = attr.ib()
    display_name     = attr.ib(repr=False)
    path             = attr.ib()
    absolute_uri     = attr.ib(repr=False)
    is_              = attr.ib(repr=False, validator=assigned_traits)
    traits           = attr.ib(repr=False)
    type             = attr.ib(repr=False, validator=assigned_res_type)
    resource_type    = attr.ib(repr=False)
    secured_by       = attr.ib(repr=False)
    security_schemes = attr.ib(repr=False)
