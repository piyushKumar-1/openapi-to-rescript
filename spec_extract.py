import re
import json
import time
import os
import sys
import utils as U

# Constants
rescriptTypeMap = {
    'String': 'string',
    'Integer': 'int',
    'Boolean': 'bool',
    'Number': 'float',
    'baseUrl': 'string',
    'uTCTime': 'string',
    'highPrecDistance': 'float',
    'highPrecMoney': 'float',
    'centesimal': 'string',
    'double': 'float'
}

deduplicateEnumsHelper = {}

def getKey(keyString, value):
    return { 'key': keyString, 'value': value}

# ENUM template variables
def ENUM_NAME(value): return getKey("<ENUM-NAME>", value)
def CAP_ENUM_NAME(value): return getKey("<CAP-ENUM-NAME>", value)
def ENUM_VALUES(value): return getKey("<POSSIBLE-VALUES>", value)
def ENUM_DECODE_FUNCTION_NAME(value): return getKey("<ENUM-DECODE-FUNCTION-NAME>", value)
def ENUM_DECODE_CODE(value): return getKey("<ENUM-DECODE-CODE>", value)
def ENUM_ENCODE_CODE(value): return getKey("<ENUM-ENCODE-CODE>", value)
def ENUM_DEFAULT_VALUE(value): return getKey("<ENUM-DEFAULT-VALUE>", value)

# SHARED-TYPE template variables
def TYPE_NAME(value): return getKey("<TYPE-NAME>", value)
def TYPE_SCHEMA(value): return getKey("<TYPE-SCHEMA>", value)
def CAP_TYPE_NAME(value): return getKey("<CAP-TYPE-NAME>", value)
def DECODE_CODE(value): return getKey("<DECODE-CODE>", value)

# defualt-field value template variables
def FIELD_NAME_GETTER(value): return getKey("<FIELD-NAME-GETTER>", value)
def FIELD_TYPE(value): return getKey("<FIELD-TYPE>", value)
def DEFAULT_VALUE(value): return getKey("<DEFAULT-VALUE>", value)

# API-TYPE template variables
def API_NAME(value): return getKey("<API-NAME>", value)
def API_ENDPOINT(value): return getKey("<API-ENDPOINT>", value)
def METHOD(value): return getKey("<METHOD>", value)
def REQUEST_BODY_CODE(value): return getKey("<REQUEST-BODY-CODE>", value)
def INPUTS(value): return getKey("<INPUTS>", value)
def CAP_RESPONSE_TYPE(value): return getKey("<CAP-RESPONSE-TYPE>", value)
def CAP_API_NAME(value): return getKey("<CAP-API-NAME>", value)
def QUERY_PARAM_CODE(value): return getKey("<QUERY-PARAM-CODE>", value)

