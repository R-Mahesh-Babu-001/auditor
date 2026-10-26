import { GENERATE_INVOICE_REQUEST, GENERATE_INVOICE_SUCCESS, GENERATE_INVOICE_FAIL, UPLOAD_FILE_REQUEST, UPLOAD_FILE_SUCCESS, UPLOAD_FILE_FAIL, RECONCILIATION_REQUEST, RECONCILIATION_SUCCESS, RECONCILIATION_FAIL, UPLOAD_PO_REQUEST, UPLOAD_PO_SUCCESS, UPLOAD_PO_FAIL, UPLOAD_INVOICE_REQUEST, UPLOAD_INVOICE_SUCCESS, UPLOAD_INVOICE_FAIL } from "../constants/invoiceConstants";

export const uploadFileReducer = (state = {}, action) => {
    switch(action.type){
        case UPLOAD_FILE_REQUEST:
            return {loading: true}
        case UPLOAD_FILE_SUCCESS:
            return {loading: false, success: true, fileInfo: action.payload}
        case UPLOAD_FILE_FAIL:
            return {loading: false, error: action.payload}
        default:
            return state
    }
}

export const uploadPOReducer = (state = {}, action) => {
    switch(action.type){
        case UPLOAD_PO_REQUEST:
            return {loading: true}
        case UPLOAD_PO_SUCCESS:
            return {loading: false, success: true, poInfo: action.payload}
        case UPLOAD_PO_FAIL:
            return {loading: false, error: action.payload}
        default:
            return state
    }
}

export const uploadInvoiceReducer = (state = {}, action) => {
    switch(action.type){
        case UPLOAD_INVOICE_REQUEST:
            return {loading: true}
        case UPLOAD_INVOICE_SUCCESS:
            return {loading: false, success: true, invoiceInfo: action.payload}
        case UPLOAD_INVOICE_FAIL:
            return {loading: false, error: action.payload}
        default:
            return state
    }
}


export const generateInvoiceReducer = (state = {}, action) => {
    switch(action.type){
        case GENERATE_INVOICE_REQUEST:
            return {loading: true}
        case GENERATE_INVOICE_SUCCESS:
            return {loading: false, success: true, invoiceInfo: action.payload}
        case GENERATE_INVOICE_FAIL:
            return {loading: false, success:false, error: action.payload}
        default:
            return state
    }
}


export const reconciliationReducer = (state = {}, action) => {
    switch(action.type){
        case RECONCILIATION_REQUEST:
            return {loading: true}
        case RECONCILIATION_SUCCESS:
            return {loading: false, success: true, reconciliationInfo: action.payload}
        case RECONCILIATION_FAIL:
            return {loading: false, success:false, error: action.payload}
        default:
            return state
    }
}