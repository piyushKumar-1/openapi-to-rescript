
module Gender = {
  type gender = MALE | FEMALE | OTHER | UNKNOWN | PREFER_NOT_TO_SAY
}

let getGenderEnumResult = (data) => {
  open Gender
  data
  ->Option.flatMap(JSON.Decode.string)
  ->Option.mapWithDefault(Result.Error("failed to decode to Gender type"), 
    str => {
      switch str {
        | "MALE" => Result.Ok(MALE)
				| "FEMALE" => Result.Ok(FEMALE)
				| "OTHER" => Result.Ok(OTHER)
				| "UNKNOWN" => Result.Ok(UNKNOWN)
				| "PREFER_NOT_TO_SAY" => Result.Ok(PREFER_NOT_TO_SAY)
				| _ => Result.Error("failed to decode enum Gender")
      }
  })
}

let getGenderResult = (dict, key): result<Gender.gender, string> => {
  dict
  ->Dict.get(key)
  ->getGenderEnumResult
}

let genderToString = (enumValue) => {
  open Gender
  switch enumValue {
    | MALE => "MALE"
		| FEMALE => "FEMALE"
		| OTHER => "OTHER"
		| UNKNOWN => "UNKNOWN"
		| PREFER_NOT_TO_SAY => "PREFER_NOT_TO_SAY"
  }
}
module IdentifierType = {
  type identifierType = MOBILENUMBER | AADHAAR | EMAIL
}

let getIdentifierTypeEnumResult = (data) => {
  open IdentifierType
  data
  ->Option.flatMap(JSON.Decode.string)
  ->Option.mapWithDefault(Result.Error("failed to decode to IdentifierType type"), 
    str => {
      switch str {
        | "MOBILENUMBER" => Result.Ok(MOBILENUMBER)
				| "AADHAAR" => Result.Ok(AADHAAR)
				| "EMAIL" => Result.Ok(EMAIL)
				| _ => Result.Error("failed to decode enum IdentifierType")
      }
  })
}

let getIdentifierTypeResult = (dict, key): result<IdentifierType.identifierType, string> => {
  dict
  ->Dict.get(key)
  ->getIdentifierTypeEnumResult
}

let identifierTypeToString = (enumValue) => {
  open IdentifierType
  switch enumValue {
    | MOBILENUMBER => "MOBILENUMBER"
		| AADHAAR => "AADHAAR"
		| EMAIL => "EMAIL"
  }
}
module Language = {
  type language = ENGLISH | HINDI | KANNADA | TAMIL | MALAYALAM | BENGALI | FRENCH | TELUGU
}

let getLanguageEnumResult = (data) => {
  open Language
  data
  ->Option.flatMap(JSON.Decode.string)
  ->Option.mapWithDefault(Result.Error("failed to decode to Language type"), 
    str => {
      switch str {
        | "ENGLISH" => Result.Ok(ENGLISH)
				| "HINDI" => Result.Ok(HINDI)
				| "KANNADA" => Result.Ok(KANNADA)
				| "TAMIL" => Result.Ok(TAMIL)
				| "MALAYALAM" => Result.Ok(MALAYALAM)
				| "BENGALI" => Result.Ok(BENGALI)
				| "FRENCH" => Result.Ok(FRENCH)
				| "TELUGU" => Result.Ok(TELUGU)
				| _ => Result.Error("failed to decode enum Language")
      }
  })
}

let getLanguageResult = (dict, key): result<Language.language, string> => {
  dict
  ->Dict.get(key)
  ->getLanguageEnumResult
}

let languageToString = (enumValue) => {
  open Language
  switch enumValue {
    | ENGLISH => "ENGLISH"
		| HINDI => "HINDI"
		| KANNADA => "KANNADA"
		| TAMIL => "TAMIL"
		| MALAYALAM => "MALAYALAM"
		| BENGALI => "BENGALI"
		| FRENCH => "FRENCH"
		| TELUGU => "TELUGU"
  }
}
module OTPChannel = {
  type oTPChannel = SMS | WHATSAPP | EMAIL
}

let getOTPChannelEnumResult = (data) => {
  open OTPChannel
  data
  ->Option.flatMap(JSON.Decode.string)
  ->Option.mapWithDefault(Result.Error("failed to decode to OTPChannel type"), 
    str => {
      switch str {
        | "SMS" => Result.Ok(SMS)
				| "WHATSAPP" => Result.Ok(WHATSAPP)
				| "EMAIL" => Result.Ok(EMAIL)
				| _ => Result.Error("failed to decode enum OTPChannel")
      }
  })
}

