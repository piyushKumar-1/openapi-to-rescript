open Enums
type distance = {
	unit: DistanceUnit.distanceUnit,
	value: float
}

let decodeDistance = data => {
  try {
    Ok(data -> 
			JSON.Decode.object -> 
			Option.getOr(Dict.make()) -> 
			(dict => {
				unit: getDistanceUnitResult(dict, "unit") -> Result.getExn,
				value: getOptionFloat(dict, "value") -> Option.getExn
			})
		)
  }
  catch {
    | err => Error(err)
  }
}

let toJson = (req: distance) => {
  req->asJson
}
