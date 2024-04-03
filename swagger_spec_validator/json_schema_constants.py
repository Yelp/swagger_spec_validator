LOCAL_JSON_SCHEMA_STORE = {
    "https://json-schema.org/draft/2019-09/links": {
        "$schema": "https://json-schema.org/draft/2019-09/schema",
        "$id": "https://json-schema.org/draft/2019-09/links",
        "title": "Link Description Object",
        "allOf": [
            {
                "required": [
                    "rel",
                    "href"
                ]
            },
            {
                "$ref": "#/$defs/noRequiredFields"
            }
        ],
        "$defs": {
            "noRequiredFields": {
                "type": "object",
                "properties": {
                    "anchor": {
                        "type": "string",
                        "format": "uri-template"
                    },
                    "anchorPointer": {
                        "type": "string",
                        "anyOf": [
                            {
                                "format": "json-pointer"
                            },
                            {
                                "format": "relative-json-pointer"
                            }
                        ]
                    },
                    "rel": {
                        "anyOf": [
                            {
                                "type": "string"
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "minItems": 1
                            }
                        ]
                    },
                    "href": {
                        "type": "string",
                        "format": "uri-template"
                    },
                    "hrefSchema": {
                        "$ref": "https://json-schema.org/draft/2019-09/hyper-schema",
                        "default": False
                    },
                    "templatePointers": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "string",
                            "anyOf": [
                                {
                                    "format": "json-pointer"
                                },
                                {
                                    "format": "relative-json-pointer"
                                }
                            ]
                        }
                    },
                    "templateRequired": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "uniqueItems": True
                    },
                    "title": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "targetSchema": {
                        "$ref": "https://json-schema.org/draft/2019-09/hyper-schema",
                        "default": True
                    },
                    "targetMediaType": {
                        "type": "string"
                    },
                    "targetHints": {},
                    "headerSchema": {
                        "$ref": "https://json-schema.org/draft/2019-09/hyper-schema",
                        "default": True
                    },
                    "submissionMediaType": {
                        "type": "string",
                        "default": "application/json"
                    },
                    "submissionSchema": {
                        "$ref": "https://json-schema.org/draft/2019-09/hyper-schema",
                        "default": True
                    },
                    "$comment": {
                        "type": "string"
                    }
                }
            }
        }
    },
    "https://json-schema.org/draft/2019-09/hyper-schema": {
        "$schema": "https://json-schema.org/draft/2019-09/hyper-schema",
        "$id": "https://json-schema.org/draft/2019-09/hyper-schema",
        "$vocabulary": {
            "https://json-schema.org/draft/2019-09/vocab/core": True,
            "https://json-schema.org/draft/2019-09/vocab/applicator": True,
            "https://json-schema.org/draft/2019-09/vocab/validation": True,
            "https://json-schema.org/draft/2019-09/vocab/meta-data": True,
            "https://json-schema.org/draft/2019-09/vocab/format": False,
            "https://json-schema.org/draft/2019-09/vocab/content": True,
            "https://json-schema.org/draft/2019-09/vocab/hyper-schema": True
        },
        "$recursiveAnchor": True,
        "title": "JSON Hyper-Schema",
        "allOf": [
            {
                "$ref": "https://json-schema.org/draft/2019-09/schema"
            },
            {
                "$ref": "https://json-schema.org/draft/2019-09/meta/hyper-schema"
            }
        ],
        "links": [
            {
                "rel": "self",
                "href": "{+%24id}"
            }
        ]
    }
}