class CodeGenerator:
    def __init__(self) -> None:
        self.fieldNamePattern = "<FIELD_NAME>"
        self.queryParamCodeHelper = {
            'int': '->Js.Int.toString',
            'bool': '->Js.Bool.toString',
            'float': '->Js.Float.toString',
        }
        self.typeDecodeCode = {}
        self.defaultValueGetterPattern = "<DEFAULT_VALUE_GETTER>"
        self.importsPatternList = {
            '.*Enums.*': ['open Enums'],
            'defaultImports': ['open Utils']
        }
        self.typeDecodeFunctions = {
            'string': f'{self.fieldNamePattern}: getOptionString(dict, "{self.fieldNamePattern}") -> Option.getExn',
            'option<string>': f'{self.fieldNamePattern}: getOptionString(dict, "{self.fieldNamePattern}")',
            'float': f'{self.fieldNamePattern}: getOptionFloat(dict, "{self.fieldNamePattern}") -> Option.getExn',
            'option<float>': f'{self.fieldNamePattern}: getOptionFloat(dict, "{self.fieldNamePattern}")',
            'bool': f'{self.fieldNamePattern}: getOptionBool(dict, "{self.fieldNamePattern}") -> Option.getExn',
            'option<bool>': f'{self.fieldNamePattern}: getOptionBool(dict, "{self.fieldNamePattern}")',
            'int': f'{self.fieldNamePattern}: getOptionInt(dict, "{self.fieldNamePattern}") -> Option.getExn',
            'option<int>': f'{self.fieldNamePattern}: getOptionInt(dict, "{self.fieldNamePattern}")',
            'array': f'{self.fieldNamePattern}: dict->Utils.getArray(key)->Array.filterMap(<DECODE_TYPE_FUNCTION>)',
            'option<array>': f'{self.fieldNamePattern}: getOptionArray(dict, "{self.fieldNamePattern}")',
        }

    def withNoneImports(self, string):
        return (string, [])

    def convertToSchema(self, typeName, typeSchema):
        res = []
        def getType(field, typeField):
            rescriptType = typeField
            if isinstance(typeField, str):
                if typeField in rescriptTypeMap:
                    rescriptType = rescriptTypeMap[typeField]
                if field not in typeSchema['required']:
                    rescriptType = "option<" + rescriptType + ">"
                return (rescriptType, None)
            else:
                if 'type' in typeField and typeField['type'] == 'enum':
                    nestedTypeName = typeField['type_name']
                else:
                    nestedTypeName = U.pascal_to_camel(typeField['type_name'] if 'type_name' in typeField else f"{field}Type")
                if nestedTypeName in rescriptTypeMap:
                    nestedTypeName = rescriptTypeMap[nestedTypeName]
                    return (nestedTypeName, None)
                return (nestedTypeName, self.convertToSchema(nestedTypeName, typeField))
        rescriptFieldTypes = {}
        for i, j in typeSchema['properties'].items():
            if i == 'ARRAY_VAL':
                rescriptFieldTypes = {'rescriptType':  f"array<{j['array_item_type']}>", 'directThing': True, 'type': 'array', 'objectType': j['array_item_type']}
            else:
                (rescriptTypeName, nestedTypeSchema) = getType(i, j)
                rescriptFieldTypes[i] = rescriptTypeName
                if nestedTypeSchema: res = res + nestedTypeSchema
            if rescriptFieldTypes == {}:
                return res
            res.append({ typeName: rescriptFieldTypes})
        return res

    def generateDecodeString(self, fieldName, typeName):
        typeFileName = U.camel_to_pascal(typeName)
        typeDetails = all_types[typeFileName] if typeFileName in all_types else {}
        return f"// {fieldName}: FailedToGenerateFor({typeName})"

    def generateDecodeCodeAndGetImportsList(self, typeName, typeSchema):
        decodeStringList = []
        imports = []
        if isinstance(typeSchema, dict):
            if 'directThing' in typeSchema:
                typeName = typeSchema['rescriptType']
                objectType = typeSchema['objectType']
                decodeString = ""
                if typeSchema['type'] == 'array':
                    decodeString = "\n\t\t -> ".join(["dict", "JSON.Decode.array", "Option.getOr([])", "Array.filterMap(JSON.Decode.object)", f"Array.map(x => decode{U.camel_to_pascal(objectType)}(x))"])
                # elif
                imports = self.importsPatternList[typeName] if typeName in self.importsPatternList else self.tryPatternBasedImport(typeName)
                return (decodeString, imports)
            else:
                for i, j in typeSchema.items():
                    defaultValueGetter = f"default{U.camel_to_pascal(i)}"
                    (needsDefault, rescriptDecodeString, importForField) = self.getTypeDecodeString(i, j, defaultValueGetter)
                    imports += importForField
                    if needsDefault:
                        required_defaults[typeName] = {} if typeName not in required_defaults else required_defaults[typeName]
                        required_defaults[typeName][defaultValueGetter] = j
                    decodeStringList.append(rescriptDecodeString)
                ds = " -> \n\t\t\t".join(["data", "JSON.Decode.object", "Option.getOr(Dict.make())", "(dict => {\n\t\t\t\t" + ",\n\t\t\t\t".join(decodeStringList) + "\n\t\t\t})\n\t\t"]) # CODE FOR TYPES DECODE GENERATION
                return (ds, imports)
            
        

    def getQueryParamPathString(self, parameter, parameterInfo, resolvedType):
        if parameterInfo['required']:
            toStringRescriptCode = self.queryParamCodeHelper[resolvedType] if resolvedType in self.queryParamCodeHelper else ""
            pathString = f'"{parameter}=" ++ {parameter}{toStringRescriptCode}'
        else:
            toStringRescriptCode = self.queryParamCodeHelper[resolvedType] if resolvedType in self.queryParamCodeHelper else ""
            pathString = f'Option.mapWithDefault({parameter}, "", x => "{parameter}=" ++ x{toStringRescriptCode})'
        return pathString

    def getParamaterType(self, parameterInfo):
        parameterType = parameterInfo['type']
        if parameterType in rescriptTypeMap:
            parameterType = rescriptTypeMap[parameterType]
        else:
            parameterType = U.pascal_to_camel(parameterType)
        return (parameterType if parameterInfo['required'] else f"option<{parameterType}>", parameterType)
        

    def generateApiCalls(self, apiTypes, templates):
        apiCodeOutput = {}
        for apiEndpoint, apiMethods in apiTypes.items():
            apiName_ = U.toApiName(apiEndpoint)
            for apiMethod in apiMethods:
                method = apiMethod["method"] if "method" in apiMethod else ""
                apiName=apiName_ + method
                apiEndpointCodeSplit = map(U.getConstantAndVarParts, apiEndpoint.split('/'))
                pathParts = []
                partt = []
                for (pathSplit, isVariable) in apiEndpointCodeSplit:
                    if isVariable:
                        pathParts.append(f'\"{"/".join(partt)}\"')
                        pathParts.append(pathSplit)
                        partt = []
                    else:
                        partt.append(pathSplit)
                pathParts.append(f'\"{"/".join(partt)}\"')
                apiEndpointCode = " ++ \"/\" ++ ".join(pathParts)
                inputs = []
                importForRequest = importForResponse = []
                queryParams = []
                for parameter, parameterInfo in apiMethod['parameters'].items():
                    parameterInfo['in']
                    (rescriptInputType, rawType) = self.getParamaterType(parameterInfo)
                    if parameterInfo['in'] == 'query':
                        queryParamPathString = self.getQueryParamPathString(parameter, parameterInfo, rawType)
                        queryParams.append(queryParamPathString)
                    smallInputType = U.pascal_to_camel(rescriptInputType)
                    inputImport = self.importsPatternList[smallInputType] if smallInputType in self.importsPatternList else self.tryPatternBasedImport(smallInputType)
                    importForRequest += inputImport
                    inputs.append(f'{U.to_camel_case(parameter)}: {rescriptInputType}')
                if len(queryParams) > 0:
                    queryParamCode = " ++ \n\t\t\t\"&\" ++ ".join(queryParams)
                    apiEndpointCode += " ++ {\n\t\t  " + f'"?" ++ {queryParamCode}' + "\n\t\t}"
                requestBodyCode = ""
                requestType = (apiMethod.get("request_type") or {}).get("type_name")
                responseType = (apiMethod.get("response_type") or {}).get("type_name")
                smallRequestType = U.pascal_to_camel(requestType)
                smallResponseType = U.pascal_to_camel(responseType)
                if requestType != None:
                    requestBodyCode = f"~body=body->{requestType}.toJson"
                    inputs.append(f"body: {smallRequestType}")
                replacements = [CAP_RESPONSE_TYPE(responseType),REQUEST_BODY_CODE(requestBodyCode), API_NAME(U.pascal_to_camel(apiName)), CAP_API_NAME(apiName), METHOD(method), INPUTS(", ".join(inputs)), API_ENDPOINT(apiEndpointCode)]
                apiTemplate = templates['template']
                outFile = templates['outFile']
                for i in replacements:
                    apiTemplate = apiTemplate.replace(i['key'], i['value'])
                    outFile = outFile.replace(i['key'], i['value'])
                if smallRequestType != None:
                    importForRequest = self.importsPatternList[smallRequestType] if smallRequestType in self.importsPatternList else self.tryPatternBasedImport(smallRequestType)
                if smallResponseType != None:
                    importForResponse = self.importsPatternList[smallResponseType] if smallResponseType in self.importsPatternList else self.tryPatternBasedImport(smallResponseType)
                generateCodeFile = {'codeFromTemplate': [apiTemplate], 'imports': importForRequest + importForResponse }
                apiCodeOutput[outFile] = generateCodeFile
        return apiCodeOutput

    def addTypeImportsPatternAndDecodeFunction(self, typeName): # write/update rescipt code generated here for all types.
        typeName = U.camel_to_pascal(typeName)
        rescriptTypeName = U.pascal_to_camel(typeName)
        if rescriptTypeName not in self.typeDecodeCode:
            self.addToImportsPatternList(f".*{rescriptTypeName}.*", [f"open {typeName}"])
            self.addToImportsPatternList(f"{rescriptTypeName}", [f"open {typeName}"])
            self.addToImportsPatternList(f"option<{rescriptTypeName}>", [f"open {typeName}"])
            self.addTypeDecodeString(rescriptTypeName, f"{self.fieldNamePattern}: dict -> Dict.getExn(\"{self.fieldNamePattern}\") -> decode{typeName} -> Result.getExn")
            self.addTypeDecodeString(f"option<{rescriptTypeName}", f"{self.fieldNamePattern}: dict -> Dict.get(\"{self.fieldNamePattern}\") -> Option.mapWithDefault(x => decode{typeName}(x))")
            self.addTypeDecodeString(f"array<{rescriptTypeName}>", f"{self.fieldNamePattern}: dict -> Dict.get(\"{self.fieldNamePattern}\") -> Option.getOr([]) -> Array.map(x => decode{typeName}(x) -> Result.getExn)")
    
    def generateDecodeForAllTypes(self, allTypes, typesTemplate):
        decodeFunctions = {}
        cacheTypeResults = {}
        for typeName, typeSchema in allTypes.items():
            if typeName is not None:
                types = self.convertToSchema(typeName, typeSchema)
                for rescriptTypeObj in types:
                    rescriptType = list(rescriptTypeObj.keys())[0]
                    rescriptTypeObject = rescriptTypeObj[rescriptType]
                    (decodeCode, imports) = cacheTypeResults[rescriptType] if rescriptType in cacheTypeResults else self.generateDecodeCodeAndGetImportsList(rescriptType, rescriptTypeObject)
                    cacheTypeResults[rescriptType] = (decodeCode, imports)
                    if 'directThing' in rescriptTypeObject:
                        rescriptTypeSchema = rescriptTypeObject['rescriptType']
                    else:
                        rescriptTypeSchema = "{\n\t" + ",\n\t".join([f"{i}: {j}" for i, j in rescriptTypeObject.items()]) + "\n}"
                    if rescriptTypeSchema is not None:
                        replacements = [TYPE_NAME(U.pascal_to_camel(rescriptType)),TYPE_SCHEMA(rescriptTypeSchema),CAP_TYPE_NAME(U.camel_to_pascal(rescriptType)),DECODE_CODE(decodeCode)]
                        sharedTypesCodeFile = typesTemplate['template']
                        outFile = typesTemplate['outFile']
                        for i in replacements:
                            sharedTypesCodeFile = sharedTypesCodeFile.replace(i['key'], i['value'])
                            outFile = outFile.replace(i['key'], i['value'])
                        generateCodeFile = {'codeFromTemplate': [sharedTypesCodeFile], 'imports': imports }
                        self.addTypeImportsPatternAndDecodeFunction(rescriptType)
                        decodeFunctions[outFile] = generateCodeFile
        return decodeFunctions

    def getTypeDecodeString(self, fieldName, typeName, defaultValueGetter):
        decodeString = self.typeDecodeFunctions[typeName] if typeName in self.typeDecodeFunctions else self.generateDecodeString(fieldName, typeName)
        decodeStringWithFieldName = decodeString.replace(self.fieldNamePattern, fieldName)
        decodeStringWithFieldNameAndDefault = decodeStringWithFieldName.replace(self.defaultValueGetterPattern, defaultValueGetter)
        importForField = self.importsPatternList[typeName] if typeName in self.importsPatternList else self.tryPatternBasedImport(typeName)
        return (decodeStringWithFieldNameAndDefault != decodeStringWithFieldName,decodeStringWithFieldNameAndDefault, importForField)

    def addToImportsPatternList(self, typePattern, importFileName):
        self.importsPatternList[typePattern] = importFileName
    
    def addQueryParamCodeHelper(self, enumName, enumEncodeCode):
        self.queryParamCodeHelper[enumName] = enumEncodeCode

    def tryPatternBasedImport(self, typeName):
        if typeName in rescriptTypeMap.values():
            return []
        for patternString in self.importsPatternList:
            if re.match(patternString, typeName) != None:
                return self.importsPatternList[patternString]
        return []
    
    def addTypeDecodeString(self, type, decodeString):
        self.typeDecodeFunctions[type] = decodeString

