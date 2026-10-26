import { SET_ACTION, SET_ACTION_ERROR } from "../constants/actionConstants";

export const actionReducer = (state = {}, action) => {
  switch (action.type) {
    case SET_ACTION:
      return { success:true, actionInfo: action.payload };
    case SET_ACTION_ERROR:
      return { success:false, error: action.payload };
    default:
      return state;
  }
};