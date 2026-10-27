import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

const downloadConversation = async (messages) => {
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
    
    // Text sanitizing function to handle problematic characters
    const sanitizeText = (text) => {
      if (!text || typeof text !== 'string') return '';
      
      // Remove emojis and non-standard characters
      return text
        .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '')
        // Replace tabs with spaces
        .replace(/\t/g, '    ')
        // Replace carriage returns with nothing
        .replace(/\r/g, '');
    };
    
    // Function to parse markdown-like formatting
    const parseFormatting = (text) => {
      const segments = [];
      let currentIndex = 0;
      
      // Match bold text: **text**
      const boldRegex = /\*\*(.*?)\*\*/g;
      let boldMatch;
      
      while ((boldMatch = boldRegex.exec(text)) !== null) {
        // Add normal text before the bold text
        if (boldMatch.index > currentIndex) {
          segments.push({
            text: text.substring(currentIndex, boldMatch.index),
            isBold: false
          });
        }
        
        // Add the bold text without ** markers
        segments.push({
          text: boldMatch[1], // The text between ** markers
          isBold: true
        });
        
        currentIndex = boldMatch.index + boldMatch[0].length;
      }
      
      // Add any remaining text
      if (currentIndex < text.length) {
        segments.push({
          text: text.substring(currentIndex),
          isBold: false
        });
      }
      
      return segments.length > 0 ? segments : [{ text, isBold: false }];
    };
    
    // Text adding function with markdown support
    const addText = (text, options = {}) => {
      const {
        fontType = font,
        color = rgb(0, 0, 0),
        indent = 0,
        maxWidth = width - 80,
      } = options;
      
      // Sanitize and split by newlines
      const sanitizedText = sanitizeText(text);
      const paragraphs = sanitizedText.split('\n');
      
      for (const paragraph of paragraphs) {
        if (paragraph.trim() === '') {
          // Just add some space for empty paragraphs
          y -= lineHeight;
          continue;
        }
        
        const formattedSegments = parseFormatting(paragraph);
        let currentLine = '';
        let lineSegments = [];
        let x = 40 + indent;
        
        // Helper function to draw the current line
        const drawCurrentLine = () => {
          if (y < 40) {
            page = pdfDoc.addPage([595.28, 841.89]);
            y = height - 40;
            x = 40 + indent;
          }
          
          // Draw each segment with its appropriate formatting
          for (const segment of lineSegments) {
            const segmentFont = segment.isBold ? fontBold : fontType;
            const textWidth = segmentFont.widthOfTextAtSize(segment.text, fontSize);
            
            page.drawText(segment.text, {
              x,
              y,
              size: fontSize,
              font: segmentFont,
              color,
            });
            
            x += textWidth;
          }
          
          y -= lineHeight;
          x = 40 + indent;
          lineSegments = [];
          currentLine = '';
        };
        
        // Process each formatted segment
        for (const segment of formattedSegments) {
          const words = segment.text.split(' ');
          
          for (let i = 0; i < words.length; i++) {
            const word = words[i] + (i < words.length - 1 ? ' ' : '');
            const testLineWidth = fontType.widthOfTextAtSize(currentLine + word, fontSize);
            
            if (testLineWidth > maxWidth && currentLine !== '') {
              // Complete the current line and draw it
              drawCurrentLine();
              
              // Start a new line with this word
              currentLine = word;
              lineSegments = [{ 
                text: word, 
                isBold: segment.isBold 
              }];
            } else {
              // Add word to current line
              currentLine += word;
              
              // If the last segment had the same formatting, just append to it
              if (lineSegments.length > 0 && 
                  lineSegments[lineSegments.length - 1].isBold === segment.isBold) {
                lineSegments[lineSegments.length - 1].text += word;
              } else {
                lineSegments.push({
                  text: word,
                  isBold: segment.isBold
                });
              }
            }
          }
        }
        
        // Draw any remaining text
        if (currentLine !== '') {
          drawCurrentLine();
        }
      }
      
      // Add extra space after paragraphs
      y -= lineHeight / 2;
    };
    
    // Add title
    page.drawText("Chat Transcript", {
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
    for (let index = 0; index < messages.length; index++) {
      try {
        const msg = messages[index];
        
        if (!msg || typeof msg !== 'object') {
          console.warn(`Invalid message at index ${index}:`, msg);
          continue;
        }
        
        const isUser = msg.role === "user";
        const prefix = isUser ? "You: " : "Assistant:";
        const roleColor = isUser ? rgb(0.1, 0.5, 0.2) : rgb(0.2, 0.2, 0.6);
        
        // Add some extra space between messages
        if (index > 0) y -= lineHeight;
        
        if (y < 40) {
          page = pdfDoc.addPage([595.28, 841.89]);
          y = height - 40;
        }
        
        page.drawText(prefix, {
          x: 40,
          y,
          size: fontSize,
          font: fontBold,
          color: roleColor,
        });
        y -= lineHeight;
        
        if (msg.content) {
          addText(msg.content, {
            indent: 10,
          });
        } else {
          addText("(No content)", { indent: 10 });
        }
        
        if (msg.model || msg.provider) {
          if (y < 40) {
            page = pdfDoc.addPage([595.28, 841.89]);
            y = height - 40;
          }
          
          page.drawText(`Model: ${msg.model || "N/A"} | Provider: ${msg.provider || "N/A"}`, {
            x: 40 + 10,
            y,
            size: fontSize - 2,
            font: font,
            color: rgb(0.5, 0.5, 0.5),
          });
          y -= lineHeight;
        }
      } catch (err) {
        console.error(`Error processing message at index ${index}:`, err);
      }
    }
    
    // Save the PDF
    const pdfBytes = await pdfDoc.save();
    
    // Create a Blob and trigger download
    const blob = new Blob([pdfBytes], { type: "application/pdf" });
    
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