TEMPLATE_FOLDER_NAME = "ny-integration-templates"
MAX_FILES_TO_CHECK = 100
RED_COLOR = "\033[31m"
RESET_COLOR = "\033[0m"
GREEN_COLOR = "\033[32m"

# Global variables
all_types = {}
all_prop_types = {}  # analytics
all_enums = {}
required_defaults = {}
generated = {}


def resolve_ref(ref, spec):
    """Resolve a reference to its schema in the spec."""
    ref_path = ref.split('/')[1:]
    resolved = spec
    type_name = None
    for part in ref_path:
        resolved = resolved.get(part)
        type_name = part
        if resolved is None:
            break
    return {'res': resolved, 'type_name': type_name}


def get_schema_type(schema_det, spec, resolved_refs=None):
    """Extract and resolve the schema type."""
    schema = schema_det['res']
    if resolved_refs is None:
        resolved_refs = {}

    required = []
    schema_type = {}
    api_name = schema_det.get('path')
    type_name = schema_det.get('type_name')

    if schema.get('type') == 'string' and 'enum' in schema:
        all_enums[type_name] = schema['enum']
        return {'type': 'enum', 'properties': {}, 'required': [], 'type_name': f"{type_name}.{U.pascal_to_camel(type_name)}"}
    elif schema.get('type') == 'string':
        return {'type': 'string', 'properties': {}, 'required': [], 'type_name': "String"}
    elif schema.get('type') == 'array':
        itemsRef = (schema.get('items') or {}).get('$ref')
        if itemsRef == None:
            itemsType = (schema.get('items') or {})
        else:
            resolvedItem = resolve_ref(itemsRef, spec)
            resolvedItem['path'] = api_name
            itemsType = get_schema_type(resolvedItem, spec, resolved_refs)
        arrayTypeName = f"{itemsType['type_name']}Array"
        result = {'type': 'array', 'properties': {}, 'required': [], 'type_name': arrayTypeName, 'array_item_type': U.pascal_to_camel(itemsType['type_name'])}
        all_types[arrayTypeName] = {
            'properties': {'ARRAY_VAL': result},
            'required': [],
            'count': all_types.get(arrayTypeName, {}).get('count', 0) + 1
        }
        return result
    elif schema.get('type') == 'object' and 'properties' in schema:
        properties = schema['properties']
        required = schema.get('required', [])

        for prop, prop_details in properties.items():
            if '$ref' in prop_details:
                nested_schema = resolve_ref(prop_details['$ref'], spec)
                nested_schema['path'] = api_name
                prop_type = get_schema_type(nested_schema, spec, resolved_refs)
            elif 'type' in prop_details and prop_details['type'] == 'array':
                toResovle = {'res': prop_details['items'], 'path': api_name}
                resoled_schema = get_schema_type(toResovle, spec, resolved_refs)
                prop_type = f"array<{U.pascal_to_camel(resoled_schema['type_name'])}>"
            else:
                prop_type = prop_details.get('type', 'unknown').capitalize()

            if isinstance(prop_type, str) or (isinstance(prop_type, dict) and prop_type.get('type') == 'enum'):
                prop_key = str(json.dumps(prop_type)).replace('"', '') if isinstance(prop_type, dict) else prop_type
                all_prop_types[prop_key] = {'usedIn': [api_name], 'count': all_prop_types.get(prop_key, {}).get('count', 0) + 1}

            schema_type[prop] = prop_type

    elif '$ref' in schema:
        ref_key = schema['$ref']
        if ref_key not in resolved_refs:
            resolved_schema = resolve_ref(ref_key, spec)
            resolved_schema['path'] = api_name
            nested_type = get_schema_type(resolved_schema, spec, resolved_refs)
            resolved_refs[ref_key] = nested_type

        return resolved_refs[ref_key]

    all_types[type_name] = {
        'properties': schema_type,
        'required': required,
        'count': all_types.get(type_name, {}).get('count', 0) + 1
    }

    return {'type': 'object', 'properties': schema_type, 'required': required, 'type_name': type_name}


