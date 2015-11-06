import functools
import re

import jsonschema
from jsonschema import _utils
from jsonschema.compat import iteritems
from jsonschema.exceptions import ValidationError
from jsonschema.validators import Draft4Validator
from jsonschema import validators, _validators


def ssv_validate(instance, schema, instance_cls, cls=None, *args, **kwargs):
    """
    Validate an instance under the given schema.

        >>> validate([2, 3, 4], {"maxItems" : 2})
        Traceback (most recent call last):
            ...
        ValidationError: [2, 3, 4] is too long

    :func:`validate` will first verify that the provided schema is itself
    valid, since not doing so can lead to less obvious error messages and fail
    in less obvious or consistent ways. If you know you have a valid schema
    already or don't care, you might prefer using the
    :meth:`~IValidator.validate` method directly on a specific validator
    (e.g. :meth:`Draft4Validator.validate`).


    :argument instance: the instance to validate
    :argument schema: the schema to validate with
    :argument cls: an :class:`IValidator` class that will be used to validate
                   the instance.

    If the ``cls`` argument is not provided, two things will happen in
    accordance with the specification. First, if the schema has a
    :validator:`$schema` property containing a known meta-schema [#]_ then the
    proper validator will be used.  The specification recommends that all
    schemas contain :validator:`$schema` properties for this reason. If no
    :validator:`$schema` property is found, the default validator class is
    :class:`Draft4Validator`.

    Any other provided positional and keyword arguments will be passed on when
    instantiating the ``cls``.

    :raises:
        :exc:`ValidationError` if the instance is invalid

        :exc:`SchemaError` if the schema itself is invalid

    .. rubric:: Footnotes
    .. [#] known by a validator registered with :func:`validates`
    """
    if cls is None:
        cls = jsonschema.validator_for(schema)
    cls.check_schema(schema)
    instance_cls(schema, *args, **kwargs).validate(instance)


def create_dereffing_validator(instance_resolver):
    """Create a customized Draft4Validator that follows $refs in the schema
    being validated (the Swagger spec for a service). This is not to be
    confused $refs that are in the schema that describes the Swagger 2.0
    specification.

    :param instance_resolver: resolver for the swagger service's spec
    :type instance_resolver: :class:`jsonschema.RefResolver`

    :rtype: Its complicated. See jsonschema.validators.create()
    """
    visisted_refs = {}

    return validators.extend(
        Draft4Validator,
        {
            '$ref': functools.partial(
                dereffing_ref,
                instance_resolver=instance_resolver),
            'properties': functools.partial(
                dereffing_properties_draft4,
                instance_resolver=instance_resolver),
            'additionalProperties': functools.partial(
                dereffing_additionalProperties,
                instance_resolver=instance_resolver),
            'patternProperties': functools.partial(
                dereffing_patternProperties,
                instance_resolver=instance_resolver),
            'type': functools.partial(
                dereffing_type_draft4,
                instance_resolver=instance_resolver),
            'dependencies': functools.partial(
                dereffing_dependencies,
                instance_resolver=instance_resolver),
            'required': functools.partial(
                dereffing_required_draft4,
                instance_resolver=instance_resolver),
            'minProperties': functools.partial(
                dereffing_minProperties_draft4,
                instance_resolver=instance_resolver),
            'maxProperties': functools.partial(
                dereffing_maxProperties_draft4,
                instance_resolver=instance_resolver),
            'allOf': functools.partial(
                dereffing_allOf_draft4,
                instance_resolver=instance_resolver),
            'oneOf': functools.partial(
                dereffing_oneOf_draft4,
                instance_resolver=instance_resolver),
            'anyOf': functools.partial(
                dereffing_anyOf_draft4,
                instance_resolver=instance_resolver),
            'not': functools.partial(
                dereffing_not_draft4,
                instance_resolver=instance_resolver),
        })


def dereffing_patternProperties(validator, patternProperties, instance, schema,
                                instance_resolver, visited_refs=None):
    visited_refs = visited_refs or []

    if not validator.is_type(instance, "object"):
        return

    if '$ref' in instance:
        ref = instance['$ref']
        # if ref in visited_refs:
        #     # Don't recurse into cyclic refs
        #     return
        with instance_resolver.resolving(ref) as target:
            for error in dereffing_patternProperties(
                    validator, patternProperties, target, schema,
                    instance_resolver, visited_refs + [ref]):
                yield error
    else:
        for pattern, subschema in iteritems(patternProperties):
            for k, v in iteritems(instance):
                if re.search(pattern, k):
                    for error in validator.descend(
                        v, subschema, path=k, schema_path=pattern,
                    ):
                        yield error


def dereffing_additionalProperties(validator, aP, instance, schema,
                                   instance_resolver):
    if not validator.is_type(instance, "object"):
        return

    if '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_additionalProperties(
                    validator, aP, target, schema, instance_resolver):
                yield error
    else:
        extras = set(_utils.find_additional_properties(instance, schema))

        if validator.is_type(aP, "object"):
            for extra in extras:
                for error in validator.descend(instance[extra], aP, path=extra):
                    yield error
        elif not aP and extras:
            error = "Additional properties are not allowed (%s %s unexpected)"
            yield ValidationError(error % _utils.extras_msg(extras))


def dereffing_properties_draft4(validator, properties, instance, schema,
                                instance_resolver):
    if not validator.is_type(instance, "object"):
        return

    if '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_properties_draft4(
                    validator, properties, target, schema, instance_resolver):
                yield error
    else:
        for property, subschema in iteritems(properties):
            if property in instance:
                for error in validator.descend(
                    instance[property],
                    subschema,
                    path=property,
                    schema_path=property,
                ):
                    yield error


