import contextlib
import functools

import jsonschema
from jsonschema.compat import iteritems
from jsonschema.validators import Draft4Validator
from jsonschema import validators, _validators


def validate(instance, schema, instance_cls, cls=None, *args, **kwargs):
    """This is a carbon-copy of :method:`jsonscema.validate` except that it
    takes two validator classes instead of just one. In the jsonschema
    implementation, `cls` is used to validate both the schema and the
    instance. This changes the behavior to have a separate validator for
    each of schema and instance. Schema should not be validated with the
    custom validator returned by :method:`create_dereffing_validator` because
    it follows $refs.

    :param instance: the instance to validate
    :param schema: the schema to validate with
    :param instance_cls: Validator class to validate instance.
    :param cls: Validator class to validate schema.

    :raises:
        :exc:`ValidationError` if the instance is invalid
        :exc:`SchemaError` if the schema itself is invalid
    """
    if cls is None:
        cls = jsonschema.validator_for(schema)
    cls.check_schema(schema)
    instance_cls(schema, *args, **kwargs).validate(instance)


def create_dereffing_validator(instance_resolver):
    """Create a customized Draft4Validator that follows $refs in the schema
    being validated (the Swagger spec for a service). This is not to be
    confused with $refs that are in the schema that describes the Swagger 2.0
    specification.

    :param instance_resolver: resolver for the swagger service's spec
    :type instance_resolver: :class:`jsonschema.RefResolver`

    :rtype: Its complicated. See jsonschema.validators.create()
    """
    visited_refs = {}

    custom_validators = {
        '$ref': dereffing_ref,
        'properties': dereffing_properties_draft4,
        'additionalProperties': dereffing_additionalProperties,
        'patternProperties': dereffing_patternProperties,
        'type': dereffing_type_draft4,
        'dependencies': dereffing_dependencies,
        'required': dereffing_required_draft4,
        'minProperties': dereffing_minProperties_draft4,
        'maxProperties': dereffing_maxProperties_draft4,
        'allOf': dereffing_allOf_draft4,
        'oneOf': dereffing_oneOf_draft4,
        'anyOf': dereffing_anyOf_draft4,
        'not': dereffing_not_draft4,
    }

    bound_validators = {}
    for k, v in iteritems(custom_validators):
        bound_validators[k] = functools.partial(
            v, instance_resolver=instance_resolver,
            visited_refs=visited_refs)

    return validators.extend(Draft4Validator, bound_validators)


@contextlib.contextmanager
def visiting(visited_refs, ref):
    visited_refs[ref] = ref
    try:
        yield
    finally:
        del visited_refs[ref]


def deref_and_call(validator, validator_context, instance, schema,
                   instance_resolver, visited_refs,
                   default_validator_callable):

    if isinstance(instance, dict) and '$ref' in instance:
        ref = instance['$ref']
        if ref in visited_refs:
            print("XXX Found cycle in %s" % ref)
            return
        with visiting(visited_refs, ref):
            with instance_resolver.resolving(ref) as target:
                for error in default_validator_callable(
                        validator, validator_context, target, schema):
                    yield error

    else:
        for error in default_validator_callable(
                validator, validator_context, instance, schema):
            yield error


def dereffing_patternProperties(validator, patternProperties, instance, schema,
                                instance_resolver, visited_refs):

    for error in deref_and_call(
        validator,
        patternProperties,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.patternProperties,
    ):
        yield error


def dereffing_additionalProperties(validator, aP, instance, schema,
                                   instance_resolver, visited_refs):
    for error in deref_and_call(
        validator,
        aP,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.additionalProperties,
    ):
        yield error


def dereffing_properties_draft4(validator, properties, instance, schema,
                                instance_resolver, visited_refs):

    for error in deref_and_call(
        validator,
        properties,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.properties_draft4,
    ):
        yield error


def dereffing_type_draft4(validator, types, instance, schema,
                          instance_resolver, visited_refs):

    for error in deref_and_call(
        validator,
        types,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.type_draft4,
    ):
        yield error


def dereffing_dependencies(validator, dependencies, instance, schema,
                           instance_resolver, visited_refs):

    for error in deref_and_call(
        validator,
        dependencies,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.dependencies,
    ):
        yield error


def dereffing_ref(validator, ref, instance, schema, instance_resolver,
                  visited_refs):

    for error in deref_and_call(
        validator,
        ref,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.ref,
    ):
        yield error


def dereffing_required_draft4(validator, required, instance, schema,
                              instance_resolver, visited_refs):

    for error in deref_and_call(
        validator,
        required,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.required_draft4,
    ):
        yield error


def dereffing_minProperties_draft4(validator, mP, instance, schema,
                                   instance_resolver, visited_refs):

    for error in deref_and_call(
        validator,
        mP,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.minProperties_draft4,
    ):
        yield error


def dereffing_maxProperties_draft4(validator, mP, instance, schema,
                                   instance_resolver, visited_refs):
    for error in deref_and_call(
        validator,
        mP,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.maxProperties_draft4,
    ):
        yield error


def dereffing_allOf_draft4(validator, allOf, instance, schema,
                           instance_resolver, visited_refs):
    # TODO: remove jsonReference from allOf
    for error in deref_and_call(
        validator,
        allOf,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.allOf_draft4,
    ):
        yield error


def dereffing_oneOf_draft4(validator, oneOf, instance, schema,
                           instance_resolver, visited_refs):
    # TODO: remove jsonReference from allOf
    for error in deref_and_call(
        validator,
        oneOf,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.oneOf_draft4,
    ):
        yield error
        # def remove_jsonReference(oneOf):
        #     return [
        #         element
        #         for element in oneOf
        #         if not(isinstance(element, dict)
        #             and '$ref' in element
        #             and element['$ref'].endswith('jsonReference'))
        #     ]
        #
        # oneOf = remove_jsonReference(oneOf)


def dereffing_anyOf_draft4(validator, anyOf, instance, schema,
                           instance_resolver, visited_refs):
    # TODO: remove jsonReference from anyOf
    for error in deref_and_call(
        validator,
        anyOf,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.anyOf_draft4,
    ):
        yield error


def dereffing_not_draft4(validator, not_schema, instance, schema,
                         instance_resolver, visited_refs):
    for error in deref_and_call(
        validator,
        not_schema,
        instance,
        schema,
        instance_resolver,
        visited_refs,
        _validators.not_draft4,
    ):
        yield error
