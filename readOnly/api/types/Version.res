
type version = {
	build: option<string>,
	maintenance: int,
	major: int,
	minor: int,
	preRelease: option<string>
}

let decodeVersion = data => {
  try {
    Ok(data -> 
			JSON.Decode.object -> 
			Option.getOr(Dict.make()) -> 
			(dict => {
				build: getOptionString(dict, "build"),
				maintenance: getOptionInt(dict, "maintenance") -> Option.getExn,
				major: getOptionInt(dict, "major") -> Option.getExn,
				minor: getOptionInt(dict, "minor") -> Option.getExn,
				preRelease: getOptionString(dict, "preRelease")
			})
		)
  }
  catch {
    | err => Error(err)
  }
}

let toJson = (req: version) => {
  req->asJson
}