def dereffing_type_draft4(validator, types, instance, schema,
                          instance_resolver):
    types = _utils.ensure_list(types)

    if isinstance(instance, dict) and '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_type_draft4(
                    validator, types, target, schema, instance_resolver):
                yield error
    else:
        if not any(validator.is_type(instance, type) for type in types):
            yield ValidationError(_utils.types_msg(instance, types))


def dereffing_dependencies(validator, dependencies, instance, schema,
                           instance_resolver):
    if not validator.is_type(instance, "object"):
        return

    if '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_dependencies(
                    validator, dependencies, target, schema,
                    instance_resolver):
                yield error
    else:
        for property, dependency in iteritems(dependencies):
            if property not in instance:
                continue

            if validator.is_type(dependency, "object"):
                for error in validator.descend(
                    instance, dependency, schema_path=property,
                ):
                    yield error
            else:
                dependencies = _utils.ensure_list(dependency)
                for dependency in dependencies:
                    if dependency not in instance:
                        yield ValidationError(
                            "%r is a dependency of %r" % (dependency, property)
                        )


def dereffing_ref(validator, ref, instance, schema, instance_resolver):

    if isinstance(instance, dict) and '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_ref(
                    validator, ref, target, schema, instance_resolver):
                yield error
    else:
        resolve = getattr(validator.resolver, "resolve", None)
        if resolve is None:
            with validator.resolver.resolving(ref) as resolved:
                for error in validator.descend(instance, resolved):
                    yield error
        else:
            scope, resolved = validator.resolver.resolve(ref)
            validator.resolver.push_scope(scope)

            try:
                for error in validator.descend(instance, resolved):
                    yield error
            finally:
                validator.resolver.pop_scope()


def dereffing_required_draft4(validator, required, instance, schema,
                              instance_resolver):
    if not validator.is_type(instance, "object"):
        return

    if '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_required_draft4(
                    validator, required, target, schema, instance_resolver):
                yield error
    else:
        for property in required:
            if property not in instance:
                yield ValidationError("%r is a required property" % property)


def dereffing_minProperties_draft4(validator, mP, instance, schema,
                                   instance_resolver):

    if isinstance(instance, dict) and '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_minProperties_draft4(
                    validator, mP, target, schema, instance_resolver):
                yield error
    else:
        if validator.is_type(instance, "object") and len(instance) < mP:
            yield ValidationError(
                "%r does not have enough properties" % (instance,)
            )


def dereffing_maxProperties_draft4(validator, mP, instance, schema,
                                   instance_resolver):
    if not validator.is_type(instance, "object"):
        return

    if '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_maxProperties_draft4(
                    validator, mP, target, schema, instance_resolver):
                yield error
    else:
        if validator.is_type(instance, "object") and len(instance) > mP:
            yield ValidationError("%r has too many properties" % (instance,))


def dereffing_allOf_draft4(validator, allOf, instance, schema,
                           instance_resolver):

    if isinstance(instance, dict) and '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_allOf_draft4(
                    validator, allOf, target, schema, instance_resolver):
                yield error
    else:
        for index, subschema in enumerate(allOf):
            for error in validator.descend(instance, subschema, schema_path=index):
                yield error


def dereffing_oneOf_draft4(validator, oneOf, instance, schema,
                           instance_resolver):

    if isinstance(instance, dict) and '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_oneOf_draft4(
                    validator, oneOf, target, schema, instance_resolver):
                yield error
    else:
        def remove_jsonReference(oneOf):
            return [
                element
                for element in oneOf
                if not(isinstance(element, dict)
                    and '$ref' in element
                    and element['$ref'].endswith('jsonReference'))
            ]

        oneOf = remove_jsonReference(oneOf)
        subschemas = enumerate(oneOf)
        all_errors = []
        for index, subschema in subschemas:
            errs = list(validator.descend(instance, subschema, schema_path=index))
            if not errs:
                first_valid = subschema
                break
            all_errors.extend(errs)
        else:
            yield ValidationError(
                "%r is not valid under any of the given schemas" % (instance,),
                context=all_errors,
            )

        more_valid = [s for i, s in subschemas if validator.is_valid(instance, s)]
        if more_valid:
            more_valid.append(first_valid)
            reprs = ", ".join(repr(schema) for schema in more_valid)
            yield ValidationError(
                "%r is valid under each of %s" % (instance, reprs)
            )


def dereffing_anyOf_draft4(validator, anyOf, instance, schema,
                           instance_resolver):

    if isinstance(instance, dict) and '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_anyOf_draft4(
                    validator, anyOf, target, schema, instance_resolver):
                yield error
    else:
        all_errors = []
        for index, subschema in enumerate(anyOf):
            errs = list(validator.descend(instance, subschema, schema_path=index))
            if not errs:
                break
            all_errors.extend(errs)
        else:
            yield ValidationError(
                "%r is not valid under any of the given schemas" % (instance,),
                context=all_errors,
            )


def dereffing_not_draft4(validator, not_schema, instance, schema,
                         instance_resolver):

    if isinstance(instance, dict) and '$ref' in instance:
        with instance_resolver.resolving(instance['$ref']) as target:
            for error in dereffing_not_draft4(
                    validator, not_schema, target, schema, instance_resolver):
                yield error
    else:
        if validator.is_valid(instance, not_schema):
            yield ValidationError(
                "%r is not allowed for %r" % (not_schema, instance)
            )