def extract_parameters(path, parameters, avoidHeaders):
    """Extract parameters from the request."""
    param_details = {}
    for param in parameters:
        param_name = param['name']
        if param['in'] == 'header' and param_name in avoidHeaders:
            continue
        param_type = param['schema'].get('type', 'unknown').capitalize()
        if 'enum' in param['schema']:
            enumValues = str(sorted(param['schema']['enum']))
            enumName = deduplicateEnumsHelper[enumValues] if enumValues in deduplicateEnumsHelper else U.toApiName(path) + U.camel_to_pascal(param['name'])
            deduplicateEnumsHelper[enumValues] = enumName
            all_enums[enumName] = param['schema']['enum']
            param_type = enumName
        param_details[param_name] = {
            'in': param['in'],
            'type': param_type,
            'required': param['required']
        }
    return param_details


def extract_request_response_types(spec, avoidHeaders, apiList):
    """Extract request and response types from the API spec."""
    api_types = {}

    for apiEndpoint, methods in spec.get('paths', {}).items():
        if apiEndpoint in apiList and (apiEndpoint.startswith("/v2") or apiEndpoint.startswith("/ui")):
            path = apiEndpoint.replace("/v2", "").replace("/ui","")
            for method, details in methods.items():
                request_type = None
                response_type = None
                resolved_refs = {}
                parameters = extract_parameters(path, details.get('parameters', []), avoidHeaders)

                if 'requestBody' in details:
                    content = details['requestBody'].get('content', {})
                    if content:
                        media_type = list(content.keys())[0]
                        schema = content[media_type].get('schema', {})
                        request_type = get_schema_type({'res': schema, 'path': path}, spec, resolved_refs) if '$ref' in schema else get_schema_type({'res': schema, 'path': path}, spec)

                if 'responses' in details:
                    responses = details['responses']
                    if '200' in responses and 'content' in responses['200']:
                        response_content = responses['200']['content']
                        media_type = list(response_content.keys())[0]
                        schema = response_content[media_type].get('schema', {})
                        response_type = get_schema_type({'res': schema, 'path': path}, spec, resolved_refs) if '$ref' in schema else get_schema_type({'res': schema, 'path': path}, spec)                            

                parsed_result = {
                    'method': U.camel_to_pascal(method),
                    'request_type': request_type,
                    'parameters': parameters,
                    'response_type': response_type
                }

                if path not in api_types:
                    api_types[path] = []
                api_types[path].append(parsed_result)

    return api_types


