# J2J #

> J2J is a rule engine library that helps in converting one form of JSON into another by applying some rules on top of the input JSON.

J2J is a thin layer that sits on top of the application layer converting the input JSON into the expected JSON. It'll be helpful when the request data POSTed on to the server is different from what the application expects.

> **For eg:**- Let us consider, you have designed a base platform which has exposed some of its APIs. Now, due to some (business partnership)
> reasons, the client cannot POST the data as per the expected format.
> Use J2J to convert the input JSON into expected JSON **WITHOUT
> CHANGING YOUR APIs** for a specific business partner.

## Installation ##

    pip install j2j

## Quick start ##


    import j2j
    
    input = {
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
    
    rules = {
        "rules": [
            {
                "base_elem": "/",
                "changes": {
                    "newk1": "k1",
                    "newk2": "k2@0",
                    "k3.newa": "k3.a",
                    "k4.newa.newb": "k4.a.b"
                },
                "keep_others": True,
                "make_base": False,
                "new_key_elem": "/"
            }
    
        ]
    }
    
    >>> print(j2j.convert(input, rules))

    {'newk1': 'v1', 'k3': {'newa': 1}, 'k4': {'newa': {'newb': 3}}, 'newk2': 'v40'}



## Configuration ##

### Splitters

* To split by dict, use `.`

* To split by array, use `@`

* Root Element is `/`

* End of array is `$`

* All items is `*`

### Rule Configuration

* `base_element` - **For future use.** Element(or key) where you want to start the navigation.

For eg, for the above `input`, if `base_element` is set as `k4`, then the changes will be done only inside the element `k4`. Rest will remain unchanged (if `keep_others` is `True`, else output will only return the changes done inside `k4`).

* `keep_others` - **For future use.** Setting to keep other `keys` in the output along with the changes done.

* `new_key_elem` - **For future use.** Useful when `base_elem` is some key other than root element.

* `make_base` - **For future use.**

* `changes` - Include changes that need to be done on the input JSON.

For the above applied `rules`, following changes will be made.

    1) A new key `newk1` will be created having the value of `k1`.
    
    2) A new key `newk2` will be created having the value of the `0th` index of `k2`
    
    3) `k3.newa` means a new key `newa` will be created inside `k3` having value `k3.a`.

## Recommendations

* Create a separate `rules.json` file, read it and then pass the `loaded` json to the function.

Use the following settings for the time-being. Working on their implementations.

* `base_elem` as root element `\`.

* `keep_others` as `True`.

* `make_base` as `True`.

* `base_elem` as root element `\`.


## TODO ##
* Apply multiple rules on the same input JSON. (Work in Progress)

* `keep_others` when base element is root (`\`).

* Create new keys by concatenating 2 or more keys.


## Contribution Guidelines

* Writing tests - Always welcome to improve on this.

* Other guidelines - Feel free to suggest any more feature or raise a PR to contribute in fixing bugs.

