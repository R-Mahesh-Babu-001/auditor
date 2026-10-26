import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

const downloadConversation = async ({messages}) => {
  // console.log('Starting PDF download process');
  
  try {
    // Create a new PDF document
    const pdfDoc = await PDFDocument.create();
    let page = pdfDoc.addPage([595.28, 841.89]); // A4
    const { width, height } = page.getSize();
    
    // Embed fonts
    const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
    const fontBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
    const fontSize = 12;
    const lineHeight = 18;
    
    let y = height - 40;
    
    // Text adding function
    const addText = (text, options = {}) => {
      const {
        fontType = font,
        color = rgb(0, 0, 0),
        indent = 0,
        maxWidth = width - 80,
      } = options;
      
      if (!text || typeof text !== 'string') {
        console.warn('Invalid text passed to addText:', text);
        return;
      }
      
      const words = text.split(" ");
      let line = "";
      for (let i = 0; i < words.length; i++) {
        const testLine = line + words[i] + " ";
        const testWidth = fontType.widthOfTextAtSize(testLine, fontSize);
        if (testWidth > maxWidth) {
          if (y < 40) {
            page = pdfDoc.addPage([595.28, 841.89]);
            y = height - 40;
          }
          page.drawText(line.trim(), {
            x: 40 + indent,
            y,
            size: fontSize,
            font: fontType,
            color,
          });
          y -= lineHeight;
          line = words[i] + " ";
        } else {
          line = testLine;
        }
      }
      if (line.trim() !== "") {
        if (y < 40) {
          page = pdfDoc.addPage([595.28, 841.89]);
          y = height - 40;
        }
        page.drawText(line.trim(), {
          x: 40 + indent,
          y,
          size: fontSize,
          font: fontType,
          color,
        });
        y -= lineHeight;
      }
    };
    
    // Add title
    page.drawText("🧠 Chat Transcript", {
      x: 40,
      y,
      size: 20,
      font: fontBold,
      color: rgb(0.1, 0.2, 0.4),
    });
    y -= 30;
    
    // Validate messages
    if (!Array.isArray(messages)) {
      console.error('Messages is not an array:', messages);
      throw new Error('Messages must be an array');
    }
    
    // Add messages
    messages.forEach((msg, index) => {
      try {
        if (!msg || typeof msg !== 'object') {
          console.warn(`Invalid message at index ${index}:`, msg);
          return;
        }
        
        const isUser = msg.role === "user";
        const prefix = isUser ? "You: " : "Assistant:";
        const roleColor = isUser ? rgb(0.1, 0.5, 0.2) : rgb(0.2, 0.2, 0.6);
        
        addText(`${prefix}`, {
          fontType: fontBold,
          color: roleColor,
        });
        
        if (msg.content) {
          addText(msg.content, {
            indent: 10,
          });
        } else {
          addText("(No content)", { indent: 10 });
        }
        
        if (msg.model || msg.provider) {
          addText(`Model: ${msg.model || "N/A"} | Provider: ${msg.provider || "N/A"}`, {
            color: rgb(0.5, 0.5, 0.5),
            indent: 10,
          });
        }
        
        y -= 10;
      } catch (err) {
        console.error(`Error processing message at index ${index}:`, err);
      }
    });
    
    // Save the PDF
    const pdfBytes = await pdfDoc.save();
    
    // Create a Blob and trigger download
    const blob = new Blob([pdfBytes], { type: "application/pdf" });

    // console.log('pdf blob ready');
    
    
    // Create a download link and trigger it
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = "conversation.pdf";
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();

    
    // Clean up
    setTimeout(() => {
      URL.revokeObjectURL(link.href);
      document.body.removeChild(link);
    }, 100);
    
    // console.log('PDF download initiated successfully');
    return true;
  } catch (error) {
    console.error('Error generating PDF:', error);
    return false;
  }
};

export default downloadConversation;