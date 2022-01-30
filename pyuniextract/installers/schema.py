#
# schema.py
# The configuration schema used to validate JSON configurations.

schema = {
    "type" : "object",
    "required" : ["name", "extensions", "install", "pack", "unpack", "test", "identification"],
    "properties" : {
        "name": {"type" : "string"},
        "extensions": {"type" : "array"},
        "install": {
            "type" : "object",
            "required" : ["method"],
            "properties" : {
                "method": {"enum": ["apt", "source", "pip"]},
                "packages": {"type" : "array"},
                "tool": {"type" : "string"}, 
                "container": {"type" : "string"}, 
                "test_install": {"type" : "boolean"},
                "repo": {"type" : "string"}, 
                "build": {"type" : "string"}, 
                "exist_check": {"type" : "array"},
            },
            "allOf": [
                {
                    "if": {"properties": { "method": { "const": "apt" }}},
                    "then": {"required" : ["method", "packages"]},
                },
                {
                    "if": {"properties": { "method": { "const": "pip" }}},
                    "then": {"required" : ["method", "packages"]},
                },
                {
                    "if": {"properties": { "method": { "const": "source" }}},
                    "then": {"required" : ["method", "repo", "build", "exist_check"]},
                },
            ],
        },
        "pack": {
            "type" : "object",
            "required" : ["type"],
            "properties" : {
                "exe": {"type" : "string"}, 
                "cmdline": {"type" : "string"},
                "type": {"enum" : ["archiver", "dosbox", "blob", "wine"]},
                "blob": {"type" : "string"},
            },
            "allOf": [
                {
                    "if": {"properties": { "type": { "oneOf":[{ "const": "archiver" },{ "const": "dosbox" },{ "const": "wine" }]}}},
                    "then": {"required" : ["type", "exe", "cmdline"]},
                },
                {
                    "if": {"properties": { "type": {"const": "blob"}}},
                    "then": {"required" : ["type", "blob"]},
                },
            ],
        },  
        "unpack": {
            "type" : "object",
            "required" : ["exe", "cmdline", "extension", "force_extension"],
            "properties" : {
                "exe": {"type" : "string"}, 
                "cmdline": {"type" : "string"}, 
                "extension": {"type" : "string"}, 
                "force_extension": {"type" : "boolean"},
            },
        },
        "test": {
            "type" : "object",
            "required" : ["blob", "file", "content", "delete"],
            "dependentRequired" : {
                "padbyte" : ["padlen"],
                "padlen" : ["padbyte"],
            },
            "properties" : {
                "blob": {"type" : "string"}, 
                "file": {"type" : "string"}, 
                "content": {"type" : "string"}, 
                "delete": {"type" : "boolean"},
                "padbyte": {"type" : "string"}, 
                "padlen": {"type" : "number"}, 
            },
        },
        "unpackinstall": {
            "type" : "object",
            "required" : ["method"],
            "properties" : {
                "method": {"enum": ["apt", "source", "pip"]},
                "packages": {"type" : "array"},
                "repo": {"type" : "string"}, 
                "build": {"type" : "string"}, 
                "exist_check": {"type" : "array"},
            },
            "allOf": [
                {
                    "if": {"properties": { "method": { "const": "apt" }}},
                    "then": {"required" : ["method", "packages"]},
                },
                {
                    "if": {"properties": { "method": { "const": "pip" }}},
                    "then": {"required" : ["method", "packages"]},
                },
                {
                    "if": {"properties": { "method": { "const": "source" }}},
                    "then": {"required" : ["method", "repo", "build", "exist_check"]},
                },
            ],
        },
        "identification": {
            "type" : "object",
            "required" : ["file", "trid", "idarc"],
            "properties" : {
                "file": {"type" : "string"}, 
                "trid": {"type" : "string"}, 
                "idarc": {"type" : "string"},
            },
        },
    },
}