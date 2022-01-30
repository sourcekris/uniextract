#
# schema.py
# The configuration schema used to validate JSON configurations.

schema = {
    "type" : "object",
    "required" : ["install", "pack", "unpack", "test", "identification"],
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