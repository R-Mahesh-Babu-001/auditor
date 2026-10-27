import { combineReducers } from "redux";
import { configureStore } from "@reduxjs/toolkit";
import { thunk } from "redux-thunk";
import { generateInvoiceReducer, reconciliationReducer, uploadFileReducer, uploadInvoiceReducer, uploadPOReducer } from "../reducers/invoiceReducers";
import { actionReducer } from "../reducers/actionReducers";
// import InvoiceGeneration from "@//components/invoiceGeneration";

const reducers = combineReducers({
    fileUpload: uploadFileReducer,
    poUpload: uploadPOReducer,
    invoiceUpload: uploadInvoiceReducer,
    invoiceGeneration: generateInvoiceReducer,
    reconciliation: reconciliationReducer,
    actionState: actionReducer,
});

const initialState = {
  // userLogin: { userInfo: userInfoFromStorage },
  // domainsList: {domainsListInfo: domainsListInfoFromStorage},
  // learningPathDetails: { learningPathInfo: learningPathInfoFromStorage },
  // newsArticles: { newsInfo: newsArticlesFromStorage },
};

const store = configureStore({
  reducer: reducers,
  preloadedState: initialState,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(thunk),
  devTools: true,
});

export default store;
