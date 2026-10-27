// import { useEffect, useState } from "react"
// import { Button } from "@/components/ui/button"
// import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
// import { Input } from "@/components/ui/input"
// import { Label } from "@/components/ui/label"
// import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
// import { Progress } from "@/components/ui/progress"
// import { Upload, FileText, Check, AlertCircle, Loader2, FileCheck, CheckCircle } from "lucide-react"
// import { Badge } from "@/components/ui/badge"
// import { cn } from "../lib/utils"
// import { useDispatch, useSelector } from "react-redux"
// import { reconcileAPI, uploadInvoiceAPI, uploadPOAPI } from "../redux/actions/auditActions"

// export default function ReconcilePO() {
//   const [poFile, setPoFile] = useState(null)
//   const [invoiceFile, setInvoiceFile] = useState(null)
//   const [status, setStatus] = useState("idle")
//   const [reconcileResults, setReconcileResults] = useState(null)
//   const [dragActive, setDragActive] = useState({ po: false, invoice: false })

//   const dispatch = useDispatch()

//   const poUpload = useSelector((state) => state.poUpload)
//   const { loading: poUploadLoading, success: poUploadSuccess, error: poUploadError, poInfo } = poUpload

//   const invoiceUpload = useSelector((state) => state.invoiceUpload)
//   const { loading: invoiceUploadLoading, success: invoiceUploadSuccess, error: invoiceUploadError, invoiceInfo } = invoiceUpload

//   const reconciliation = useSelector((state) => state.reconciliation)
//   const { loading, error, success: reconciliationSuccess, reconciliationInfo } = reconciliation

//   const handlePoFileChange = (e) => {
//     if (e.target.files && e.target.files[0]) {
//       setPoFile(e.target.files[0])
//       // dispatch(uploadPOAPI(poFile))
//       dispatch(uploadPOAPI(e.target.files[0]))
//     }
//   }

//   const handleInvoiceFileChange = (e) => {
//     if (e.target.files && e.target.files[0]) {
//       setInvoiceFile(e.target.files[0])
//       // dispatch(uploadInvoiceAPI(invoiceFile))
//       dispatch(uploadInvoiceAPI(e.target.files[0]))
//     }
//   }

//   const handlePoDragOver = (e) => {
//     e.preventDefault()
//     setDragActive({ ...dragActive, po: true })
//   }

//   const handlePoDragLeave = (e) => {
//     e.preventDefault()
//     setDragActive({ ...dragActive, po: false })
//   }

//   const handlePoDrop = (e) => {
//     e.preventDefault()
//     setDragActive({ ...dragActive, po: false })
//     if (e.dataTransfer.files && e.dataTransfer.files[0]) {
//       setPoFile(e.dataTransfer.files[0])
//       dispatch(uploadPOAPI(poFile))
//       setStatus("idle")
//     }
//   }

//   const handleInvoiceDragOver = (e) => {
//     e.preventDefault()
//     setDragActive({ ...dragActive, invoice: true })
//   }

//   const handleInvoiceDragLeave = (e) => {
//     e.preventDefault()
//     setDragActive({ ...dragActive, invoice: false })
//   }

//   const handleInvoiceDrop = (e) => {
//     e.preventDefault()
//     setDragActive({ ...dragActive, invoice: false })
//     if (e.dataTransfer.files && e.dataTransfer.files[0]) {
//       setInvoiceFile(e.dataTransfer.files[0])
//       dispatch(uploadInvoiceAPI(invoiceFile))
//       setStatus("idle")
//     }
//   }

//   const handleReconcile = () => {
//     if (!poFile || !invoiceFile) return

//     setStatus("reconciling")
//     // console.log("reconciling",poInfo, invoiceInfo);
    
//     dispatch(reconcileAPI(poInfo, invoiceInfo))

//   }

