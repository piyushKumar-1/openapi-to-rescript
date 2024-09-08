open RouteInfo
type routeInfoArray = array<routeInfo>

let decodeRouteInfoArray = data => {
  try {
    Ok(dict
		 -> JSON.Decode.array
		 -> Option.getOr([])
		 -> Array.filterMap(JSON.Decode.object)
		 -> Array.map(x => decodeRouteInfo(x)))
  }
  catch {
    | err => Error(err)
  }
}

let toJson = (req: routeInfoArray) => {
  req->asJson
}
