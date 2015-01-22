.. swagger spec validator documentation master file, created by
   sphinx-quickstart on Fri May 13 14:16:02 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Swagger Spec Validator
**********************

Introduction
============

Swagger Spec Validator is a Python library that validates *Swagger Specs*
against the `Swagger 1.2`_ or `Swagger 2.0`_ specification.  The validator
aims to check for full compliance with the Specification.


Frequently Asked Questions
==========================

Is the API stable?
------------------

Probably not.  However, it is currently very simple, so it shouldn't be hard to
upgrade code if there's a non backwards-compatible change.

API
===

.. currentmodule:: swagger_spec_validator

.. autoclass:: SwaggerValidationError

.. autofunction:: validate_spec_url


.. _Swagger 1.2: https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md

.. _Swagger 2.0: https://github.com/wordnik/swagger-spec/blob/master/versions/2.0.md