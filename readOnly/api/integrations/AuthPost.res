open AuthRes
open AuthReq


module Keys = {
  let all = "authPost"
}


let authPostApiCall = async (body: authReq) => {
  let data = await ApiCall.callPostAPI'(
    ~url="/auth",
    ~body=body->AuthReq.toJson
  )
  AuthRes.decodeAuthRes(data)
}

let useAuthPost = (~mutationKey) => {
  useMutation({
    mutationKey,
    mutationFn: data => authPostApiCall(body: authReq),
  })
}
