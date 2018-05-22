
import j2j

ijson = {
    "k1": "v1",
    "k2": ["v40", "v41", "v42", "v43", "v44", "v45"],
    "k3": {
        'a': 1
    },
    "k4": {
        'a': {
            'b': 3
        }
    }
}

rjson = {
    "rules": [
        {
            "base_elem": "/",
            "changes": {
                "newk1": "k1",
                "newk2": "k2@0",
                "k3.newa": "k3.a",
                "k4": "k4.a.b"
            },
            "keep_others": True,
            "make_base": False,
            "new_key_elem": "/"
        }

    ]
}

print(j2j.convert(ijson, rjson))