//   useEffect(() => {
//     if (reconciliationInfo && reconciliationSuccess) {
//       setStatus("completed")
//       setReconcileResults(reconciliationInfo)
//     }
//   })

//   const renderFileUpload = () => (
//     <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//       <Card>
//         <CardHeader>
//           <CardTitle>Upload Purchase Order</CardTitle>
//         </CardHeader>
//         <CardContent>
//           <div
//             onDragOver={handlePoDragOver}
//             onDragLeave={handlePoDragLeave}
//             onDrop={handlePoDrop}
//             className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-muted-foreground/25 rounded-lg bg-muted/50">
//             <FileText className="h-10 w-10 text-muted-foreground mb-4" />
//             <p className="text-sm text-muted-foreground mb-2">Upload your PO file</p>
//             <Input
//               type="file"
//               id="po-file"
//               className="hidden"
//               onChange={handlePoFileChange}
//               accept=".pdf,.docx,.png,.jpg,.jpeg"
//             />
//             <Label htmlFor="po-file" asChild>
//               <Button variant="outline" size="sm" onClick={() => document.getElementById('po-file').click()}>
//                 <Upload className="mr-2 h-4 w-4" />
//                 Select File
//               </Button>
//             </Label>
//           </div>

//           {poFile && (
//             <div className="mt-4 p-3 bg-muted rounded-lg flex items-center">
//               <FileText className="h-5 w-5 mr-2 text-muted-foreground" />
//               <span className="text-sm font-medium truncate flex-1">{poFile.name}</span>
//               <Badge variant="outline" className="ml-2">
//                 <Check className="h-3 w-3 mr-1" />
//                 Ready
//               </Badge>
//             </div>
//           )}
//         </CardContent>
//       </Card>

//       <Card>
//         <CardHeader>
//           <CardTitle>Upload Invoice</CardTitle>
//         </CardHeader>
//         <CardContent>
//           <div
//             onDragOver={handleInvoiceDragOver}
//             onDragLeave={handleInvoiceDragLeave}
//             onDrop={handleInvoiceDrop}
//             className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-muted-foreground/25 rounded-lg bg-muted/50">
//             <FileCheck className="h-10 w-10 text-muted-foreground mb-4" />
//             <p className="text-sm text-muted-foreground mb-2">Upload your invoice file</p>
//             <Input
//               type="file"
//               id="invoice-file"
//               className="hidden"
//               onChange={handleInvoiceFileChange}
//               accept=".pdf,.docx,.png,.jpg,.jpeg"
//             />
//             <Label htmlFor="invoice-file" asChild>
//               <Button variant="outline" size="sm" onClick={() => document.getElementById('invoice-file').click()}>
//                 <Upload className="mr-2 h-4 w-4" />
//                 Select File
//               </Button>
//             </Label>
//           </div>

//           {invoiceFile && (
//             <div className="mt-4 p-3 bg-muted rounded-lg flex items-center">
//               <FileCheck className="h-5 w-5 mr-2 text-muted-foreground" />
//               <span className="text-sm font-medium truncate flex-1">{invoiceFile.name}</span>
//               <Badge variant="outline" className="ml-2">
//                 <Check className="h-3 w-3 mr-1" />
//                 Ready
//               </Badge>
//             </div>
//           )}
//         </CardContent>
//       </Card>
//     </div>
//   )

//   const renderReconcileButton = () => {
//     if (!poFile || !invoiceFile) return null

//     return (
//       <div className="flex justify-center mt-6">
//         <Button size="lg" onClick={handleReconcile} disabled={status !== "idle"} className="px-8">
//           {status === "idle" ? (
//             <>
//               <FileCheck className="mr-2 h-5 w-5" />
//               Reconcile Documents
//             </>
//           ) : status == "completed" ? (
//             <>
//               <FileCheck className="mr-2 h-5 w-5" />
//               Reconciliation Complete
//             </>
//           ) : (
//             <>
//               <Loader2 className="mr-2 h-5 w-5 animate-spin" />
//               Processing...
//             </>
//           )}
//         </Button>
//       </div>
//     )
//   }

