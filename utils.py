from datetime import datetime

def withTime(fn):
    def wrapWithTime(*args, **kwargs):
        before = datetime.now()
        result = fn(*args, **kwargs)
        after = datetime.now()
        print(f'TimeTaken - {after - before}')
        return result
    return wrapWithTime

to_camel_case = lambda s: s.split('-')[0] + ''.join(word.capitalize() for word in s.split('-')[1:])
# converts string = "x-bundle-version" to xBundleVersion

cleanParts = lambda apiRouteSplit: apiRouteSplit[1:-1] if apiRouteSplit != "" and apiRouteSplit[0] == '{' and apiRouteSplit[-1] == '}' else apiRouteSplit
# converts {afaasdfa} to afaasdfa, i.e. removes curly braces.

pascal_to_camel = lambda s: s if not s else s[0].lower() + s[1:]
# converts ArithmeticError to arithmeticError

camel_to_pascal = lambda s: s if not s else s[0].upper() + s[1:]
# converts arithmeticError to ArithmeticError

toApiName = lambda y: "".join(map(lambda x: camel_to_pascal(cleanParts(x)), y.split("/")))
# converts /ui/lms/{moduleId}/listAllQuiz to UiLmsModuleIdListAllQuiz

getConstantAndVarParts = lambda apiRouteSplit: (apiRouteSplit[1:-1], True) if apiRouteSplit != "" and apiRouteSplit[0] == '{' and apiRouteSplit[-1] == '}' else (apiRouteSplit, False)