def categorize_types(api_types):
    """Categorize types into shared and specific types."""
    return {
        'apis': api_types,
        'all-types': all_types,
        'enums': all_enums
    }


def countdown(n, message):
    """Display a countdown message."""
    for i in range(n, 0, -1):
        sys.stdout.write(f"\r{message} in {i}s{RESET_COLOR}")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n")  # Clean up the line


def find_templates_directory(start_dir='.'):
    """Find the templates directory."""
    current_dir = os.path.abspath(start_dir)
    while True:
        count = 0
        for dirpath, dirnames, _ in os.walk(current_dir):
            print(f"Finding template folder: {TEMPLATE_FOLDER_NAME} in {dirpath}")
            count += 1
            if count > MAX_FILES_TO_CHECK:
                break
            if TEMPLATE_FOLDER_NAME in dirnames:
                return os.path.join(dirpath, TEMPLATE_FOLDER_NAME)
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        if current_dir == parent_dir:
            break
        countdown(3, f"\r{RED_COLOR}Missing {TEMPLATE_FOLDER_NAME} in current directory {current_dir}, looking in parent folder {parent_dir}")
        current_dir = parent_dir
    return None


def read_templates(template_folder_path):
    """Read and process template files."""
    path_split = template_folder_path.split("/")
    files = [f for f in os.listdir(template_folder_path) if os.path.isfile(os.path.join(template_folder_path, f))]
    templates = {}
    out_file_pattern = re.compile(r'<OUT=(.*)>')
    going_back_pattern = re.compile(r'\.\./')

    for template_file_name in files:
        with open(os.path.join(template_folder_path, template_file_name), "r") as f:
            content = f.read()
            template_key_name = template_file_name.replace(".template", "")
            if template_file_name.endswith(".template"):
                out_file_pattern_string = out_file_pattern.search(content)
                if out_file_pattern_string == None:
                    print(f"please add OUT file line in your template file {template_key_name}")
                else:
                    out_file = out_file_pattern_string.group(1)
                    clean_content = content.replace(out_file_pattern.pattern.replace('(.*)', out_file), "")
                    go_back_from_template_dir = len(going_back_pattern.findall(out_file))
                    out_file_path = "/".join(path_split[:-go_back_from_template_dir]) + "/" + out_file.replace("../", "")
                    templates[template_key_name] = {
                        "template": clean_content,
                        "outFile": out_file_path
                    }
            else: 
                ah = al = []
                try:
                    integrationConfig = json.loads(content) 
                    if 'avoidHeaders' in integrationConfig:
                        ah = integrationConfig['avoidHeaders']
                    if 'apiList' in integrationConfig:
                        al = integrationConfig['apiList']
                except:
                    print(f"something wrong in your template file {template_file_name}")
                templates[template_key_name] = (ah, al)
    return templates


