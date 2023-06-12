
def json_replace(json_obj, **values):
    """
    Search for elements of `{"{{REPLACE_PARAM}}": "some_key"}` and replace
    with the result of `values["some_key"]`.
    """
    if type(json_obj) is list:
        return [json_replace(x, **values) for x in json_obj]
    elif type(json_obj) is dict:
        new = {}
        for key, value in json_obj.items():
            if type(value) is dict and list(value) == ["{{REPLACE_PARAM}}"]:
                param_name = value["{{REPLACE_PARAM}}"]
                new[key] = values[param_name]
            else:
                new[key] = json_replace(value, **values)
        return new
    else:
        return json_obj