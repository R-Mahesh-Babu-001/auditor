import { SET_ACTION, SET_ACTION_ERROR } from "../constants/actionConstants"

export const setAction = (action)=> async(dispatch)=>{
    try{
        dispatch({type:SET_ACTION,payload:action})
    }
    catch(error){
        console.log('Error: ',error);
        dispatch({
            type:SET_ACTION_ERROR,
            payload: error.response?.data?.message || error.message,
        })
    }
}