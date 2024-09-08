open GetRoutesReq
open RouteInfoArray


module Keys = {
  let all = "pickupRoutePost"
}


let pickupRoutePostApiCall = async (body: getRoutesReq) => {
  let data = await ApiCall.callPostAPI'(
    ~url="/pickup/route",
    ~body=body->GetRoutesReq.toJson
  )
  RouteInfoArray.decodeRouteInfoArray(data)
}

let usePickupRoutePost = (~mutationKey) => {
  useMutation({
    mutationKey,
    mutationFn: data => pickupRoutePostApiCall(body: getRoutesReq),
  })
}