def get_templates():
    """Get templates from the templates directory."""
    template_folder = find_templates_directory('.')
    if not template_folder:
        print(f"{RED_COLOR}Template folder not found. Create a folder {GREEN_COLOR}{TEMPLATE_FOLDER_NAME}{RESET_COLOR} {RED_COLOR}in your project root directory with relevant files for generating code.{RESET_COLOR}")
        exit(1)
    return read_templates(template_folder)

def write_rescript(rescriptModules):
    for outFile in rescriptModules:
        if outFile:
            moduleCode = rescriptModules[outFile]['codeFromTemplate']
            moduleImports = list(set(rescriptModules[outFile]['imports']))
            finalCode = ["\n".join(moduleImports)] + ["\n"] + moduleCode
            dir_path = os.path.dirname(outFile)
            os.makedirs(dir_path, exist_ok=True)
            with open(outFile, 'w+') as f:
                f.writelines(finalCode)

def generate_and_write_enums_code(enums, enumTemplate, fieldDecodeStringGenerator):
    enumModules = {}
    outFile = None
    fieldNamePattern = "<FIELD_NAME>" # this is for heling in generating decode fnCall for enums
    for enum, enumValues in enums.items():
        enumName = U.pascal_to_camel(enum)
        enumDefaultValueGetter = f"defualt{enum}"
        enumDecodeCode = "\n\t\t\t\t".join([f'| "{i}" => Result.Ok({i})' for i in enumValues])
        enumDecodeCode += f"\n\t\t\t\t| _ => Result.Error(\"failed to decode enum {enum}\")"
        enumEncodeCode = "\n\t\t".join([f'| {i} => "{i}"' for i in enumValues])
        enumDecodeFnName = f"get{enum}"
        enumDecodeFnVall = f'{fieldNamePattern}: {enumDecodeFnName}Result(dict, "{fieldNamePattern}") -> Result.getExn'
        enumOptionDecodeFnVall = f'{fieldNamePattern}: {enumDecodeFnName}Result(dict, "{fieldNamePattern}") -> Result.mapWithDefault(None, x => Some(x))'
        enumArrayDecodeFnVall = f'{fieldNamePattern}: dict -> Dict.get("{fieldNamePattern}") -> Array.map(x => {enumDecodeFnName}EnumResult(x) -> Result.getExn)'
        fieldDecodeStringGenerator.addToImportsPatternList(f".*{enum}.{enumName}.*", ['open Enums'])
        fieldDecodeStringGenerator.addToImportsPatternList(f'{enum}.{enumName}', ['open Enums'])
        fieldDecodeStringGenerator.addToImportsPatternList(f"option<{enum}.{enumName}>", ['open Enums']) # this is for faster access for most field usage by avoiding regex match while generating code
        fieldDecodeStringGenerator.addTypeDecodeString(f'{enum}.{enumName}', enumDecodeFnVall)
        fieldDecodeStringGenerator.addTypeDecodeString(f"option<{enum}.{enumName}>", f"{enumOptionDecodeFnVall}")
        fieldDecodeStringGenerator.addTypeDecodeString(f"array<{enum}.{enumName}>", f"{enumArrayDecodeFnVall}")
        enumEncodeFnName = f"->{enumName}ToString"
        fieldDecodeStringGenerator.addQueryParamCodeHelper(enumName, enumEncodeFnName)
        replacements = [ENUM_NAME(enumName), ENUM_VALUES(" | ".join(enumValues)), CAP_ENUM_NAME(enum), ENUM_DECODE_CODE(enumDecodeCode),ENUM_ENCODE_CODE(enumEncodeCode),  ENUM_DECODE_FUNCTION_NAME(enumDecodeFnName), ENUM_DEFAULT_VALUE(enumDefaultValueGetter)]
        enumsCodeFile = enumTemplate['template']
        outFile = enumTemplate['outFile']
        for i in replacements:
            enumsCodeFile = enumsCodeFile.replace(i['key'], i['value'])
            outFile = outFile.replace(i['key'], i['value'])
        enumModules[outFile] = [enumsCodeFile] if outFile not in enumModules else enumModules[outFile] + [enumsCodeFile]
    if outFile:
        enumModules[outFile] = {'codeFromTemplate': enumModules[outFile] if outFile in enumModules else [], 'imports': []}
    return enumModules

