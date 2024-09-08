open Enums
open PersonAPIEntity
type authRes = {
	attempts: int,
	authId: string,
	authType: LoginType.loginType,
	isPersonBlocked: bool,
	person: personAPIEntity,
	token: option<string>
}

let decodeAuthRes = data => {
  try {
    Ok(data -> 
			JSON.Decode.object -> 
			Option.getOr(Dict.make()) -> 
			(dict => {
				attempts: getOptionInt(dict, "attempts") -> Option.getExn,
				authId: getOptionString(dict, "authId") -> Option.getExn,
				authType: getLoginTypeResult(dict, "authType") -> Result.getExn,
				isPersonBlocked: getOptionBool(dict, "isPersonBlocked") -> Option.getExn,
				person: dict -> Dict.getExn("person") -> decodePersonAPIEntity -> Result.getExn,
				token: getOptionString(dict, "token")
			})
		)
  }
  catch {
    | err => Error(err)
  }
}

let toJson = (req: authRes) => {
  req->asJson
}
