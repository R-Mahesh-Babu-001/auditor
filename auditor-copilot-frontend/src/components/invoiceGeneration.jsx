// import { useEffect, useState } from "react"
// import { Button } from "@/components/ui/button"
// import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
// import { Input } from "@/components/ui/input"
// import { Label } from "@/components/ui/label"
// import { Progress } from "@/components/ui/progress"
// import { Upload, FileText, Check, AlertCircle, Loader2 } from "lucide-react"
// import { uploadFileAPI, generateInvoiceAPI } from "../redux/actions/auditActions"
// import InvoiceForm from "./InvoiceGenerationComponents/InvoicePreview"
// import { useDispatch, useSelector } from "react-redux"
// import useGenerateInvoicePDF from "../hooks/invoicePdfGenerator"

// export default function InvoiceGeneration() {
//   const [file, setFile] = useState(null)
//   const [status, setStatus] = useState("idle")
//   const [progress, setProgress] = useState(0)
//   const [invoiceData, setInvoiceData] = useState(null)
//   const [filePath, setFilePath] = useState("")
  
//   const fileUpload = useSelector((state) => state.fileUpload)
//   const {success:fileUploadSuccess, loading:fileUploadLoading, fileInfo} = fileUpload

//   const invoiceGeneration = useSelector((state) => state.invoiceGeneration)
//   const { loading, error: invoiceGenerationError ,success:invoiceGenerationSuccess, invoiceInfo } = invoiceGeneration

//   const [formData, setFormData] = useState(null);

//   const generatePdf = useGenerateInvoicePDF(formData)

//   useEffect(()=>{
//     // console.log('form data changed',formData);
    
//   },[formData])
  
//   const dispatch = useDispatch()

//   const handleFileChange = (e) => {
//     if (e.target.files && e.target.files[0]) {
//       setFile(e.target.files[0])
//     }
//   }

//   const handleUpload = async () => {
//     if (!file) return

//     setStatus("uploading")
//     setProgress(0)

//     // Simulate upload progress
//     const interval = setInterval(() => {
//       setProgress((prev) => {
//         if (prev >= 100) {
//           clearInterval(interval)
//           return 100
//         }
//         return prev + 10
//       })
//     }, 300)

//     try {
//       dispatch(uploadFileAPI("INVOICING", file)) // Upload using RAG flag
//       setProgress(100)
//       // if(fileInfo && fileUploadSuccess){
//       //   setFilePath(fileInfo.filePath)
//       //   await handleGenerateInvoice(response.payload.filePath)
//       // } // Store the file path from the response
//       // setStatus("analyzing")

//       // Trigger invoice generation upon successful upload
      
//     } catch (error) {
//       setStatus("error")
//       console.error("Error during file upload:", error)
//     }
//   }

//   useEffect(()=>{
//     if((fileInfo && fileUploadSuccess==true && fileUploadLoading==false) && (!invoiceGenerationError && !invoiceGenerationSuccess==true) ){
//       setFilePath(fileInfo.file_path)

//       // setStatus("analyzing: ",fileInfo.file_path)
//       handleGenerateInvoice(fileInfo.file_path)
//       setStatus("analyzing")
//     } // Store the file path from the response
//     // setStatus("analyzing")

//     if(invoiceInfo && invoiceGenerationSuccess){
//       setInvoiceData(invoiceInfo)
//       setStatus("completed")
//     }
//   },[fileUploadSuccess, fileInfo, invoiceGenerationSuccess, invoiceInfo])

//   const handleGenerateInvoice = async (path) => {
//     try {
//       dispatch(generateInvoiceAPI(path)) // Trigger invoice generation
//       // setInvoiceData(data)
//       // setStatus("completed")
//     } catch (error) {
//       setStatus("error")
//       console.error("Error during invoice generation:", error)
//     }
//   }

//   const handleDrop = (e) => {
//     e.preventDefault()
//     if (e.dataTransfer.files && e.dataTransfer.files[0]) {
//       setFile(e.dataTransfer.files[0])
//       setStatus("idle")
//     }
//   }