//   const renderProcessingStatus = () => {
//     if (status !== "reconciling") return null

//     return (
//       <Card className="mt-6">
//         <CardHeader>
//           <CardTitle className="flex items-center">
//             <Loader2 className="mr-2 h-5 w-5 text-primary animate-spin" />
//             Reconciling Documents
//           </CardTitle>
//         </CardHeader>
//         <CardContent>
//           <div className="space-y-4">
//             <Progress value={75} className="h-2" />

//             <div className="space-y-2">
//               <div className="flex items-center space-x-4">
//                 <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
//                   <Check className="h-4 w-4 text-primary" />
//                 </div>
//                 <div>
//                   <p className="text-sm font-medium">Documents uploaded successfully</p>
//                 </div>
//               </div>

//               <div className="flex items-center space-x-4">
//                 <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
//                   <Check className="h-4 w-4 text-primary" />
//                 </div>
//                 <div>
//                   <p className="text-sm font-medium">Extracting data from documents</p>
//                 </div>
//               </div>

//               <div className="flex items-center space-x-4">
//                 <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center animate-pulse">
//                   <Loader2 className="h-4 w-4 text-primary-foreground animate-spin" />
//                 </div>
//                 <div>
//                   <p className="text-sm font-medium">Comparing line items and totals</p>
//                   <p className="text-xs text-muted-foreground">This may take a few moments</p>
//                 </div>
//               </div>
//             </div>
//           </div>
//         </CardContent>
//       </Card>
//     )
//   }

//   const renderReconcileResults = () => {
//     if (status !== "completed" || !reconcileResults) return null

//     return (
//       <Card className="mt-6">
//         <CardHeader>
//           <CardTitle className="flex items-center justify-between">
//             <span>Reconciliation Results</span>
//             <Badge variant={reconciliationInfo.status == "success" ? "success" : "destructive"}>
//               {reconciliationInfo.status == "success" ? "Match" : "Discrepancies Found"}
//             </Badge>
//           </CardTitle>
//         </CardHeader>

//         <CardContent>
//           {/* PO and Invoice Details */}
//           <div className="grid grid-cols-2 gap-4 mb-6">
//             {/* <div>
//         <p className="text-sm font-medium">PO Number</p>
//         <p className="text-sm">
//           {reconciliation.purchase_order.po_details.match(/PO Number: (\S+)/)?.[1] || reconciliation.purchase_order.po_details || "N/A"}
//         </p>
//       </div>
//       <div>
//         <p className="text-sm font-medium">Invoice Number</p>
//         <p className="text-sm">
//           {reconciliation.invoice.invoice_details.match(/Invoice Number: (\S+)/)?.[1] || reconciliation.invoice.invoice_details || "N/A"}
//         </p>
//       </div> */}
//             {/* <div>
//         <p className="text-sm font-medium">PO Total</p>
//         <p className="text-sm">
//           {reconciliation.purchase_order.po_details.match(/Total Value: (\$\d+,?\d+)/)?.[1] || "N/A"}
//         </p>
//       </div>
//       <div>
//         <p className="text-sm font-medium">Invoice Total</p>
//         <p
//           className={cn(
//             "text-sm",
//             reconciliation.purchase_order.po_details.match(/Total Value: (\$\d+,?\d+)/)?.[1] !==
//               reconciliation.invoice.invoice_details.match(/Total Value: (\$\d+,?\d+)/)?.[1] &&
//               "text-destructive font-medium"
//           )}
//         >
//           {reconciliation.invoice.invoice_details.match(/Total Value: (\$\d+,?\d+)/)?.[1] || "N/A"}
//         </p>
//       </div> */}
//           </div>

