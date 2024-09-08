open Enums
open Version
type personAPIEntity = {
	bundleVersion: version,
	clientVersion: version,
	disability: option<string>,
	email: option<string>,
	firstName: option<string>,
	followsRide: bool,
	gender: Gender.gender,
	hasCompletedMockSafetyDrill: option<bool>,
	hasCompletedSafetySetup: bool,
	hasDisability: option<bool>,
	hasTakenRide: bool,
	hasTakenValidRide: bool,
	id: string,
	isSafetyCenterDisabled: bool,
	language: Language.language,
	lastName: option<string>,
	maskedDeviceToken: option<string>,
	maskedMobileNumber: option<string>,
	middleName: option<string>,
	referralCode: option<string>,
	whatsappNotificationEnrollStatus: OptApiMethods.optApiMethods
}

let decodePersonAPIEntity = data => {
  try {
    Ok(data -> 
			JSON.Decode.object -> 
			Option.getOr(Dict.make()) -> 
			(dict => {
				bundleVersion: dict -> Dict.getExn("bundleVersion") -> decodeVersion -> Result.getExn,
				clientVersion: dict -> Dict.getExn("clientVersion") -> decodeVersion -> Result.getExn,
				disability: getOptionString(dict, "disability"),
				email: getOptionString(dict, "email"),
				firstName: getOptionString(dict, "firstName"),
				followsRide: getOptionBool(dict, "followsRide") -> Option.getExn,
				gender: getGenderResult(dict, "gender") -> Result.getExn,
				hasCompletedMockSafetyDrill: getOptionBool(dict, "hasCompletedMockSafetyDrill"),
				hasCompletedSafetySetup: getOptionBool(dict, "hasCompletedSafetySetup") -> Option.getExn,
				hasDisability: getOptionBool(dict, "hasDisability"),
				hasTakenRide: getOptionBool(dict, "hasTakenRide") -> Option.getExn,
				hasTakenValidRide: getOptionBool(dict, "hasTakenValidRide") -> Option.getExn,
				id: getOptionString(dict, "id") -> Option.getExn,
				isSafetyCenterDisabled: getOptionBool(dict, "isSafetyCenterDisabled") -> Option.getExn,
				language: getLanguageResult(dict, "language") -> Result.getExn,
				lastName: getOptionString(dict, "lastName"),
				maskedDeviceToken: getOptionString(dict, "maskedDeviceToken"),
				maskedMobileNumber: getOptionString(dict, "maskedMobileNumber"),
				middleName: getOptionString(dict, "middleName"),
				referralCode: getOptionString(dict, "referralCode"),
				whatsappNotificationEnrollStatus: getOptApiMethodsResult(dict, "whatsappNotificationEnrollStatus") -> Result.getExn
			})
		)
  }
  catch {
    | err => Error(err)
  }
}

let toJson = (req: personAPIEntity) => {
  req->asJson
}
