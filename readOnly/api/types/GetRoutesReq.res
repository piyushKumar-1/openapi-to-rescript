open Enums
open LatLong
type getRoutesReq = {
	calcPoints: bool,
	mode: TravelMode.travelMode,
	waypoints: array<latLong>
}

let decodeGetRoutesReq = data => {
  try {
    Ok(data -> 
			JSON.Decode.object -> 
			Option.getOr(Dict.make()) -> 
			(dict => {
				calcPoints: getOptionBool(dict, "calcPoints") -> Option.getExn,
				mode: getTravelModeResult(dict, "mode") -> Result.getExn,
				waypoints: dict -> Dict.get("waypoints") -> Option.getOr([]) -> Array.map(x => decodeLatLong(x) -> Result.getExn)
			})
		)
  }
  catch {
    | err => Error(err)
  }
}

let toJson = (req: getRoutesReq) => {
  req->asJson
}