//           {/* Discrepancies Section */}
//           {/* {reconciliation.status == " failure" &&  */}
//           {reconciliation.status == " failure" && reconciliationInfo?.discrepancies?.length > 0 ? (
//             <div className="mb-4">
//               <h3 className="text-sm font-medium mb-2">Discrepancies</h3>
//               <Table>
//                 <TableHeader>
//                   <TableRow>
//                     <TableHead>Item</TableHead>
//                     <TableHead>PO Quantity</TableHead>
//                     <TableHead>Invoice Quantity</TableHead>
//                     <TableHead>PO Price</TableHead>
//                     <TableHead>Invoice Price</TableHead>
//                     <TableHead>Discrepancy Type</TableHead>
//                     <TableHead>Action Required</TableHead>
//                   </TableRow>
//                 </TableHeader>
//                 <TableBody>
//                   {reconciliationInfo.discrepancies.map((item, index) => (
//                     <TableRow key={index}>
//                       <TableCell className="font-medium">{item.item_name}</TableCell>
//                       <TableCell>{item.po_quantity}</TableCell>
//                       <TableCell className={item.po_quantity !== item.invoice_quantity ? "text-destructive font-medium" : ""}>
//                         {item.invoice_quantity}
//                       </TableCell>
//                       <TableCell>₹{item.po_price.toFixed(2)}</TableCell>
//                       <TableCell className={item.po_price !== item.invoice_price ? "text-destructive font-medium" : ""}>
//                         ₹{item.invoice_price.toFixed(2)}
//                       </TableCell>
//                       <TableCell className="capitalize">{item.discrepancy_type}</TableCell>
//                       <TableCell
//                         style={{
//                           maxWidth: '300px',  // Limit the width of the cell
//                           wordWrap: 'break-word',  // Allow wrapping of long content
//                           whiteSpace: 'normal', // Allow the text to break into multiple lines
//                         }}
//                       >
//                         {item.action_required}
//                       </TableCell>
//                     </TableRow>
//                   ))}
//                 </TableBody>
//               </Table>
//             </div>
//           ) : (
//             <div className="p-4 bg-success/20 rounded-lg">
//               <div style={{margin:'10px'}}>
//               <p className="text-sm text-success-foreground flex items-center">
//                 <CheckCircle className="inline-block mr-2 h-4 w-4" />
//                 No discrepancies found. The PO and invoice match successfully.
//               </p>
//               </div>
//               <Table><TableBody>
//               <TableRow>
//               <TableCell className="font-medium">PO Number</TableCell>
//               <TableCell>{reconciliationInfo?.purchase_order?.po_details}</TableCell>
//               </TableRow>
//               <TableRow>
//               <TableCell className="font-medium">Invoice Number</TableCell>
//               <TableCell>{reconciliationInfo?.invoice?.invoice_details}</TableCell>
//               </TableRow>
//               </TableBody></Table>
//             </div>
//           )}

//           {/* Alert for Issues */}
//           {reconciliation.status === "failure" && (
//             <div className="p-4 bg-muted rounded-lg">
//               <p className="text-sm text-muted-foreground flex items-center">
//                 <AlertCircle className="inline-block mr-2 h-4 w-4" />
//                 The AI has detected discrepancies between the PO and invoice. Please review and take appropriate action.
//               </p>
//             </div>
//           )}
//         </CardContent>

//         {/* Footer Buttons */}
//         <CardFooter className="flex justify-end space-x-2">
//           <Button variant="outline">Export Report</Button>
//           {reconciliation.status === "failure" && <Button variant="destructive">Flag for Review</Button>}
//           <Button>{reconciliation.status === "success" ? "Finalize" : "Approve with Exceptions"}</Button>
//         </CardFooter>
//       </Card>

//     )
//   }

//   return (
//     <div className="space-y-6">
//       {renderFileUpload()}
//       {renderReconcileButton()}
//       {renderProcessingStatus()}
//       {renderReconcileResults()}
//     </div>
//   )
// }