//   const handleDragOver = (e) => {
//     e.preventDefault()
//   }

//   const renderUploadSection = () => (
//     <Card>
//       <CardHeader>
//         <CardTitle>Upload Purchase Order</CardTitle>
//       </CardHeader>
//       <CardContent>
//         <div
//           className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-muted-foreground/25 rounded-lg bg-muted/50"
//           onDrop={handleDrop}
//           onDragOver={handleDragOver}
//         >
//           <FileText className="h-10 w-10 text-muted-foreground mb-4" />
//           <p className="text-sm text-muted-foreground mb-2">
//             Drag and drop your PO file, or click to browse
//           </p>
//           <p className="text-xs text-muted-foreground mb-4">
//             Supports PDF, DOCX, and image files
//           </p>
//           <Input
//             type="file"
//             id="po-file"
//             className="hidden"
//             onChange={handleFileChange}
//             accept=".pdf,.docx,.png,.jpg,.jpeg"
//           />
//           <Label htmlFor="po-file" asChild>
//             <Button variant="outline" onClick={() => document.querySelector('input[type=file]').click()}>
//               <Upload className="mr-2 h-4 w-4" />
//               Select File
//             </Button>
//           </Label>
//         </div>

//         {file && (
//           <div className="mt-4 p-3 bg-muted rounded-lg flex items-center justify-between">
//             <div className="flex items-center">
//               <FileText className="h-5 w-5 mr-2 text-muted-foreground" />
//               <span className="text-sm font-medium truncate max-w-[200px]">{file.name}</span>
//             </div>
//             <Button
//               onClick={handleUpload}
//               disabled={status !== "idle"}
//               size="sm"
//             >
//               {status === "idle" ? "Process" : status === "completed" ? "Analyzed" : "Processing..."}
//             </Button>
//           </div>
//         )}
//       </CardContent>
//     </Card>
//   )

//   const renderProcessingStatus = () => {
//     if (status === "idle") return null

//     return (
//       <Card className="mt-6">
//         <CardHeader>
//           <CardTitle className="flex items-center">
//             {status === "uploading" && (
//               <>
//                 <Upload className="mr-2 h-5 w-5 text-muted-foreground" />
//                 Uploading Document
//               </>
//             )}
//             {status === "analyzing" && (
//               <>
//                 <Loader2 className="mr-2 h-5 w-5 text-primary animate-spin" />
//                 Analyzing Document
//               </>
//             )}
//             {status === "completed" && (
//               <>
//                 <Check className="mr-2 h-5 w-5 text-green-500" />
//                 Analysis Complete
//               </>
//             )}
//             {status === "error" && (
//               <>
//                 <AlertCircle className="mr-2 h-5 w-5 text-destructive" />
//                 Error Processing Document
//               </>
//             )}
//           </CardTitle>
//         </CardHeader>
//         <CardContent>
//           {status === "uploading" && (
//             <div className="space-y-2">
//               <Progress value={progress} className="h-2" />
//               <p className="text-sm text-muted-foreground text-center">{progress}% uploaded</p>
//             </div>
//           )}
//         </CardContent>
//       </Card>
//     )
//   }

//   const renderInvoicePreview = () => {
//     if (status !== "completed" || !invoiceData) return null

//     return (
//       <Card className="mt-6">
//         <CardHeader>
//           <CardTitle>Invoice Preview</CardTitle>
//         </CardHeader>
//         <InvoiceForm formData={formData} setFormData={setFormData} />
//         <CardFooter className="flex justify-end space-x-2">
//           <Button variant="outline">Edit Invoice</Button>
//           <Button onClick={generatePdf}>Generate Final Invoice</Button>
//         </CardFooter>
//       </Card>
//     )
//   }

//   return (
//     <div className="space-y-6">
//       {renderUploadSection()}
//       {renderProcessingStatus()}
//       {renderInvoicePreview()}
//     </div>
//   )
// }