# def generate_and_write_defaults_code(typesRequireDefaults, defaultFieldValueTemplate):
#     defaultModules = {}
#     outFile = None
#     for typeName, fieldDetails in typesRequireDefaults.items():
#         for fieldName, fieldType in fieldDetails.items():
#             defaultValuesCodeFile = defaultFieldValueTemplate['template']
#             outFile = defaultFieldValueTemplate['outFile']
#             defaultValue = "<def>" # TODO: add this support somehow.
#             replacements = [FIELD_NAME_GETTER(fieldName), FIELD_TYPE(fieldType), DEFAULT_VALUE(defaultValue), CAP_TYPE_NAME(typeName)]
#             for i in replacements:
#                 defaultValuesCodeFile = defaultValuesCodeFile.replace(i['key'], i['value'])
#                 outFile = outFile.replace(i['key'], i['value'])
#             defaultModules[outFile] = [defaultValuesCodeFile] if outFile not in defaultModules else defaultModules[outFile] + [defaultValuesCodeFile]
#         defaultModules[outFile] = {'codeFromTemplate': defaultModules[outFile], 'imports': []}
#     write_rescript(defaultModules)


# def generateDecodeCodeAndGetImportsList(fieldDecodeStringGenerator, typeName, typeSchema):
#     decodeStringList = []
#     imports = []
#     for i, j in typeSchema.items():
#         defaultValueGetter = f"default{U.camel_to_pascal(i)}"
#         (needsDefault, rescriptDecodeString, importForField) = fieldDecodeStringGenerator.getTypeDecodeString(i, j, defaultValueGetter)
#         imports += importForField
#         if needsDefault:
#             required_defaults[typeName] = {} if typeName not in required_defaults else required_defaults[typeName]
#             required_defaults[typeName][defaultValueGetter] = j
#         decodeStringList.append(rescriptDecodeString)

