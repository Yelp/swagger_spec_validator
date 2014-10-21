.. swagger spec validator documentation master file, created by
   sphinx-quickstart on Fri May 13 14:16:02 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Swagger Spec Validator
**********************

Introduction
============

Swagger Spec Validator is a Python library that validates *Swagger Specs*
against the `Swagger 1.2 Specification`_.  The validator aims to check
for full compliance with the Specification.


Frequently Asked Questions
==========================

Do you support Swagger 2.0?
---------------------------

No, but this functionality is planned.

Is the API stable?
------------------

Probably not.  However, it is currently very simple, so it shouldn't be hard to
upgrade code if there's a non backwards-compatible change.

API
===

.. currentmodule:: swagger_spec_validator

.. autoclass:: SwaggerValidationError

.. autofunction:: validate_resource_listing_url

.. autofunction:: validate_resource_listing

.. autofunction:: validate_api_declaration


.. _Swagger 1.2 Specification: https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md
