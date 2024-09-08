open Enums
type authReq = {
	deviceToken: option<string>,
	email: option<string>,
	enableOtpLessRide: option<bool>,
	firstName: option<string>,
	gender: Gender.gender,
	identifierType: IdentifierType.identifierType,
	language: Language.language,
	lastName: option<string>,
	merchantId: string,
	middleName: option<string>,
	mobileCountryCode: option<string>,
	mobileNumber: option<string>,
	notificationToken: option<string>,
	otpChannel: OTPChannel.oTPChannel,
	registrationLat: option<float>,
	registrationLon: option<float>,
	whatsappNotificationEnroll: OptApiMethods.optApiMethods
}

let decodeAuthReq = data => {
  try {
    Ok(data -> 
			JSON.Decode.object -> 
			Option.getOr(Dict.make()) -> 
			(dict => {
				deviceToken: getOptionString(dict, "deviceToken"),
				email: getOptionString(dict, "email"),
				enableOtpLessRide: getOptionBool(dict, "enableOtpLessRide"),
				firstName: getOptionString(dict, "firstName"),
				gender: getGenderResult(dict, "gender") -> Result.getExn,
				identifierType: getIdentifierTypeResult(dict, "identifierType") -> Result.getExn,
				language: getLanguageResult(dict, "language") -> Result.getExn,
				lastName: getOptionString(dict, "lastName"),
				merchantId: getOptionString(dict, "merchantId") -> Option.getExn,
				middleName: getOptionString(dict, "middleName"),
				mobileCountryCode: getOptionString(dict, "mobileCountryCode"),
				mobileNumber: getOptionString(dict, "mobileNumber"),
				notificationToken: getOptionString(dict, "notificationToken"),
				otpChannel: getOTPChannelResult(dict, "otpChannel") -> Result.getExn,
				registrationLat: getOptionFloat(dict, "registrationLat"),
				registrationLon: getOptionFloat(dict, "registrationLon"),
				whatsappNotificationEnroll: getOptApiMethodsResult(dict, "whatsappNotificationEnroll") -> Result.getExn
			})
		)
  }
  catch {
    | err => Error(err)
  }
}

let toJson = (req: authReq) => {
  req->asJson
}
