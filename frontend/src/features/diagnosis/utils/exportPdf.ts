import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export interface ShareReportOptions {
  title: string;
  text: string;
  url?: string;
  pdfBlob?: Blob;
  fileName?: string;
}

/**
 * Converts a designated HTML element into a high-resolution A4 PDF document.
 */
export async function generatePdfFromElement(
  element: HTMLElement,
  fileName: string = "Sunflower_Diagnostic_Report.pdf",
): Promise<Blob> {
  // Capture high-DPI canvas
  const canvas = await html2canvas(element, {
    scale: 2, // 2x resolution for crisp text & charts
    useCORS: true,
    logging: false,
    backgroundColor: "#ffffff",
  });

  const imgData = canvas.toDataURL("image/jpeg", 0.95);

  // A4 dimensions in millimeters
  const pdfWidth = 210;
  const pdfHeight = 297;
  const margin = 10;
  const usableWidth = pdfWidth - margin * 2;

  const imgWidth = usableWidth;
  const imgHeight = (canvas.height * usableWidth) / canvas.width;

  const pdf = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
    compress: true,
  });

  // Handle multi-page if content overflows A4
  let heightLeft = imgHeight;
  let position = margin;

  pdf.addImage(imgData, "JPEG", margin, position, imgWidth, imgHeight);
  heightLeft -= pdfHeight - margin * 2;

  while (heightLeft > 0) {
    position = heightLeft - imgHeight + margin;
    pdf.addPage();
    pdf.addImage(imgData, "JPEG", margin, position, imgWidth, imgHeight);
    heightLeft -= pdfHeight - margin * 2;
  }

  // Trigger browser download
  pdf.save(fileName);

  // Return blob for Web Share API
  return pdf.output("blob");
}

/**
 * Shares the report using the Web Share API with fallback to Clipboard copy.
 */
export async function shareDiagnosticReport(
  options: ShareReportOptions,
): Promise<{ success: boolean; method: "native" | "clipboard" | "file" }> {
  const { title, text, url = window.location.href, pdfBlob, fileName = "Sunflower_Diagnosis.pdf" } = options;

  // 1. Try file sharing via Web Share API
  if (pdfBlob && typeof navigator !== "undefined" && "canShare" in navigator) {
    const file = new File([pdfBlob], fileName, { type: "application/pdf" });
    if (navigator.canShare({ files: [file] })) {
      try {
        await navigator.share({
          files: [file],
          title,
          text,
        });
        return { success: true, method: "file" };
      } catch (err: unknown) {
        // Ignore AbortError (user dismissed native share sheet)
        if (err instanceof Error && err.name === "AbortError") {
          return { success: false, method: "file" };
        }
      }
    }
  }

  // 2. Try text/link sharing via Web Share API
  if (typeof navigator !== "undefined" && "share" in navigator) {
    try {
      await navigator.share({
        title,
        text,
        url,
      });
      return { success: true, method: "native" };
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        return { success: false, method: "native" };
      }
    }
  }

  // 3. Fallback: Copy summary and URL to clipboard
  try {
    const shareContent = `${title}\n\n${text}\n\n${url}`;
    await navigator.clipboard.writeText(shareContent);
    return { success: true, method: "clipboard" };
  } catch {
    return { success: false, method: "clipboard" };
  }
}

