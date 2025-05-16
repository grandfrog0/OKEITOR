import builtins


class MyFunctions:
    def __init__(self):
        pass

    # pattern: 'int int'
    def type_of(self, text, pattern, edit=True):
        elements = text.strip().split()
        if edit and elements[0].startswith('/'):
            elements = elements[1:]
        pattern_elements = pattern.strip().split()

        if len(elements) != len(pattern_elements):
            return MFTypeOfObject(False)

        objects = []
        try:
            for i in range(len(pattern_elements)):
                objects += [getattr(builtins, pattern_elements[i])(elements[i])]
        except (ValueError, TypeError):
            return MFTypeOfObject(False)

        return MFTypeOfObject(True, objects)


class MFTypeOfObject:
    def __init__(self, result, objects=[]):
        self.result = result
        self.objects = objects

    def __bool__(self):
        return self.result

    def __getitem__(self, item):
        return self.objects[item]

    def __str__(self):
        return str(self.result) + ' ' + str(self.objects)