#     return (",\n\t\t\t".join(decodeStringList), imports)

def generate_rescript(spec):
    templates = get_templates()
    (avoidHeaders, apiList) = templates['integration-config']
    api_request_response_types = extract_request_response_types(spec, avoidHeaders, apiList)
    categorized_types = categorize_types(api_request_response_types)
    fieldDecodeStringGenerator = CodeGenerator()


    with open("result.json", "w") as f:
        f.write(json.dumps(categorized_types, indent=2))

    # with open("all_types.json", "w") as f:
    #     f.write(json.dumps(all_types, indent=2))
    

    @U.withTime
    def generateAllEnums():
        enumModules = generate_and_write_enums_code(categorized_types['enums'], templates['enum'], fieldDecodeStringGenerator)
        write_rescript(enumModules)
        
    @U.withTime
    def generateAllTypes():
        allTypesCode = fieldDecodeStringGenerator.generateDecodeForAllTypes(categorized_types['all-types'], templates['api-type'])
        write_rescript(allTypesCode)

    @U.withTime
    def generateAllApis(): 
        allApisCode = fieldDecodeStringGenerator.generateApiCalls(categorized_types['apis'], templates['api'])
        write_rescript(allApisCode)
    
    
    generateAllEnums()
    generateAllTypes()
    generateAllApis()

    # with open("importsPatternList.json", "w") as f:
    #     f.write(json.dumps(fieldDecodeStringGenerator.importsPatternList, indent=2))


spec = None
with open('openapi.json', 'r') as file:
    spec = json.load(file)
generate_rescript(spec)

