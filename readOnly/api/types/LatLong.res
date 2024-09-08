
type latLong = {
	lat: float,
	lon: float
}

let decodeLatLong = data => {
  try {
    Ok(data -> 
			JSON.Decode.object -> 
			Option.getOr(Dict.make()) -> 
			(dict => {
				lat: getOptionFloat(dict, "lat") -> Option.getExn,
				lon: getOptionFloat(dict, "lon") -> Option.getExn
			})
		)
  }
  catch {
    | err => Error(err)
  }
}

let toJson = (req: latLong) => {
  req->asJson
}
