open LatLong
open Distance
type routeInfo = {
	boundingBox: string,
	distance: option<int>,
	distanceWithUnit: distance,
	duration: option<int>,
	points: array<latLong>,
	snappedWaypoints: array<latLong>,
	staticDuration: option<int>
}

let decodeRouteInfo = data => {
  try {
    Ok(data -> 
			JSON.Decode.object -> 
			Option.getOr(Dict.make()) -> 
			(dict => {
				boundingBox: getOptionString(dict, "boundingBox") -> Option.getExn,
				distance: getOptionInt(dict, "distance"),
				distanceWithUnit: dict -> Dict.getExn("distanceWithUnit") -> decodeDistance -> Result.getExn,
				duration: getOptionInt(dict, "duration"),
				points: dict -> Dict.get("points") -> Option.getOr([]) -> Array.map(x => decodeLatLong(x) -> Result.getExn),
				snappedWaypoints: dict -> Dict.get("snappedWaypoints") -> Option.getOr([]) -> Array.map(x => decodeLatLong(x) -> Result.getExn),
				staticDuration: getOptionInt(dict, "staticDuration")
			})
		)
  }
  catch {
    | err => Error(err)
  }
}

let toJson = (req: routeInfo) => {
  req->asJson
}