let getOTPChannelResult = (dict, key): result<OTPChannel.oTPChannel, string> => {
  dict
  ->Dict.get(key)
  ->getOTPChannelEnumResult
}

let oTPChannelToString = (enumValue) => {
  open OTPChannel
  switch enumValue {
    | SMS => "SMS"
		| WHATSAPP => "WHATSAPP"
		| EMAIL => "EMAIL"
  }
}
module OptApiMethods = {
  type optApiMethods = OPT_IN | OPT_OUT
}

let getOptApiMethodsEnumResult = (data) => {
  open OptApiMethods
  data
  ->Option.flatMap(JSON.Decode.string)
  ->Option.mapWithDefault(Result.Error("failed to decode to OptApiMethods type"), 
    str => {
      switch str {
        | "OPT_IN" => Result.Ok(OPT_IN)
				| "OPT_OUT" => Result.Ok(OPT_OUT)
				| _ => Result.Error("failed to decode enum OptApiMethods")
      }
  })
}

let getOptApiMethodsResult = (dict, key): result<OptApiMethods.optApiMethods, string> => {
  dict
  ->Dict.get(key)
  ->getOptApiMethodsEnumResult
}

let optApiMethodsToString = (enumValue) => {
  open OptApiMethods
  switch enumValue {
    | OPT_IN => "OPT_IN"
		| OPT_OUT => "OPT_OUT"
  }
}
module LoginType = {
  type loginType = OTP | PASSWORD | DIRECT | OAUTH
}

let getLoginTypeEnumResult = (data) => {
  open LoginType
  data
  ->Option.flatMap(JSON.Decode.string)
  ->Option.mapWithDefault(Result.Error("failed to decode to LoginType type"), 
    str => {
      switch str {
        | "OTP" => Result.Ok(OTP)
				| "PASSWORD" => Result.Ok(PASSWORD)
				| "DIRECT" => Result.Ok(DIRECT)
				| "OAUTH" => Result.Ok(OAUTH)
				| _ => Result.Error("failed to decode enum LoginType")
      }
  })
}

let getLoginTypeResult = (dict, key): result<LoginType.loginType, string> => {
  dict
  ->Dict.get(key)
  ->getLoginTypeEnumResult
}

let loginTypeToString = (enumValue) => {
  open LoginType
  switch enumValue {
    | OTP => "OTP"
		| PASSWORD => "PASSWORD"
		| DIRECT => "DIRECT"
		| OAUTH => "OAUTH"
  }
}
module TravelMode = {
  type travelMode = CAR | MOTORCYCLE | BICYCLE | FOOT
}

let getTravelModeEnumResult = (data) => {
  open TravelMode
  data
  ->Option.flatMap(JSON.Decode.string)
  ->Option.mapWithDefault(Result.Error("failed to decode to TravelMode type"), 
    str => {
      switch str {
        | "CAR" => Result.Ok(CAR)
				| "MOTORCYCLE" => Result.Ok(MOTORCYCLE)
				| "BICYCLE" => Result.Ok(BICYCLE)
				| "FOOT" => Result.Ok(FOOT)
				| _ => Result.Error("failed to decode enum TravelMode")
      }
  })
}

let getTravelModeResult = (dict, key): result<TravelMode.travelMode, string> => {
  dict
  ->Dict.get(key)
  ->getTravelModeEnumResult
}

let travelModeToString = (enumValue) => {
  open TravelMode
  switch enumValue {
    | CAR => "CAR"
		| MOTORCYCLE => "MOTORCYCLE"
		| BICYCLE => "BICYCLE"
		| FOOT => "FOOT"
  }
}
module DistanceUnit = {
  type distanceUnit = Meter | Mile | Yard | Kilometer
}

let getDistanceUnitEnumResult = (data) => {
  open DistanceUnit
  data
  ->Option.flatMap(JSON.Decode.string)
  ->Option.mapWithDefault(Result.Error("failed to decode to DistanceUnit type"), 
    str => {
      switch str {
        | "Meter" => Result.Ok(Meter)
				| "Mile" => Result.Ok(Mile)
				| "Yard" => Result.Ok(Yard)
				| "Kilometer" => Result.Ok(Kilometer)
				| _ => Result.Error("failed to decode enum DistanceUnit")
      }
  })
}

let getDistanceUnitResult = (dict, key): result<DistanceUnit.distanceUnit, string> => {
  dict
  ->Dict.get(key)
  ->getDistanceUnitEnumResult
}

let distanceUnitToString = (enumValue) => {
  open DistanceUnit
  switch enumValue {
    | Meter => "Meter"
		| Mile => "Mile"
		| Yard => "Yard"
		| Kilometer => "Kilometer"
  }
}
